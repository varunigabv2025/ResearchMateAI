"""
Tests for embedding service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Tests for embedding service."""
    
    @pytest.fixture
    def service(self):
        """Create embedding service instance."""
        return EmbeddingService()
    
    @pytest.mark.asyncio
    async def test_generate_embedding_success(self, service):
        """Test successful embedding generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3] * 512}]  # 1536 dimensions
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            # Mock the dimension check
            with patch.object(service, 'dimension', 1536):
                embedding = await service.generate_embedding("test text")
                
                assert isinstance(embedding, list)
                assert len(embedding) == 1536
    
    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self, service):
        """Test embedding generation with empty text."""
        with pytest.raises(ValueError, match="Cannot generate embedding for empty text"):
            await service.generate_embedding("")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_dimension_mismatch(self, service):
        """Test embedding generation with wrong dimension."""
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
    async def test_generate_embeddings_batch(self, service):
        """Test batch embedding generation."""
        texts = ["text1", "text2", "text3"]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1] * 1536}]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            with patch.object(service, 'dimension', 1536):
                embeddings = await service.generate_embeddings_batch(texts)
                
                assert len(embeddings) == 3
                assert all(isinstance(e, list) for e in embeddings)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_api_error(self, service):
        """Test handling of API errors."""
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
