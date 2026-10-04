"""
Vector similarity retrieval service for finding relevant paper chunks.

Supports multiple retrieval modes:
- Dense: Vector similarity only (default, original behavior)
- Lexical: BM25-based term matching
- Hybrid: Reciprocal Rank Fusion of dense + lexical
"""
import logging
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from enum import Enum

from app.models import PaperChunk, Embedding, Paper
from app.services.embedding_service import embedding_service
from app.services.lexical_search import lexical_search_service

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    from pgvector.sqlalchemy import Vector  # type: ignore
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False


class RetrievalMode(str, Enum):
    """Retrieval mode for chunk selection."""
    DENSE = "dense"      # Vector similarity only
    LEXICAL = "lexical"  # BM25 lexical matching only
    HYBRID = "hybrid"    # RRF fusion of dense + lexical


class RetrievalService:
    """
    Service for retrieving relevant paper chunks using various retrieval strategies.
    
    Supports:
    - Dense: Vector similarity search (original behavior, default)
    - Lexical: BM25-based term matching
    - Hybrid: Reciprocal Rank Fusion combining both
    """
    
    # Configuration
    DEFAULT_TOP_K = 5
    DEFAULT_SIMILARITY_THRESHOLD = 0.4  # Cosine similarity threshold (0-1) calibrated for Qwen3 local embeddings
    DEFAULT_DENSE_K = 20  # Candidate pool for hybrid retrieval
    DEFAULT_LEXICAL_K = 20  # Candidate pool for hybrid retrieval
    DEFAULT_RRF_K = 60  # RRF parameter (standard value)
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.lexical_service = lexical_search_service
    
    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Dict],
        lexical_results: List[Dict],
        rrf_k: int = DEFAULT_RRF_K
    ) -> List[Dict]:
        """
        Combine dense and lexical results using Reciprocal Rank Fusion.
        
        RRF formula: RRF(d) = Σ 1 / (k + rank(d))
        
        Where:
        - d = document (chunk)
        - rank(d) = rank of document in source (1-indexed)
        - k = constant (typically 60)
        
        Args:
            dense_results: Results from dense retrieval with 'rank' field
            lexical_results: Results from lexical retrieval with 'rank' field
            rrf_k: RRF constant (default 60)
            
        Returns:
            Fused results sorted by RRF score, deduplicated by chunk_id
        """
        # Build RRF scores by chunk_id
        rrf_scores = {}
        chunk_data = {}
        
        # Process dense results
        for result in dense_results:
            chunk_id = result['chunk_id']
            rank = result.get('rank', len(dense_results) + 1)
            
            # RRF contribution from dense source
            rrf_score = 1.0 / (rrf_k + rank)
            
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0
                chunk_data[chunk_id] = {
                    'text': result['text'],
                    'page_number': result['page_number'],
                    'section': result['section'],
                    'chunk_id': chunk_id,
                    'chunk_index': result['chunk_index'],
                    'dense_similarity': result.get('similarity'),
                    'dense_rank': rank,
                    'lexical_score': None,
                    'lexical_rank': None
                }
            
            rrf_scores[chunk_id] += rrf_score
            chunk_data[chunk_id]['dense_similarity'] = result.get('similarity')
            chunk_data[chunk_id]['dense_rank'] = rank
        
        # Process lexical results
        for result in lexical_results:
            chunk_id = result['chunk_id']
            rank = result.get('rank', len(lexical_results) + 1)
            
            # RRF contribution from lexical source
            rrf_score = 1.0 / (rrf_k + rank)
            
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0
                chunk_data[chunk_id] = {
                    'text': result['text'],
                    'page_number': result['page_number'],
                    'section': result['section'],
                    'chunk_id': chunk_id,
                    'chunk_index': result['chunk_index'],
                    'dense_similarity': None,
                    'dense_rank': None,
                    'lexical_score': result.get('bm25_score'),
                    'lexical_rank': rank
                }
            
            rrf_scores[chunk_id] += rrf_score
            chunk_data[chunk_id]['lexical_score'] = result.get('bm25_score')
            chunk_data[chunk_id]['lexical_rank'] = rank
        
        # Create result list with RRF scores
        fused_results = []
        for chunk_id, rrf_score in rrf_scores.items():
            result = chunk_data[chunk_id].copy()
            result['rrf_score'] = rrf_score
            fused_results.append(result)
        
        # Sort by RRF score descending, then by chunk_id for deterministic tie-breaking
        # Convert chunk_id to string for comparison
        fused_results.sort(key=lambda x: (-x['rrf_score'], str(x['chunk_id'])))
        
        logger.info(f"RRF fused {len(dense_results)} dense + {len(lexical_results)} lexical → {len(fused_results)} unique chunks")
        
        return fused_results
    
    async def retrieve_relevant_chunks(
        self,
        db: Session,
        paper_id: UUID,
        question: str,
        top_k: int = DEFAULT_TOP_K,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        mode: RetrievalMode = RetrievalMode.DENSE,
        dense_k: int = DEFAULT_DENSE_K,
        lexical_k: int = DEFAULT_LEXICAL_K,
        rrf_k: int = DEFAULT_RRF_K
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a question about a specific paper.
        
        Supports three retrieval modes:
        - DENSE: Vector similarity only (default, preserves original behavior)
        - LEXICAL: BM25 term matching only
        - HYBRID: RRF fusion of dense + lexical
        
        Args:
            db: Database session
            paper_id: UUID of the paper to search within
            question: User's question
            top_k: Maximum number of chunks to return (final result size)
            similarity_threshold: Minimum similarity score for DENSE mode (0-1)
            mode: Retrieval mode (DENSE, LEXICAL, or HYBRID)
            dense_k: Candidate pool size for dense retrieval in HYBRID mode
            lexical_k: Candidate pool size for lexical retrieval in HYBRID mode
            rrf_k: RRF constant for HYBRID mode
            
        Returns:
            List of dictionaries containing:
            - text: Chunk text
            - page_number: Page number
            - section: Section name
            - chunk_id: Chunk UUID
            - chunk_index: Position in document
            
            Additional fields depending on mode:
            - DENSE: similarity (float)
            - LEXICAL: bm25_score (float)
            - HYBRID: rrf_score, dense_similarity, lexical_score, dense_rank, lexical_rank
        """
        # Validate paper exists (common for all modes)
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError(f"Paper with id {paper_id} not found")
        
        # Check if paper is fully processed
        if not paper.processed:
            error_msg = "Paper has not been fully processed"
            if paper.processing_error:
                error_msg += f": {paper.processing_error}"
            raise ValueError(error_msg)
        
        logger.info(f"Retrieval mode: {mode}, paper: {paper_id}, question length: {len(question)}")
        
        # Route to appropriate retrieval method
        if mode == RetrievalMode.DENSE:
            return await self._retrieve_dense(
                db, paper_id, question, top_k, similarity_threshold
            )
        elif mode == RetrievalMode.LEXICAL:
            return self._retrieve_lexical(
                db, paper_id, question, top_k
            )
        elif mode == RetrievalMode.HYBRID:
            return await self._retrieve_hybrid(
                db, paper_id, question, top_k, dense_k, lexical_k, rrf_k, similarity_threshold
            )
        else:
            raise ValueError(f"Unknown retrieval mode: {mode}")
    
    async def _retrieve_dense(
        self,
        db: Session,
        paper_id: UUID,
        question: str,
        top_k: int,
        similarity_threshold: float
    ) -> List[Dict]:
        """
        Dense vector retrieval (original behavior).
        
        This preserves the exact original retrieval logic.
        """
        # Generate embedding for the question
        question_embedding = await self.embedding_service.generate_embedding(question, is_query=True)
        
        # Log retrieval operation for diagnostics
        logger.debug(f"Dense retrieval for paper {paper_id}: question length={len(question)} chars")
        logger.debug(f"Query embedding dimension: {len(question_embedding)}")
        
        # Perform similarity search
        if HAS_PGVECTOR:
            results = self._search_with_pgvector(
                db, paper_id, question_embedding, top_k
            )
        else:
            results = self._search_with_fallback(
                db, paper_id, question_embedding, top_k
            )
        
        # Add ranks (1-indexed)
        for rank, result in enumerate(results, start=1):
            result['rank'] = rank
        
        # Filter by similarity threshold and format results
        filtered_results = []
        
        # Log retrieval results for diagnostics (without full text content)
        logger.info(f"Retrieved {len(results)} chunks, threshold={similarity_threshold}")
        for i, result in enumerate(results[:5]):  # Log top 5 only
            logger.debug(
                f"Chunk {i+1}: similarity={result['similarity']:.4f}, "
                f"page={result['page_number']}, section={result.get('section', 'N/A')}"
            )
        
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
        
        logger.info(f"Returned {len(filtered_results)} chunks after filtering")
        
        return filtered_results
    
    def _retrieve_lexical(
        self,
        db: Session,
        paper_id: UUID,
        question: str,
        top_k: int
    ) -> List[Dict]:
        """
        Lexical BM25 retrieval only.
        """
        results = self.lexical_service.search_chunks(
            db=db,
            paper_id=paper_id,
            query=question,
            top_k=top_k
        )
        
        # Format for compatibility (remove internal rank field from output)
        formatted_results = []
        for result in results:
            formatted_results.append({
                'text': result['text'],
                'page_number': result['page_number'],
                'section': result['section'],
                'chunk_id': result['chunk_id'],
                'chunk_index': result['chunk_index'],
                'bm25_score': result['bm25_score']
            })
        
        logger.info(f"Lexical retrieval returned {len(formatted_results)} chunks")
        
        return formatted_results
    
    async def _retrieve_hybrid(
        self,
        db: Session,
        paper_id: UUID,
        question: str,
        final_top_k: int,
        dense_k: int,
        lexical_k: int,
        rrf_k: int,
        similarity_threshold: float
    ) -> List[Dict]:
        """
        Hybrid retrieval using RRF fusion of dense + lexical.
        
        Strategy:
        1. Get dense_k candidates from vector search (no threshold)
        2. Get lexical_k candidates from BM25
        3. Fuse with RRF
        4. Return final_top_k results
        
        Note: For hybrid mode, we retrieve more candidates before fusion
        to give RRF enough material to work with. The similarity_threshold
        is NOT applied before fusion to avoid excluding potentially useful
        candidates that might rank well after fusion.
        """
        # Get dense candidates (no threshold filtering before fusion)
        question_embedding = await self.embedding_service.generate_embedding(question, is_query=True)
        
        logger.debug(f"Hybrid retrieval: dense_k={dense_k}, lexical_k={lexical_k}, final_k={final_top_k}")
        
        if HAS_PGVECTOR:
            dense_results = self._search_with_pgvector(
                db, paper_id, question_embedding, dense_k
            )
        else:
            dense_results = self._search_with_fallback(
                db, paper_id, question_embedding, dense_k
            )
        
        # Add ranks to dense results
        for rank, result in enumerate(dense_results, start=1):
            result['rank'] = rank
        
        # Get lexical candidates
        lexical_results = self.lexical_service.search_chunks(
            db=db,
            paper_id=paper_id,
            query=question,
            top_k=lexical_k
        )
        
        # Fuse with RRF
        fused_results = self._reciprocal_rank_fusion(
            dense_results=dense_results,
            lexical_results=lexical_results,
            rrf_k=rrf_k
        )
        
        # Take final top-K
        final_results = fused_results[:final_top_k]
        
        # Format results for output
        formatted_results = []
        for result in final_results:
            formatted_results.append({
                'text': result['text'],
                'page_number': result['page_number'],
                'section': result['section'],
                'chunk_id': result['chunk_id'],
                'chunk_index': result['chunk_index'],
                'rrf_score': result['rrf_score'],
                'dense_similarity': result['dense_similarity'],
                'lexical_score': result['lexical_score'],
                'dense_rank': result['dense_rank'],
                'lexical_rank': result['lexical_rank']
            })
        
        logger.info(f"Hybrid retrieval returned {len(formatted_results)} chunks after RRF fusion")
        
        return formatted_results
    
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
