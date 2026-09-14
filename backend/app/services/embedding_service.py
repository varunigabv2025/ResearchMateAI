"""
Embedding generation service with modular API provider support and local models.
"""
import httpx
from typing import List, Optional
import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using configured API provider or local models.
    Supports both OpenAI-compatible APIs and local sentence-transformers models.
    """
    
    def __init__(self):
        self.api_key = settings.EMBEDDING_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.api_base_url = settings.EMBEDDING_API_BASE_URL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.timeout = 30.0
        
        # Check if using local embeddings
        self.is_local = self.api_base_url == "local"
        self._local_model = None
        
        if self.is_local:
            self._initialize_local_model()
    
    def _initialize_local_model(self):
        """Initialize local sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            # Determine device - auto-detect CUDA if available, otherwise CPU
            if torch.cuda.is_available():
                device = "cuda"
                logger.info("CUDA detected - will use GPU for embeddings")
            else:
                device = "cpu"
                logger.info("No CUDA detected - will use CPU for embeddings")
            
            logger.info(f"Loading local embedding model: {self.model}")
            logger.info("This may take a few moments on first use (downloading model weights)...")
            
            # Load model with detected device
            self._local_model = SentenceTransformer(
                self.model,
                device=device,
                trust_remote_code=False  # Security: don't execute remote code
            )
            
            # Verify dimension
            logger.info("Model loaded, verifying dimensions...")
            test_embedding = self._local_model.encode("test", convert_to_numpy=True)
            actual_dim = len(test_embedding)
            
            if actual_dim != self.dimension:
                logger.warning(
                    f"Model {self.model} produces {actual_dim} dimensions, "
                    f"but config expects {self.dimension}. Using actual dimension."
                )
                self.dimension = actual_dim
            
            logger.info(
                f"Local embedding model loaded successfully. "
                f"Dimension: {self.dimension}, Device: {self._local_model.device}"
            )
        except ImportError as e:
            raise RuntimeError(
                "sentence-transformers package is required for local embeddings. "
                f"Install with: pip install sentence-transformers. Error: {str(e)}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load local embedding model {self.model}: {str(e)}")
    
    async def generate_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            is_query: Whether this is a query (vs document). Some models use different
                     prompts for queries vs documents for better retrieval.
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Cannot generate embedding for empty text")
        
        if self.is_local:
            return await self._generate_embedding_local(text, is_query=is_query)
        else:
            return await self._generate_embedding_api(text)
    
    async def _generate_embedding_local(self, text: str, is_query: bool = False) -> List[float]:
        """Generate embedding using local model."""
        try:
            # Run in thread pool to avoid blocking async event loop
            loop = asyncio.get_event_loop()
            
            # Qwen3-Embedding models have prompt support for queries
            # Documents don't need prompts
            kwargs = {
                "convert_to_numpy": True,
                "show_progress_bar": False
            }
            if is_query and hasattr(self._local_model, 'prompts') and 'query' in self._local_model.prompts:
                kwargs["prompt_name"] = "query"
            
            embedding = await loop.run_in_executor(
                None,
                lambda: self._local_model.encode(text, **kwargs).tolist()
            )
            return embedding
        except Exception as e:
            raise Exception(f"Local embedding generation failed: {str(e)}")
    
    async def _generate_embedding_api(self, text: str) -> List[float]:
        """Generate embedding using API."""
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
            batch_size: Maximum number of texts per API request (for API mode)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.is_local:
            return await self._generate_embeddings_batch_local(texts)
        else:
            return await self._generate_embeddings_batch_api(texts, batch_size)
    
    async def _generate_embeddings_batch_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batch using local model."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self._local_model.encode(
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    batch_size=32  # Process in smaller batches for memory efficiency
                )
            )
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            raise Exception(f"Batch local embedding generation failed: {str(e)}")
    
    async def _generate_embeddings_batch_api(
        self,
        texts: List[str],
        batch_size: int
    ) -> List[List[float]]:
        """Generate embeddings in batch using API."""
        embeddings = []
        
        # Process in batches to avoid API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # For now, process sequentially within batch
            # Could be parallelized further if needed
            batch_embeddings = []
            for text in batch:
                try:
                    embedding = await self._generate_embedding_api(text)
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
