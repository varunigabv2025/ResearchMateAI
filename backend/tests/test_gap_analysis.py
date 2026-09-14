"""
Tests for research gap analysis feature.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models import Paper, PaperChunk


class TestGapAnalysisValidation:
    """Test request validation for gap analysis endpoint."""
    
    def test_analyze_gaps_too_few_papers(self, client: TestClient):
        """Test that 0 or 1 paper is rejected."""
        # 0 papers
        response = client.post(
            "/api/papers/gaps",
            json={"paper_ids": []}
        )
        assert response.status_code == 422
        
        # 1 paper
        response = client.post(
            "/api/papers/gaps",
            json={"paper_ids": [str(uuid.uuid4())]}
        )
        assert response.status_code == 422
    
    def test_analyze_gaps_too_many_papers(self, client: TestClient):
        """Test that more than 5 papers is rejected."""
        paper_ids = [str(uuid.uuid4()) for _ in range(6)]
        response = client.post(
            "/api/papers/gaps",
            json={"paper_ids": paper_ids}
        )
        assert response.status_code == 422
    
    def test_analyze_gaps_duplicates(self, client: TestClient):
        """Test that duplicate paper IDs are rejected."""
        paper_id = str(uuid.uuid4())
        response = client.post(
            "/api/papers/gaps",
            json={"paper_ids": [paper_id, paper_id]}
        )
        assert response.status_code == 422
    
    def test_analyze_gaps_invalid_uuid(self, client: TestClient):
        """Test that invalid UUID format is rejected."""
        response = client.post(
            "/api/papers/gaps",
            json={"paper_ids": ["not-a-uuid", "also-not-uuid"]}
        )
        assert response.status_code == 422
    
    def test_analyze_gaps_nonexistent_papers(self, client: TestClient, db_session):
        """Test that non-existent papers are rejected."""
        fake_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        response = client.post(
            "/api/papers/gaps",
            json={"paper_ids": fake_ids}
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_analyze_gaps_valid_count_2(self, client: TestClient):
        """Test that 2 papers is valid."""
        from app.schemas.gap_analysis import AnalyzeGapsRequest
        
        request = AnalyzeGapsRequest(
            paper_ids=[str(uuid.uuid4()), str(uuid.uuid4())]
        )
        assert len(request.paper_ids) == 2
    
    def test_analyze_gaps_valid_count_5(self, client: TestClient):
        """Test that 5 papers is valid."""
        from app.schemas.gap_analysis import AnalyzeGapsRequest
        
        request = AnalyzeGapsRequest(
            paper_ids=[str(uuid.uuid4()) for _ in range(5)]
        )
        assert len(request.paper_ids) == 5


class TestGapAnalysisPrompt:
    """Test gap analysis prompt building."""
    
    def test_prompt_builds_with_comparison_data(self):
        """Test that prompt correctly formats comparison data."""
        from app.services.prompts import GapAnalysisPrompt
        
        comparison_data = [
            {
                "paper_id": str(uuid.uuid4()),
                "filename": "paper1.pdf",
                "method": "Transformer architecture",
                "dataset": "WMT 2014",
                "metric_result": "BLEU 28.4",
                "limitation": "High computational cost"
            },
            {
                "paper_id": str(uuid.uuid4()),
                "filename": "paper2.pdf",
                "method": "RNN with attention",
                "dataset": "WMT 2014",
                "metric_result": "BLEU 24.1",
                "limitation": "Slow training"
            }
        ]
        
        prompt = GapAnalysisPrompt()
        messages = prompt.build_analysis_messages(comparison_data)
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        
        # Check that comparison data is in prompt
        user_content = messages[1]["content"]
        assert "paper1.pdf" in user_content
        assert "paper2.pdf" in user_content
        assert "Transformer architecture" in user_content
        assert "WMT 2014" in user_content
    
    def test_prompt_emphasizes_evidence_only(self):
        """Test that system prompt emphasizes using only provided data."""
        from app.services.prompts import GapAnalysisPrompt
        
        system_prompt = GapAnalysisPrompt.SYSTEM_PROMPT
        
        # Check for key instructions
        assert "ONLY" in system_prompt or "only" in system_prompt
        assert "do not" in system_prompt.lower() or "don't" in system_prompt.lower()
        assert "outside knowledge" in system_prompt.lower() or "general knowledge" in system_prompt.lower()
    
    def test_validate_gap_format(self):
        """Test gap format validation."""
        from app.services.prompts import GapAnalysisPrompt
        
        prompt = GapAnalysisPrompt()
        
        # Valid gap
        valid_gap = {
            "title": "Dataset diversity gap",
            "description": "Papers use similar datasets",
            "basis": "All three papers evaluate on WMT 2014"
        }
        assert prompt.validate_gap_format(valid_gap) is True
        
        # Missing field
        invalid_gap = {
            "title": "Some gap",
            "description": "Description here"
            # missing basis
        }
        assert prompt.validate_gap_format(invalid_gap) is False
        
        # Empty field
        empty_gap = {
            "title": "",
            "description": "Description",
            "basis": "Basis"
        }
        assert prompt.validate_gap_format(empty_gap) is False


class TestGapAnalysisService:
    """Test gap analysis service logic."""
    
    @pytest.mark.asyncio
    async def test_analyze_gaps_single_llm_call(self, db_session):
        """Test that exactly ONE LLM call is made for gap analysis."""
        from app.services.gap_analysis_service import GapAnalysisService
        from app.schemas.comparison import PaperComparisonResult
        
        # Create mock comparison results (bypass actual comparison service)
        mock_comparison_results = [
            PaperComparisonResult(
                paper_id=str(uuid.uuid4()),
                filename="paper0.pdf",
                method="Test method A",
                dataset="Test dataset A",
                metric_result="Test result A",
                limitation="Test limitation A"
            ),
            PaperComparisonResult(
                paper_id=str(uuid.uuid4()),
                filename="paper1.pdf",
                method="Test method B",
                dataset="Test dataset B",
                metric_result="Test result B",
                limitation="Test limitation B"
            )
        ]
        
        # Mock gap analysis response
        mock_gap_response = """[
            {
                "title": "Dataset diversity gap",
                "description": "Both papers use similar datasets",
                "basis": "Papers evaluate on the same benchmark"
            }
        ]"""
        
        service = GapAnalysisService()
        
        # Track gap analysis LLM calls only
        gap_call_count = 0
        
        async def mock_comparison_service(db, paper_ids):
            return mock_comparison_results
        
        async def mock_gap_llm(messages, **kwargs):
            nonlocal gap_call_count
            gap_call_count += 1
            return mock_gap_response
        
        # Mock comparison service and gap analysis LLM
        with patch.object(service.comparison_service, 'compare_papers',
                         side_effect=mock_comparison_service):
            with patch.object(service.llm_service, 'generate_chat_completion',
                             side_effect=mock_gap_llm):
                paper_ids = [uuid.uuid4(), uuid.uuid4()]
                gaps = await service.analyze_gaps(db_session, paper_ids)
                
                # Verify exactly ONE gap analysis LLM call
                assert gap_call_count == 1
                assert len(gaps) == 1
                assert gaps[0].title == "Dataset diversity gap"
    
    @pytest.mark.asyncio
    async def test_analyze_gaps_parses_markdown_json(self, db_session):
        """Test that markdown-wrapped JSON is handled."""
        from app.services.gap_analysis_service import GapAnalysisService
        from app.schemas.comparison import PaperComparisonResult
        
        # Mock comparison results
        mock_comparison_results = [
            PaperComparisonResult(
                paper_id=str(uuid.uuid4()),
                filename="paper0.pdf",
                method="Method A",
                dataset="Dataset A",
                metric_result="Result A",
                limitation="Limitation A"
            ),
            PaperComparisonResult(
                paper_id=str(uuid.uuid4()),
                filename="paper1.pdf",
                method="Method B",
                dataset="Dataset B",
                metric_result="Result B",
                limitation="Limitation B"
            )
        ]
        
        # Mock response with markdown code blocks
        mock_gap_response = """```json
[
    {
        "title": "Methodological gap",
        "description": "Different approaches not compared directly",
        "basis": "Papers use different methods without cross-evaluation"
    }
]
```"""
        
        service = GapAnalysisService()
        
        async def mock_comparison_service(db, paper_ids):
            return mock_comparison_results
        
        async def mock_gap_llm(messages, **kwargs):
            return mock_gap_response
        
        with patch.object(service.comparison_service, 'compare_papers',
                         side_effect=mock_comparison_service):
            with patch.object(service.llm_service, 'generate_chat_completion',
                             side_effect=mock_gap_llm):
                paper_ids = [uuid.uuid4(), uuid.uuid4()]
                gaps = await service.analyze_gaps(db_session, paper_ids)
                
                assert len(gaps) == 1
                assert gaps[0].title == "Methodological gap"
    
    @pytest.mark.asyncio
    async def test_analyze_gaps_empty_response(self, db_session):
        """Test that empty gap list is handled."""
        from app.services.gap_analysis_service import GapAnalysisService
        from app.schemas.comparison import PaperComparisonResult
        
        # Mock comparison results
        mock_comparison_results = [
            PaperComparisonResult(
                paper_id=str(uuid.uuid4()),
                filename="paper0.pdf",
                method="Method A",
                dataset="Dataset A",
                metric_result="Result A",
                limitation="Limitation A"
            ),
            PaperComparisonResult(
                paper_id=str(uuid.uuid4()),
                filename="paper1.pdf",
                method="Method B",
                dataset="Dataset B",
                metric_result="Result B",
                limitation="Limitation B"
            )
        ]
        
        # Mock empty response
        mock_gap_response = "[]"
        
        service = GapAnalysisService()
        
        async def mock_comparison_service(db, paper_ids):
            return mock_comparison_results
        
        async def mock_gap_llm(messages, **kwargs):
            return mock_gap_response
        
        with patch.object(service.comparison_service, 'compare_papers',
                         side_effect=mock_comparison_service):
            with patch.object(service.llm_service, 'generate_chat_completion',
                             side_effect=mock_gap_llm):
                paper_ids = [uuid.uuid4(), uuid.uuid4()]
                gaps = await service.analyze_gaps(db_session, paper_ids)
                
                assert len(gaps) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_gaps_malformed_json(self, db_session):
        """Test that malformed JSON is handled."""
        from app.services.gap_analysis_service import GapAnalysisService
        from app.models import Paper, PaperChunk
        
        # Create test papers
        paper_id = uuid.uuid4()
        paper = Paper(
            id=paper_id,
            filename="paper.pdf",
            original_filename="paper.pdf",
            file_path="/tmp/paper.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=True
        )
        db_session.add(paper)
        
        chunk = PaperChunk(
            paper_id=paper_id,
            page_number=1,
            section="Abstract",
            chunk_index=0,
            text="Content",
            char_count=7
        )
        db_session.add(chunk)
        
        paper_id2 = uuid.uuid4()
        paper2 = Paper(
            id=paper_id2,
            filename="paper2.pdf",
            original_filename="paper2.pdf",
            file_path="/tmp/paper2.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=True
        )
        db_session.add(paper2)
        
        chunk2 = PaperChunk(
            paper_id=paper_id2,
            page_number=1,
            section="Abstract",
            chunk_index=0,
            text="Content",
            char_count=7
        )
        db_session.add(chunk2)
        db_session.commit()
        
        # Mock malformed JSON
        mock_response = "This is not valid JSON"
        
        service = GapAnalysisService()
        
        async def mock_llm_call(messages, **kwargs):
            return mock_response
        
        with patch.object(service.llm_service, 'generate_chat_completion',
                         side_effect=mock_llm_call):
            with pytest.raises(Exception, match="Failed to parse JSON"):
                await service.analyze_gaps(db_session, [paper_id, paper_id2])


class TestGapAnalysisEndpoint:
    """Test gap analysis API endpoint."""
    
    @pytest.mark.asyncio
    async def test_gaps_endpoint_success(self, client: TestClient, db_session):
        """Test successful gap analysis with mocked services."""
        from app.models import Paper, PaperChunk
        from app.schemas.comparison import PaperComparisonResult
        
        # Create test papers with chunks
        papers = []
        for i in range(2):
            paper_id = uuid.uuid4()
            paper = Paper(
                id=paper_id,
                filename=f"paper{i}.pdf",
                original_filename=f"paper{i}.pdf",
                file_path=f"/tmp/paper{i}.pdf",
                file_size_bytes=1000,
                page_count=10,
                processed=True
            )
            db_session.add(paper)
            papers.append(paper)
            
            chunk = PaperChunk(
                paper_id=paper_id,
                page_number=1,
                section="Abstract",
                chunk_index=0,
                text=f"Test content for paper {i}",
                char_count=25
            )
            db_session.add(chunk)
        
        db_session.commit()
        
        # Mock comparison results
        mock_comparison_results = [
            PaperComparisonResult(
                paper_id=str(papers[0].id),
                filename="paper0.pdf",
                method="Test method A",
                dataset="Test dataset A",
                metric_result="Test result A",
                limitation="Test limitation A"
            ),
            PaperComparisonResult(
                paper_id=str(papers[1].id),
                filename="paper1.pdf",
                method="Test method B",
                dataset="Test dataset B",
                metric_result="Test result B",
                limitation="Test limitation B"
            )
        ]
        
        # Mock gap response
        mock_gap_response = """[
            {
                "title": "Dataset diversity gap",
                "description": "The compared papers evaluate on similar datasets",
                "basis": "Both papers use the same benchmark dataset"
            }
        ]"""
        
        from app.services import comparison_service, gap_analysis_service
        
        async def mock_comparison_service_call(db, paper_ids):
            return mock_comparison_results
        
        async def mock_gap_llm(messages, **kwargs):
            return mock_gap_response
        
        # Patch comparison service and gap LLM
        with patch.object(comparison_service, 'compare_papers',
                         side_effect=mock_comparison_service_call):
            with patch.object(gap_analysis_service.llm_service, 'generate_chat_completion',
                             side_effect=mock_gap_llm):
                
                response = client.post(
                    "/api/papers/gaps",
                    json={"paper_ids": [str(papers[0].id), str(papers[1].id)]}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify structure
                assert "paper_ids" in data
                assert "gaps" in data
                assert "disclaimer" in data
                
                # Verify disclaimer is always present
                assert data["disclaimer"] == "AI-suggested — verify against the literature yourself."
                
                # Verify gaps
                assert len(data["gaps"]) == 1
                gap = data["gaps"][0]
                assert gap["title"] == "Dataset diversity gap"
                assert "title" in gap
                assert "description" in gap
                assert "basis" in gap
    
    def test_gaps_endpoint_includes_disclaimer(self):
        """Test that disclaimer is always included in response schema."""
        from app.schemas.gap_analysis import AnalyzeGapsResponse, ResearchGap
        
        response = AnalyzeGapsResponse(
            paper_ids=["id1", "id2"],
            gaps=[]
        )
        
        assert response.disclaimer == "AI-suggested — verify against the literature yourself."
