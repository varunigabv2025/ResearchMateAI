"""
Tests for lexical (BM25) search service.
"""
import pytest
import uuid
from unittest.mock import Mock
from app.services.lexical_search import LexicalSearchService
from app.models import Paper, PaperChunk


class TestLexicalSearchService:
    """Tests for lexical search service."""
    
    @pytest.fixture
    def service(self):
        """Create lexical search service instance."""
        return LexicalSearchService()
    
    @pytest.fixture
    def mock_paper(self):
        """Create mock paper."""
        paper = Mock(spec=Paper)
        paper.id = uuid.uuid4()
        paper.processed = True
        paper.processing_error = None
        return paper
    
    def test_tokenize_basic(self, service):
        """Test basic tokenization."""
        text = "This is a test document"
        tokens = service._tokenize(text)
        
        assert tokens == ["this", "is", "a", "test", "document"]
    
    def test_tokenize_case_insensitive(self, service):
        """Test tokenization is case-insensitive."""
        text = "Docker MobileNetV2 TFLite"
        tokens = service._tokenize(text)
        
        assert tokens == ["docker", "mobilenetv2", "tflite"]
    
    def test_tokenize_empty(self, service):
        """Test tokenization of empty string."""
        assert service._tokenize("") == []
        assert service._tokenize(None) == []
        assert service._tokenize("   ") == []
    
    def test_tokenize_removes_empty_tokens(self, service):
        """Test that empty tokens are removed."""
        text = "word1  word2    word3"
        tokens = service._tokenize(text)
        
        assert tokens == ["word1", "word2", "word3"]
    
    def test_search_chunks_paper_not_found(self, service):
        """Test search with non-existent paper."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        paper_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="Paper with id .* not found"):
            service.search_chunks(mock_db, paper_id, "test query")
    
    def test_search_chunks_paper_not_processed(self, service, mock_paper):
        """Test search with unprocessed paper."""
        mock_paper.processed = False
        mock_paper.processing_error = "Processing failed"
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        with pytest.raises(ValueError, match="Paper has not been fully processed"):
            service.search_chunks(mock_db, mock_paper.id, "test query")
    
    def test_search_chunks_empty_query(self, service, mock_paper):
        """Test search with empty query."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        results = service.search_chunks(mock_db, mock_paper.id, "")
        assert results == []
        
        results = service.search_chunks(mock_db, mock_paper.id, "   ")
        assert results == []
    
    def test_search_chunks_empty_corpus(self, service, mock_paper):
        """Test search with no chunks."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        results = service.search_chunks(mock_db, mock_paper.id, "test query")
        assert results == []
    
    def test_search_chunks_exact_keyword_match(self, service, mock_paper):
        """Test that exact keywords rank highly."""
        # Create mock chunks
        chunk1 = Mock(spec=PaperChunk)
        chunk1.id = uuid.uuid4()
        chunk1.text = "This paper discusses Docker containerization for edge computing"
        chunk1.page_number = 1
        chunk1.section = "Introduction"
        chunk1.chunk_index = 0
        
        chunk2 = Mock(spec=PaperChunk)
        chunk2.id = uuid.uuid4()
        chunk2.text = "The evaluation uses MobileNetV2 and TFLite models"
        chunk2.page_number = 2
        chunk2.section = "Methods"
        chunk2.chunk_index = 1
        
        chunk3 = Mock(spec=PaperChunk)
        chunk3.id = uuid.uuid4()
        chunk3.text = "General discussion of machine learning approaches"
        chunk3.page_number = 3
        chunk3.section = "Related Work"
        chunk3.chunk_index = 2
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            chunk1, chunk2, chunk3
        ]
        
        # Query for "Docker"
        results = service.search_chunks(mock_db, mock_paper.id, "Docker", top_k=3)
        
        assert len(results) == 3
        # Chunk with "Docker" should rank first
        assert results[0]['chunk_id'] == str(chunk1.id)
        assert results[0]['bm25_score'] > 0
        assert results[0]['page_number'] == 1
    
    def test_search_chunks_rare_term_boost(self, service, mock_paper):
        """Test that rare terms get higher scores."""
        # Create chunks where one has a rare term
        chunk1 = Mock(spec=PaperChunk)
        chunk1.id = uuid.uuid4()
        chunk1.text = "The system uses TFLite for inference"
        chunk1.page_number = 1
        chunk1.section = "Methods"
        chunk1.chunk_index = 0
        
        chunk2 = Mock(spec=PaperChunk)
        chunk2.id = uuid.uuid4()
        chunk2.text = "The system uses common approaches for the system"
        chunk2.page_number = 2
        chunk2.section = "Methods"
        chunk2.chunk_index = 1
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            chunk1, chunk2
        ]
        
        # Query for "TFLite" (rare term)
        results = service.search_chunks(mock_db, mock_paper.id, "TFLite", top_k=2)
        
        assert len(results) == 2
        # Chunk with rare term should rank first
        assert results[0]['chunk_id'] == str(chunk1.id)
    
    def test_search_chunks_multi_word_phrase(self, service, mock_paper):
        """Test multi-word phrase matching."""
        chunk1 = Mock(spec=PaperChunk)
        chunk1.id = uuid.uuid4()
        chunk1.text = "PA-EIS uses priority-aware edge inference scheduling"
        chunk1.page_number = 1
        chunk1.section = "Abstract"
        chunk1.chunk_index = 0
        
        chunk2 = Mock(spec=PaperChunk)
        chunk2.id = uuid.uuid4()
        chunk2.text = "The edge computing platform uses standard scheduling"
        chunk2.page_number = 2
        chunk2.section = "Introduction"
        chunk2.chunk_index = 1
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            chunk1, chunk2
        ]
        
        # Query for multi-word phrase
        results = service.search_chunks(mock_db, mock_paper.id, "edge inference scheduling", top_k=2)
        
        assert len(results) == 2
        # Both chunks should be present
        chunk_ids = {r['chunk_id'] for r in results}
        assert str(chunk1.id) in chunk_ids
        assert str(chunk2.id) in chunk_ids
        # All should have BM25 score field
        assert all('bm25_score' in r for r in results)
    
    def test_search_chunks_no_match(self, service, mock_paper):
        """Test query with no matches still returns results."""
        chunk1 = Mock(spec=PaperChunk)
        chunk1.id = uuid.uuid4()
        chunk1.text = "This paper discusses containerization"
        chunk1.page_number = 1
        chunk1.section = "Introduction"
        chunk1.chunk_index = 0
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [chunk1]
        
        # Query for completely unrelated terms
        results = service.search_chunks(mock_db, mock_paper.id, "quantum cryptography", top_k=10)
        
        # Should still return chunks, but with low scores
        assert len(results) >= 1
        assert all(r['bm25_score'] >= 0 for r in results)
    
    def test_search_chunks_paper_filtering(self, service, mock_paper):
        """Test that results are filtered by paper_id."""
        # This is implicitly tested by the query filtering in the service
        # We verify the service calls the correct query filter
        chunk1 = Mock(spec=PaperChunk)
        chunk1.id = uuid.uuid4()
        chunk1.text = "Test content"
        chunk1.page_number = 1
        chunk1.section = "Test"
        chunk1.chunk_index = 0
        
        mock_db = Mock()
        query_mock = mock_db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = mock_paper
        order_by_mock = filter_mock.order_by.return_value
        order_by_mock.all.return_value = [chunk1]
        
        service.search_chunks(mock_db, mock_paper.id, "test", top_k=5)
        
        # Verify filter was called (paper_id filtering)
        assert query_mock.filter.called
    
    def test_search_chunks_deterministic_ordering(self, service, mock_paper):
        """Test that results have deterministic ordering."""
        chunks = []
        for i in range(5):
            chunk = Mock(spec=PaperChunk)
            chunk.id = uuid.uuid4()
            chunk.text = f"Test document number {i}"
            chunk.page_number = i + 1
            chunk.section = "Test"
            chunk.chunk_index = i
            chunks.append(chunk)
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = chunks
        
        # Run search multiple times
        results1 = service.search_chunks(mock_db, mock_paper.id, "test document", top_k=5)
        results2 = service.search_chunks(mock_db, mock_paper.id, "test document", top_k=5)
        
        # Results should be identical
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1['chunk_id'] == r2['chunk_id']
            assert r1['bm25_score'] == r2['bm25_score']
    
    def test_search_chunks_top_k_limit(self, service, mock_paper):
        """Test that top_k limits results."""
        chunks = []
        for i in range(10):
            chunk = Mock(spec=PaperChunk)
            chunk.id = uuid.uuid4()
            chunk.text = f"Document {i} with test content"
            chunk.page_number = i + 1
            chunk.section = "Test"
            chunk.chunk_index = i
            chunks.append(chunk)
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = chunks
        
        results = service.search_chunks(mock_db, mock_paper.id, "test", top_k=3)
        
        assert len(results) == 3
        # Verify all required fields are present
        for result in results:
            assert 'text' in result
            assert 'page_number' in result
            assert 'section' in result
            assert 'chunk_id' in result
            assert 'chunk_index' in result
            assert 'bm25_score' in result
            assert 'rank' in result

