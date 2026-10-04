"""
Lexical (BM25) search service for finding relevant paper chunks.

This module implements BM25-based lexical retrieval to complement dense vector retrieval.
Uses rank-bm25 library for BM25Okapi algorithm.

Note: This implementation constructs the BM25 index per query for the selected paper.
This is acceptable for single-paper queries but may need optimization for larger corpora.
"""
import logging
from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi

from app.models import PaperChunk, Paper

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LexicalSearchService:
    """
    Service for BM25-based lexical retrieval of paper chunks.
    
    This service provides term-based retrieval to complement semantic vector search.
    It's particularly effective for queries with specific technical terms, acronyms,
    or rare keywords.
    """
    
    def __init__(self):
        """Initialize lexical search service."""
        pass
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25.
        
        Uses simple whitespace tokenization with lowercasing.
        This is deterministic and requires no external dependencies.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens (lowercase)
        """
        if not text:
            return []
        
        # Simple whitespace tokenization with lowercase
        # This is deterministic and works well for technical text
        tokens = text.lower().split()
        
        # Remove empty tokens
        tokens = [t for t in tokens if t.strip()]
        
        return tokens
    
    def search_chunks(
        self,
        db: Session,
        paper_id: UUID,
        query: str,
        top_k: int = 20
    ) -> List[Dict]:
        """
        Search for relevant chunks using BM25 lexical matching.
        
        Args:
            db: Database session
            paper_id: UUID of the paper to search within
            query: Search query
            top_k: Maximum number of chunks to return
            
        Returns:
            List of dictionaries containing:
            - text: Chunk text
            - page_number: Page number
            - section: Section name
            - chunk_id: Chunk UUID
            - chunk_index: Position in document
            - bm25_score: BM25 relevance score
            
        Raises:
            ValueError: If paper not found or not processed
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
        
        # Handle empty query
        if not query or not query.strip():
            logger.warning("Empty query provided to lexical search")
            return []
        
        # Get all chunks for this paper
        chunks = db.query(PaperChunk).filter(
            PaperChunk.paper_id == paper_id
        ).order_by(
            PaperChunk.chunk_index
        ).all()
        
        # Handle empty corpus
        if not chunks:
            logger.warning(f"No chunks found for paper {paper_id}")
            return []
        
        # Tokenize corpus
        corpus = [chunk.text for chunk in chunks]
        tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        
        # Handle corpus with all empty documents
        if all(len(doc) == 0 for doc in tokenized_corpus):
            logger.warning(f"All chunks for paper {paper_id} are empty after tokenization")
            return []
        
        # Create BM25 index
        try:
            bm25 = BM25Okapi(tokenized_corpus)
        except Exception as e:
            logger.error(f"Failed to create BM25 index: {e}")
            return []
        
        # Tokenize query
        tokenized_query = self._tokenize(query)
        
        # Handle empty tokenized query
        if not tokenized_query:
            logger.warning("Query is empty after tokenization")
            return []
        
        # Get BM25 scores
        try:
            scores = bm25.get_scores(tokenized_query)
        except Exception as e:
            logger.error(f"Failed to compute BM25 scores: {e}")
            return []
        
        # Create results with scores
        chunk_scores = []
        for i, (chunk, score) in enumerate(zip(chunks, scores)):
            chunk_scores.append({
                'chunk': chunk,
                'score': float(score),
                'rank': i  # Will be updated after sorting
            })
        
        # Sort by score descending
        chunk_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Update ranks (1-indexed for RRF)
        for rank, item in enumerate(chunk_scores, start=1):
            item['rank'] = rank
        
        # Get top-K
        top_chunks = chunk_scores[:top_k]
        
        # Format results
        results = []
        for item in top_chunks:
            chunk = item['chunk']
            results.append({
                'text': chunk.text,
                'page_number': chunk.page_number,
                'section': chunk.section,
                'chunk_id': str(chunk.id),
                'chunk_index': chunk.chunk_index,
                'bm25_score': item['score'],
                'rank': item['rank']
            })
        
        logger.info(f"Lexical search returned {len(results)} chunks for paper {paper_id}")
        
        return results


# Global instance
lexical_search_service = LexicalSearchService()
