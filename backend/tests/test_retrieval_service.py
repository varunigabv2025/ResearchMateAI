"""
Tests for retrieval service.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from app.services.retrieval_service import RetrievalService
from app.models import Paper, PaperChunk, Embedding


class TestRetrievalService:
    """Tests for retrieval service."""
    
    @pytest.fixture
    def service(self):
        """Create retrieval service instance."""
        return RetrievalService()
    
    @pytest.fixture
    def mock_paper(self):
        """Create mock paper."""
        paper = Mock(spec=Paper)
        paper.id = uuid.uuid4()
        paper.processed = True
        paper.processing_error = None
        return paper
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_paper_not_found(self, service):
        """Test retrieval with non-existent paper."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        paper_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="Paper with id .* not found"):
            await service.retrieve_relevant_chunks(
                mock_db, paper_id, "test question"
            )
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_paper_not_processed(self, service, mock_paper):
        """Test retrieval with unprocessed paper."""
        mock_paper.processed = False
        mock_paper.processing_error = "Embedding failed"
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        with pytest.raises(ValueError, match="Paper has not been fully processed"):
            await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question"
            )
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_success(self, service, mock_paper):
        """Test successful chunk retrieval."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Mock embedding service
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding', 
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            # Mock the search method
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Test chunk 1',
                    'page_number': 1,
                    'section': 'Introduction',
                    'chunk_index': 0,
                    'similarity': 0.9
                },
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Test chunk 2',
                    'page_number': 2,
                    'section': 'Methods',
                    'chunk_index': 1,
                    'similarity': 0.8
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question", top_k=2
                )
                
                assert len(results) == 2
                assert results[0]['similarity'] == 0.9
                assert results[0]['page_number'] == 1
                assert results[0]['section'] == 'Introduction'
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_filters_by_threshold(self, service, mock_paper):
        """Test that chunks below similarity threshold are filtered."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Relevant chunk',
                    'page_number': 1,
                    'section': 'Introduction',
                    'chunk_index': 0,
                    'similarity': 0.9  # Above threshold
                },
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Irrelevant chunk',
                    'page_number': 2,
                    'section': 'Methods',
                    'chunk_index': 1,
                    'similarity': 0.5  # Below threshold
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question",
                    top_k=5, similarity_threshold=0.7
                )
                
                # Only the chunk above threshold should be returned
                assert len(results) == 1
                assert results[0]['similarity'] == 0.9
    
    def test_search_with_fallback(self, service):
        """Test fallback search method."""
        import numpy as np
        
        paper_id = uuid.uuid4()
        chunk_id1 = uuid.uuid4()
        chunk_id2 = uuid.uuid4()
        
        # Mock database results
        mock_result1 = Mock()
        mock_result1.chunk_id = chunk_id1
        mock_result1.text = "Test text 1"
        mock_result1.page_number = 1
        mock_result1.section = "Introduction"
        mock_result1.chunk_index = 0
        mock_result1.embedding = [0.9, 0.1, 0.0] + [0.0] * 1021  # Similar to query
        
        mock_result2 = Mock()
        mock_result2.chunk_id = chunk_id2
        mock_result2.text = "Test text 2"
        mock_result2.page_number = 2
        mock_result2.section = "Methods"
        mock_result2.chunk_index = 1
        mock_result2.embedding = [0.1, 0.9, 0.0] + [0.0] * 1021  # Less similar
        
        mock_db = Mock()
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            mock_result1, mock_result2
        ]
        
        query_embedding = [1.0, 0.0, 0.0] + [0.0] * 1021
        
        results = service._search_with_fallback(mock_db, paper_id, query_embedding, top_k=2)
        
        assert len(results) == 2
        # First result should be more similar
        assert results[0]['chunk_id'] == chunk_id1
        assert results[0]['similarity'] > results[1]['similarity']
