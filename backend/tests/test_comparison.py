"""
Tests for paper comparison feature.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from fastapi import status


class TestComparisonValidation:
    """Tests for comparison request validation."""
    
    def test_compare_papers_too_few(self, client):
        """Test comparison with only 1 paper."""
        response = client.post(
            "/api/papers/compare",
            json={"paper_ids": [str(uuid.uuid4())]}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_compare_papers_too_many(self, client):
        """Test comparison with more than 5 papers."""
        paper_ids = [str(uuid.uuid4()) for _ in range(6)]
        response = client.post(
            "/api/papers/compare",
            json={"paper_ids": paper_ids}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_compare_papers_duplicates(self, client):
        """Test comparison with duplicate paper IDs."""
        paper_id = str(uuid.uuid4())
        response = client.post(
            "/api/papers/compare",
            json={"paper_ids": [paper_id, paper_id]}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_compare_papers_invalid_uuid(self, client):
        """Test comparison with invalid UUID format."""
        response = client.post(
            "/api/papers/compare",
            json={"paper_ids": ["not-a-uuid", "also-not-uuid"]}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_compare_papers_nonexistent(self, client, db_session):
        """Test comparison with non-existent papers."""
        paper_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        response = client.post(
            "/api/papers/compare",
            json={"paper_ids": paper_ids}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not found" in response.json()["detail"].lower()
    
    def test_compare_papers_valid_count_2(self, client):
        """Test that 2 papers is valid."""
        # This will fail due to non-existent papers, but validates count
        paper_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        response = client.post(
            "/api/papers/compare",
            json={"paper_ids": paper_ids}
        )
        
        # Should be 400 (not found) not 422 (validation)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_compare_papers_valid_count_5(self, client):
        """Test that 5 papers is valid."""
        paper_ids = [str(uuid.uuid4()) for _ in range(5)]
        response = client.post(
            "/api/papers/compare",
            json={"paper_ids": paper_ids}
        )
        
        # Should be 400 (not found) not 422 (validation)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestContentSelector:
    """Tests for content selection service."""
    
    def test_content_selector_paper_not_found(self, db_session):
        """Test content selection with non-existent paper."""
        from app.services.content_selector import ContentSelector
        
        selector = ContentSelector()
        paper_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="not found"):
            selector.get_paper_content_for_comparison(db_session, paper_id)
    
    def test_content_selector_no_chunks(self, db_session):
        """Test content selection with paper that has no chunks."""
        from app.models import Paper
        from app.services.content_selector import ContentSelector
        
        # Create paper without chunks
        paper = Paper(
            id=uuid.uuid4(),
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=True
        )
        db_session.add(paper)
        db_session.commit()
        
        selector = ContentSelector()
        
        with pytest.raises(ValueError, match="no extracted content"):
            selector.get_paper_content_for_comparison(db_session, paper.id)
    
    def test_content_selector_prioritizes_sections(self, db_session):
        """Test that content selector prioritizes relevant sections."""
        from app.models import Paper, PaperChunk
        from app.services.content_selector import ContentSelector
        
        paper_id = uuid.uuid4()
        paper = Paper(
            id=paper_id,
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=True
        )
        db_session.add(paper)
        db_session.flush()
        
        # Add chunks with different sections
        chunks_data = [
            ("References", 10, "Citation 1, Citation 2"),
            ("Abstract", 1, "This is the abstract"),
            ("Conclusion", 9, "This is the conclusion"),
            ("Methodology", 5, "This is the methodology"),
        ]
        
        for i, (section, page, text) in enumerate(chunks_data):
            chunk = PaperChunk(
                paper_id=paper_id,
                page_number=page,
                section=section,
                chunk_index=i,
                text=text,
                char_count=len(text)
            )
            db_session.add(chunk)
        
        db_session.commit()
        
        selector = ContentSelector()
        content, sources = selector.get_paper_content_for_comparison(db_session, paper_id)
        
        # Abstract and Methodology should come before References
        assert "Abstract" in content
        assert "Methodology" in content
        # Abstract should appear before References in content
        assert content.index("Abstract") < content.index("References")


class TestComparisonService:
    """Tests for comparison service."""
    
    @pytest.mark.asyncio
    async def test_extraction_single_paper(self, db_session):
        """Test extraction for a single paper with mocked LLM."""
        from app.models import Paper, PaperChunk
        from app.services.comparison_service import ComparisonService
        
        paper_id = uuid.uuid4()
        paper = Paper(
            id=paper_id,
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=True
        )
        db_session.add(paper)
        db_session.flush()
        
        # Add chunk
        chunk = PaperChunk(
            paper_id=paper_id,
            page_number=1,
            section="Abstract",
            chunk_index=0,
            text="We propose a novel method using transformers.",
            char_count=50
        )
        db_session.add(chunk)
        db_session.commit()
        
        # Mock LLM response
        mock_response = """{
            "method": "Transformer-based model",
            "dataset": "Not specified in the paper",
            "metric_result": "Not specified in the paper",
            "limitation": "Not specified in the paper"
        }"""
        
        service = ComparisonService()
        
        with patch.object(service.llm_service, 'generate_chat_completion',
                         new_callable=AsyncMock, return_value=mock_response):
            
            result = await service._extract_paper_info(db_session, paper_id)
            
            assert result.paper_id == str(paper_id)
            assert result.filename == "test.pdf"
            assert result.method == "Transformer-based model"
            assert "Not specified" in result.dataset
    
    @pytest.mark.asyncio
    async def test_extraction_parses_markdown_json(self, db_session):
        """Test that extraction handles markdown-wrapped JSON."""
        from app.models import Paper, PaperChunk
        from app.services.comparison_service import ComparisonService
        
        paper_id = uuid.uuid4()
        paper = Paper(
            id=paper_id,
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=True
        )
        db_session.add(paper)
        db_session.flush()
        
        chunk = PaperChunk(
            paper_id=paper_id,
            page_number=1,
            section="Abstract",
            chunk_index=0,
            text="Test content",
            char_count=12
        )
        db_session.add(chunk)
        db_session.commit()
        
        # Mock LLM response with markdown wrapper
        mock_response = """```json
{
    "method": "BERT",
    "dataset": "Wikipedia",
    "metric_result": "Accuracy: 95%",
    "limitation": "Computationally expensive"
}
```"""
        
        service = ComparisonService()
        
        with patch.object(service.llm_service, 'generate_chat_completion',
                         new_callable=AsyncMock, return_value=mock_response):
            
            result = await service._extract_paper_info(db_session, paper_id)
            
            assert result.method == "BERT"
            assert result.dataset == "Wikipedia"
    
    @pytest.mark.asyncio
    async def test_compare_multiple_papers(self, db_session):
        """Test comparing multiple papers."""
        from app.models import Paper, PaperChunk
        from app.services.comparison_service import ComparisonService
        
        # Create two papers
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
            db_session.flush()
            
            chunk = PaperChunk(
                paper_id=paper_id,
                page_number=1,
                section="Abstract",
                chunk_index=0,
                text=f"Paper {i} content",
                char_count=20
            )
            db_session.add(chunk)
            papers.append(paper)
        
        db_session.commit()
        
        # Mock LLM to return different responses
        async def mock_llm_response(messages, **kwargs):
            # Return different response based on paper filename
            if "paper0" in messages[1]["content"]:
                return """{
                    "method": "Method A",
                    "dataset": "Dataset A",
                    "metric_result": "Result A",
                    "limitation": "Limitation A"
                }"""
            else:
                return """{
                    "method": "Method B",
                    "dataset": "Dataset B",
                    "metric_result": "Result B",
                    "limitation": "Limitation B"
                }"""
        
        service = ComparisonService()
        
        with patch.object(service.llm_service, 'generate_chat_completion',
                         side_effect=mock_llm_response):
            
            results = await service.compare_papers(
                db_session, [papers[0].id, papers[1].id]
            )
            
            assert len(results) == 2
            assert results[0].method == "Method A"
            assert results[1].method == "Method B"
    
    def test_validate_papers_exist(self, db_session):
        """Test paper existence validation."""
        from app.models import Paper, PaperChunk
        from app.services.comparison_service import ComparisonService
        
        paper_id = uuid.uuid4()
        paper = Paper(
            id=paper_id,
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=True
        )
        db_session.add(paper)
        db_session.flush()
        
        # Add a chunk so paper has content
        chunk = PaperChunk(
            paper_id=paper_id,
            page_number=1,
            section="Abstract",
            chunk_index=0,
            text="Test content",
            char_count=12
        )
        db_session.add(chunk)
        db_session.commit()
        
        service = ComparisonService()
        
        # Valid paper
        is_valid, msg = service.validate_papers_exist(db_session, [paper_id])
        assert is_valid
        assert msg == ""
        
        # Non-existent paper
        fake_id = uuid.uuid4()
        is_valid, msg = service.validate_papers_exist(db_session, [fake_id])
        assert not is_valid
        assert "not found" in msg


class TestComparisonEndpoint:
    """Tests for comparison API endpoint."""
    
    @pytest.mark.asyncio
    async def test_compare_endpoint_success(self, client, db_session):
        """Test successful comparison with mocked extraction."""
        from app.models import Paper, PaperChunk
        
        # Create two papers
        paper_ids = []
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
            db_session.flush()
            
            chunk = PaperChunk(
                paper_id=paper_id,
                page_number=1,
                section="Abstract",
                chunk_index=0,
                text=f"Content {i}",
                char_count=10
            )
            db_session.add(chunk)
            paper_ids.append(str(paper_id))
        
        db_session.commit()
        
        # Mock comparison service
        from app.schemas.comparison import PaperComparisonResult
        
        mock_results = [
            PaperComparisonResult(
                paper_id=paper_ids[0],
                filename="paper0.pdf",
                method="Method 0",
                dataset="Dataset 0",
                metric_result="Result 0",
                limitation="Limitation 0"
            ),
            PaperComparisonResult(
                paper_id=paper_ids[1],
                filename="paper1.pdf",
                method="Method 1",
                dataset="Dataset 1",
                metric_result="Result 1",
                limitation="Limitation 1"
            )
        ]
        
        with patch('app.services.comparison_service.ComparisonService.compare_papers',
                  new_callable=AsyncMock, return_value=mock_results):
            
            response = client.post(
                "/api/papers/compare",
                json={"paper_ids": paper_ids}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "papers" in data
        assert "total_papers" in data
        assert data["total_papers"] == 2
        assert len(data["papers"]) == 2
        assert data["papers"][0]["method"] == "Method 0"
        assert data["papers"][1]["method"] == "Method 1"
