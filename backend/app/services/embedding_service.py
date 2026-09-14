"""
Embedding generation service with modular API provider support.
"""
import httpx
from typing import List, Optional
import asyncio

from app.core.config import settings


class EmbeddingService:
    """
    Service for generating text embeddings using configured API provider.
    Supports OpenAI-compatible APIs.
    """
    
    def __init__(self):
        self.api_key = settings.EMBEDDING_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.api_base_url = settings.EMBEDDING_API_BASE_URL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.timeout = 30.0
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Cannot generate embedding for empty text")
        
        # Prepare API request
        url = f"{self.api_base_url.rstrip('/')}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "input": text
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                embedding = data["data"][0]["embedding"]
                
                # Validate dimension
                if len(embedding) != self.dimension:
                    raise ValueError(
                        f"Embedding dimension mismatch: expected {self.dimension}, "
                        f"got {len(embedding)}"
                    )
                
                return embedding
                
            except httpx.HTTPStatusError as e:
                raise Exception(f"Embedding API error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                raise Exception(f"Embedding API request failed: {str(e)}")
            except KeyError as e:
                raise Exception(f"Unexpected embedding API response format: missing {str(e)}")
    
    async def generate_embeddings_batch(
        self, 
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Maximum number of texts per API request
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        
        # Process in batches to avoid API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # For now, process sequentially within batch
            # Could be parallelized further if needed
            batch_embeddings = []
            for text in batch:
                try:
                    embedding = await self.generate_embedding(text)
                    batch_embeddings.append(embedding)
                except Exception as e:
                    # Re-raise with context about which text failed
                    raise Exception(f"Failed to embed text at index {i + len(batch_embeddings)}: {str(e)}")
            
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def generate_embedding_sync(self, text: str) -> List[float]:
        """
        Synchronous wrapper for generate_embedding.
        Useful for non-async contexts.
        """
        return asyncio.run(self.generate_embedding(text))
    
    def generate_embeddings_batch_sync(self, texts: List[str]) -> List[List[float]]:
        """
        Synchronous wrapper for generate_embeddings_batch.
        Useful for non-async contexts.
        """
        return asyncio.run(self.generate_embeddings_batch(texts))


# Global instance
embedding_service = EmbeddingService()
