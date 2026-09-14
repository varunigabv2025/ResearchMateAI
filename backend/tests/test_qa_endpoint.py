"""
Tests for Q&A endpoint.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from fastapi import status


class TestQAEndpoint:
    """Tests for Q&A endpoint."""
    
    @pytest.fixture
    def paper_id(self):
        """Generate a paper ID."""
        return str(uuid.uuid4())
    
    def test_ask_question_paper_not_found(self, client, paper_id):
        """Test asking question about non-existent paper."""
        response = client.post(
            f"/api/papers/{paper_id}/ask",
            json={"question": "What is this about?"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_ask_question_empty_question(self, client, paper_id):
        """Test asking empty question."""
        response = client.post(
            f"/api/papers/{paper_id}/ask",
            json={"question": ""}
        )
        
        # Should fail validation
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_ask_question_paper_not_processed(self, client, db_session, paper_id):
        """Test asking question about unprocessed paper."""
        from app.models import Paper
        
        # Create unprocessed paper
        paper = Paper(
            id=uuid.UUID(paper_id),
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size_bytes=1000,
            page_count=10,
            processed=False,
            processing_error="Embedding failed"
        )
        db_session.add(paper)
        db_session.commit()
        
        response = client.post(
            f"/api/papers/{paper_id}/ask",
            json={"question": "What is this about?"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not been fully processed" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_ask_question_success(self, client, db_session):
        """Test successful Q&A with mocked services."""
        from app.models import Paper, PaperChunk, Embedding
        
        # Create processed paper
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
        
        # Create chunk
        chunk = PaperChunk(
            paper_id=paper_id,
            page_number=1,
            section="Introduction",
            chunk_index=0,
            text="This is a test paper about AI.",
            char_count=30
        )
        db_session.add(chunk)
        db_session.flush()
        
        # Create embedding
        embedding = Embedding(
            chunk_id=chunk.id,
            embedding=[0.1] * 1536,
            model="test-model"
        )
        db_session.add(embedding)
        db_session.commit()
        
        # Mock retrieval and LLM services
        mock_chunks = [
            {
                'chunk_id': str(chunk.id),
                'text': 'This is a test paper about AI.',
                'page_number': 1,
                'section': 'Introduction',
                'chunk_index': 0,
                'similarity': 0.9
            }
        ]
        
        mock_answer = "The paper is about AI and its applications."
        
        with patch('app.services.retrieval_service.RetrievalService.retrieve_relevant_chunks',
                  new_callable=AsyncMock, return_value=mock_chunks):
            with patch('app.services.llm_service.LLMService.generate_chat_completion',
                      new_callable=AsyncMock, return_value=mock_answer):
                
                response = client.post(
                    f"/api/papers/{paper_id}/ask",
                    json={"question": "What is this paper about?"}
                )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "answer" in data
        assert data["answer"] == mock_answer
        assert "sources" in data
        assert len(data["sources"]) > 0
        assert data["sources"][0]["page_number"] == 1
        assert data["sources"][0]["section"] == "Introduction"
        assert data["has_sufficient_context"] is True
        assert data["paper_id"] == str(paper_id)
    
    @pytest.mark.asyncio
    async def test_ask_question_insufficient_context(self, client, db_session):
        """Test Q&A with insufficient context."""
        from app.models import Paper, PaperChunk, Embedding
        
        # Create processed paper
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
        
        # Create chunk and embedding
        chunk = PaperChunk(
            paper_id=paper_id,
            page_number=1,
            section="Introduction",
            chunk_index=0,
            text="Unrelated text.",
            char_count=15
        )
        db_session.add(chunk)
        db_session.flush()
        
        embedding = Embedding(
            chunk_id=chunk.id,
            embedding=[0.1] * 1536,
            model="test-model"
        )
        db_session.add(embedding)
        db_session.commit()
        
        # Mock retrieval returning no relevant chunks (below threshold)
        with patch('app.services.retrieval_service.RetrievalService.retrieve_relevant_chunks',
                  new_callable=AsyncMock, return_value=[]):
            
            response = client.post(
                f"/api/papers/{paper_id}/ask",
                json={"question": "What is quantum physics?"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["has_sufficient_context"] is False
        assert "couldn't find enough relevant information" in data["answer"].lower()
        assert len(data["sources"]) == 0
    
    def test_format_sources_deduplication(self):
        """Test that source formatting deduplicates page/section combinations."""
        from app.api.papers import _format_sources
        
        chunks = [
            {
                'chunk_id': str(uuid.uuid4()),
                'page_number': 1,
                'section': 'Introduction',
                'similarity': 0.9
            },
            {
                'chunk_id': str(uuid.uuid4()),
                'page_number': 1,
                'section': 'Introduction',  # Duplicate page/section
                'similarity': 0.85
            },
            {
                'chunk_id': str(uuid.uuid4()),
                'page_number': 2,
                'section': 'Methods',
                'similarity': 0.8
            }
        ]
        
        sources = _format_sources(chunks)
        
        # Should have only 2 unique citations (page 1 Introduction, page 2 Methods)
        assert len(sources) == 2
        assert sources[0].page_number == 1
        assert sources[0].section == 'Introduction'
        assert sources[1].page_number == 2
        assert sources[1].section == 'Methods'
