"""
Tests for embedding service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from app.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Tests for embedding service."""
    
    @pytest.fixture
    def mock_sentence_transformer(self):
        """Create mock SentenceTransformer that returns 1024-dim vectors."""
        mock_model = MagicMock()
        mock_model.device = "cpu"
        
        # Mock encode to return proper numpy-like array with len()
        def mock_encode(text, **kwargs):
            # Return different vectors for different inputs for testing
            if isinstance(text, list):
                # For batch encoding, return list of arrays
                import numpy as np
                return np.array([[0.1 + i * 0.01] * 1024 for i in range(len(text))])
            else:
                # For single text, return 1D array
                import numpy as np
                return np.array([0.1] * 1024)
        
        # Use MagicMock for encode to track calls
        mock_model.encode = MagicMock(side_effect=mock_encode)
        mock_model.prompts = {"query": "test query prompt"}  # Simulate Qwen3 prompts
        return mock_model
    
    @pytest.mark.asyncio
    async def test_generate_embedding_success_api(self):
        """Test successful embedding generation with API."""
        # Create service with API configuration
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = "test-key"
            mock_settings.EMBEDDING_MODEL = "test-model"
            mock_settings.EMBEDDING_API_BASE_URL = "https://api.test.com/v1"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            service = EmbeddingService()
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [{"embedding": [0.1] * 1024}]
            }
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                embedding = await service.generate_embedding("test text")
                
                assert isinstance(embedding, list)
                assert len(embedding) == 1024
    
    @pytest.mark.asyncio
    async def test_generate_embedding_success_local(self, mock_sentence_transformer):
        """Test successful embedding generation with local model."""
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = ""
            mock_settings.EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
            mock_settings.EMBEDDING_API_BASE_URL = "local"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
                with patch('torch.cuda.is_available', return_value=False):
                    service = EmbeddingService()
                    
                    embedding = await service.generate_embedding("test text")
                    
                    assert isinstance(embedding, list)
                    assert len(embedding) == 1024
    
    @pytest.mark.asyncio
    async def test_generate_embedding_local_document_vs_query(self, mock_sentence_transformer):
        """Test that document and query embeddings use the same model but different prompts."""
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = ""
            mock_settings.EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
            mock_settings.EMBEDDING_API_BASE_URL = "local"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
                with patch('torch.cuda.is_available', return_value=False):
                    service = EmbeddingService()
                    
                    # Generate document embedding
                    doc_embedding = await service.generate_embedding("test document", is_query=False)
                    
                    # Generate query embedding
                    query_embedding = await service.generate_embedding("test query", is_query=True)
                    
                    # Both should be 1024 dimensions
                    assert len(doc_embedding) == 1024
                    assert len(query_embedding) == 1024
                    
                    # Verify model.encode was called (same model used for both)
                    assert mock_sentence_transformer.encode.call_count == 3  # 1 init test + 2 actual
    
    @pytest.mark.asyncio
    async def test_generate_embedding_local_model_singleton(self, mock_sentence_transformer):
        """Test that local model is loaded once and reused."""
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = ""
            mock_settings.EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
            mock_settings.EMBEDDING_API_BASE_URL = "local"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer) as mock_st:
                with patch('torch.cuda.is_available', return_value=False):
                    service = EmbeddingService()
                    
                    # Generate multiple embeddings
                    await service.generate_embedding("text1")
                    await service.generate_embedding("text2")
                    await service.generate_embedding("text3")
                    
                    # SentenceTransformer should be instantiated only once
                    assert mock_st.call_count == 1
    
    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text."""
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_BASE_URL = "https://api.test.com/v1"  # Use API mode
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            service = EmbeddingService()
            
            with pytest.raises(ValueError, match="Cannot generate embedding for empty text"):
                await service.generate_embedding("")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_dimension_mismatch_api(self):
        """Test embedding generation with wrong dimension from API."""
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = "test-key"
            mock_settings.EMBEDDING_MODEL = "test-model"
            mock_settings.EMBEDDING_API_BASE_URL = "https://api.test.com/v1"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            service = EmbeddingService()
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [{"embedding": [0.1, 0.2, 0.3]}]  # Wrong dimension
            }
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                with pytest.raises(ValueError, match="Embedding dimension mismatch"):
                    await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch_local(self, mock_sentence_transformer):
        """Test batch embedding generation with local model."""
        texts = ["text1", "text2", "text3"]
        
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = ""
            mock_settings.EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
            mock_settings.EMBEDDING_API_BASE_URL = "local"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer):
                with patch('torch.cuda.is_available', return_value=False):
                    service = EmbeddingService()
                    
                    embeddings = await service.generate_embeddings_batch(texts)
                    
                    assert len(embeddings) == 3
                    assert all(isinstance(e, list) for e in embeddings)
                    assert all(len(e) == 1024 for e in embeddings)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_api_error(self):
        """Test handling of API errors."""
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = "test-key"
            mock_settings.EMBEDDING_MODEL = "test-model"
            mock_settings.EMBEDDING_API_BASE_URL = "https://api.test.com/v1"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            service = EmbeddingService()
            
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_response.raise_for_status.side_effect = Exception("API Error")
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                with pytest.raises(Exception, match="API Error"):
                    await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_gpu_detection(self, mock_sentence_transformer):
        """Test that GPU is used when CUDA is available."""
        with patch('app.services.embedding_service.settings') as mock_settings:
            mock_settings.EMBEDDING_API_KEY = ""
            mock_settings.EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
            mock_settings.EMBEDDING_API_BASE_URL = "local"
            mock_settings.EMBEDDING_DIMENSION = 1024
            
            mock_sentence_transformer.device = "cuda"
            
            with patch('sentence_transformers.SentenceTransformer', return_value=mock_sentence_transformer) as mock_st:
                with patch('torch.cuda.is_available', return_value=True):
                    service = EmbeddingService()
                    
                    # Verify model was initialized with cuda device
                    mock_st.assert_called_once()
                    call_kwargs = mock_st.call_args[1]
                    assert call_kwargs['device'] == 'cuda'
