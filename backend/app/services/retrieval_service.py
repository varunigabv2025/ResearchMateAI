"""
Vector similarity retrieval service for finding relevant paper chunks.
"""
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import PaperChunk, Embedding, Paper
from app.services.embedding_service import embedding_service

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False


class RetrievalService:
    """
    Service for retrieving relevant paper chunks using vector similarity search.
    """
    
    # Configuration
    DEFAULT_TOP_K = 5
    DEFAULT_SIMILARITY_THRESHOLD = 0.7  # Cosine similarity threshold (0-1)
    
    def __init__(self):
        self.embedding_service = embedding_service
    
    async def retrieve_relevant_chunks(
        self,
        db: Session,
        paper_id: UUID,
        question: str,
        top_k: int = DEFAULT_TOP_K,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a question about a specific paper.
        
        Args:
            db: Database session
            paper_id: UUID of the paper to search within
            question: User's question
            top_k: Maximum number of chunks to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of dictionaries containing:
            - text: Chunk text
            - page_number: Page number
            - section: Section name
            - chunk_id: Chunk UUID
            - chunk_index: Position in document
            - similarity: Similarity score
        """
        # Validate paper exists
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError(f"Paper with id {paper_id} not found")
        
        # Check if paper is fully processed
        if not paper.processed:
            error_msg = "Paper has not been fully processed"
            if paper.processing_error:
                error_msg += f": {paper.processing_error}"
            raise ValueError(error_msg)
        
        # Generate embedding for the question
        question_embedding = await self.embedding_service.generate_embedding(question, is_query=True)
        
        # Perform similarity search
        if HAS_PGVECTOR:
            results = self._search_with_pgvector(
                db, paper_id, question_embedding, top_k
            )
        else:
            results = self._search_with_fallback(
                db, paper_id, question_embedding, top_k
            )
        
        # Filter by similarity threshold and format results
        filtered_results = []
        for result in results:
            if result['similarity'] >= similarity_threshold:
                filtered_results.append({
                    'text': result['text'],
                    'page_number': result['page_number'],
                    'section': result['section'],
                    'chunk_id': str(result['chunk_id']),
                    'chunk_index': result['chunk_index'],
                    'similarity': result['similarity']
                })
        
        return filtered_results
    
    def _search_with_pgvector(
        self,
        db: Session,
        paper_id: UUID,
        query_embedding: List[float],
        top_k: int
    ) -> List[Dict]:
        """
        Search using pgvector's native similarity operators.
        Uses cosine distance.
        """
        # Query with pgvector cosine distance
        # Join chunks -> embeddings, filter by paper_id
        results = db.query(
            PaperChunk.id.label('chunk_id'),
            PaperChunk.text,
            PaperChunk.page_number,
            PaperChunk.section,
            PaperChunk.chunk_index,
            Embedding.embedding.cosine_distance(query_embedding).label('distance')
        ).join(
            Embedding, Embedding.chunk_id == PaperChunk.id
        ).filter(
            PaperChunk.paper_id == paper_id
        ).order_by(
            'distance'
        ).limit(top_k).all()
        
        # Convert distance to similarity (1 - distance for cosine)
        return [
            {
                'chunk_id': r.chunk_id,
                'text': r.text,
                'page_number': r.page_number,
                'section': r.section,
                'chunk_index': r.chunk_index,
                'similarity': 1.0 - r.distance
            }
            for r in results
        ]
    
    def _search_with_fallback(
        self,
        db: Session,
        paper_id: UUID,
        query_embedding: List[float],
        top_k: int
    ) -> List[Dict]:
        """
        Fallback search without pgvector (for testing).
        Uses simple cosine similarity computation in Python.
        """
        import numpy as np
        
        # Get all chunks and embeddings for this paper
        results = db.query(
            PaperChunk.id.label('chunk_id'),
            PaperChunk.text,
            PaperChunk.page_number,
            PaperChunk.section,
            PaperChunk.chunk_index,
            Embedding.embedding
        ).join(
            Embedding, Embedding.chunk_id == PaperChunk.id
        ).filter(
            PaperChunk.paper_id == paper_id
        ).all()
        
        # Compute cosine similarities
        scored_results = []
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        for r in results:
            # Handle both list and JSON stored embeddings
            chunk_embedding = r.embedding if isinstance(r.embedding, list) else r.embedding
            chunk_vec = np.array(chunk_embedding)
            chunk_norm = np.linalg.norm(chunk_vec)
            
            # Cosine similarity
            if query_norm > 0 and chunk_norm > 0:
                similarity = np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm)
            else:
                similarity = 0.0
            
            scored_results.append({
                'chunk_id': r.chunk_id,
                'text': r.text,
                'page_number': r.page_number,
                'section': r.section,
                'chunk_index': r.chunk_index,
                'similarity': float(similarity)
            })
        
        # Sort by similarity and return top_k
        scored_results.sort(key=lambda x: x['similarity'], reverse=True)
        return scored_results[:top_k]


# Global instance
retrieval_service = RetrievalService()
