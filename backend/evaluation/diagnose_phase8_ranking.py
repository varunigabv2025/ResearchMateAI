"""
Phase 8 Ranking Diagnostic Script

Analyzes actual dense, BM25, and RRF ranks/scores for difficult questions
to identify the ranking bottleneck.

This is a diagnostic tool only - does not modify any data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import PaperChunk, Embedding, Paper
from app.services.retrieval_service import retrieval_service, RetrievalMode
from app.services.embedding_service import embedding_service
from app.services.lexical_search import lexical_search_service
import asyncio
import json
from uuid import UUID
import numpy as np


PAPER_ID = UUID('075cdd7f-bff1-43fd-a52c-bba13a64acda')


async def analyze_question_ranking(db, question_id, question_text, relevant_pages):
    """
    Analyze dense, BM25, and RRF rankings for a specific question.
    
    Returns detailed diagnostic information about where relevant chunks rank.
    """
    print(f"\n{'='*80}")
    print(f"ANALYZING: {question_id}")
    print(f"Question: {question_text}")
    print(f"Relevant pages (ground truth): {relevant_pages}")
    print('='*80)
    
    # Get all chunks for this paper
    all_chunks = db.query(PaperChunk).filter(
        PaperChunk.paper_id == PAPER_ID
    ).order_by(PaperChunk.chunk_index).all()
    
    # Identify relevant chunks based on page numbers
    relevant_chunks = [c for c in all_chunks if c.page_number in relevant_pages]
    print(f"\nRelevant chunks: {len(relevant_chunks)}")
    for chunk in relevant_chunks:
        snippet = chunk.text[:100].encode('ascii', errors='replace').decode('ascii')
        print(f"  Chunk {chunk.chunk_index} (page {chunk.page_number}): \"{snippet}...\"")
    
    # 1. DENSE RETRIEVAL ANALYSIS
    print(f"\n{'-'*80}")
    print("DENSE RETRIEVAL ANALYSIS")
    print('-'*80)
    
    # Generate query embedding
    question_embedding = await embedding_service.generate_embedding(question_text, is_query=True)
    
    # Get all chunks with embeddings
    chunk_embeddings = db.query(
        PaperChunk.id,
        PaperChunk.chunk_index,
        PaperChunk.page_number,
        PaperChunk.text,
        Embedding.embedding
    ).join(
        Embedding, Embedding.chunk_id == PaperChunk.id
    ).filter(
        PaperChunk.paper_id == PAPER_ID
    ).all()
    
    # Compute cosine similarities for ALL chunks
    dense_scores = []
    for chunk_id, chunk_idx, page_num, text, emb in chunk_embeddings:
        # Convert embedding to numpy array
        if isinstance(emb, str):
            import json
            emb = json.loads(emb)
        chunk_emb = np.array(emb)
        query_emb = np.array(question_embedding)
        
        # Cosine similarity
        similarity = np.dot(query_emb, chunk_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(chunk_emb))
        
        dense_scores.append({
            'chunk_id': str(chunk_id),
            'chunk_index': chunk_idx,
            'page_number': page_num,
            'text_snippet': text[:100],
            'similarity': float(similarity),
            'is_relevant': page_num in relevant_pages
        })
    
    # Sort by similarity (descending)
    dense_scores.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Add ranks
    for rank, item in enumerate(dense_scores, start=1):
        item['dense_rank'] = rank
    
    print(f"\nTop-10 Dense Results:")
    for i in range(min(10, len(dense_scores))):
        item = dense_scores[i]
        marker = "★ RELEVANT" if item['is_relevant'] else ""
        print(f"  {i+1}. Page {item['page_number']}, Chunk {item['chunk_index']}, "
              f"Similarity: {item['similarity']:.4f} {marker}")
    
    print(f"\nRelevant chunks in dense retrieval:")
    for item in dense_scores:
        if item['is_relevant']:
            print(f"  Rank {item['dense_rank']}: Page {item['page_number']}, Chunk {item['chunk_index']}, "
                  f"Similarity: {item['similarity']:.4f}")
    
    # 2. BM25 RETRIEVAL ANALYSIS
    print(f"\n{'-'*80}")
    print("BM25 RETRIEVAL ANALYSIS")
    print('-'*80)
    
    # Use lexical search service to get BM25 scores
    bm25_results = lexical_search_service.search_chunks(
        db=db,
        paper_id=PAPER_ID,
        query=question_text,
        top_k=len(all_chunks)  # Get all results with scores
    )
    
    print(f"\nTop-10 BM25 Results:")
    for i in range(min(10, len(bm25_results))):
        result = bm25_results[i]
        marker = "★ RELEVANT" if result['page_number'] in relevant_pages else ""
        print(f"  {i+1}. Page {result['page_number']}, Chunk {result['chunk_index']}, "
              f"BM25 Score: {result['bm25_score']:.4f} {marker}")
    
    print(f"\nRelevant chunks in BM25 retrieval:")
    for result in bm25_results:
        if result['page_number'] in relevant_pages:
            print(f"  Rank {result['rank']}: Page {result['page_number']}, Chunk {result['chunk_index']}, "
                  f"BM25 Score: {result['bm25_score']:.4f}")
    
    # 3. RRF FUSION ANALYSIS (20+20)
    print(f"\n{'-'*80}")
    print("RRF FUSION ANALYSIS (20+20 - current production)")
    print('-'*80)
    
    # Get hybrid results with full candidate pool visibility
    hybrid_results = await retrieval_service.retrieve_relevant_chunks(
        db=db,
        paper_id=PAPER_ID,
        question=question_text,
        top_k=100,  # Get all results to see full ranking
        mode=RetrievalMode.HYBRID,
        dense_k=20,
        lexical_k=20
    )
    
    print(f"\nTotal RRF candidates: {len(hybrid_results)}")
    print(f"\nTop-10 RRF Results:")
    for i in range(min(10, len(hybrid_results))):
        result = hybrid_results[i]
        marker = "★ RELEVANT" if result['page_number'] in relevant_pages else ""
        print(f"  {i+1}. Page {result['page_number']}, Chunk {result['chunk_index']}, "
              f"RRF Score: {result.get('rrf_score', 0):.6f}, "
              f"Dense: {result.get('dense_similarity', 'N/A')}, "
              f"BM25: {result.get('lexical_score', 'N/A')} {marker}")
    
    print(f"\nRelevant chunks in RRF results:")
    relevant_in_rrf = [r for r in hybrid_results if r['page_number'] in relevant_pages]
    if relevant_in_rrf:
        for i, result in enumerate(relevant_in_rrf):
            rrf_rank = hybrid_results.index(result) + 1
            print(f"  RRF Rank {rrf_rank}: Page {result['page_number']}, Chunk {result['chunk_index']}, "
                  f"RRF Score: {result.get('rrf_score', 0):.6f}")
            print(f"    Dense Similarity: {result.get('dense_similarity', 'N/A')}, Dense Rank: {result.get('dense_rank', 'N/A')}")
            print(f"    BM25 Score: {result.get('lexical_score', 'N/A')}, BM25 Rank: {result.get('lexical_rank', 'N/A')}")
    else:
        print(f"  ⚠️  NO RELEVANT CHUNKS IN RRF CANDIDATE POOL!")
    
    # 4. DIAGNOSTIC SUMMARY
    print(f"\n{'-'*80}")
    print("DIAGNOSTIC SUMMARY")
    print('-'*80)
    
    # Find best ranks for relevant chunks
    best_dense_rank = min([item['dense_rank'] for item in dense_scores if item['is_relevant']], default=None)
    best_bm25_rank = min([r['rank'] for r in bm25_results if r['page_number'] in relevant_pages], default=None)
    best_rrf_rank = min([hybrid_results.index(r)+1 for r in hybrid_results if r['page_number'] in relevant_pages], default=None)
    
    print(f"\nBest rank for relevant chunks:")
    print(f"  Dense: {best_dense_rank if best_dense_rank else 'NOT IN TOP-54'}")
    print(f"  BM25: {best_bm25_rank if best_bm25_rank else 'NOT IN TOP-54'}")
    print(f"  RRF: {best_rrf_rank if best_rrf_rank else 'NOT IN CANDIDATE POOL'}")
    print(f"  Final Top-10: {'YES' if best_rrf_rank and best_rrf_rank <= 10 else 'NO'}")
    
    # Determine failure mode
    print(f"\nFAILURE MODE DIAGNOSIS:")
    if best_dense_rank and best_dense_rank <= 20 and best_bm25_rank and best_bm25_rank <= 20:
        if best_rrf_rank and best_rrf_rank > 10:
            print(f"  → CASE D: Both retrievers rank relevant chunk in top-20, but RRF demotes it below top-10")
            print(f"     RRF may be over-weighting other chunks or fusion logic is suboptimal")
        else:
            print(f"  → CASE A: Dense and BM25 both retrieve relevant chunk, RRF successfully promotes it")
    elif best_dense_rank and best_dense_rank <= 20:
        print(f"  → CASE B: Dense ranks relevant chunk well (rank {best_dense_rank}), but BM25 ranks it poorly (rank {best_bm25_rank})")
        print(f"     BM25 may be dragging down the RRF score")
    elif best_bm25_rank and best_bm25_rank <= 20:
        print(f"  → CASE B (inverted): BM25 ranks relevant chunk well (rank {best_bm25_rank}), but Dense ranks it poorly (rank {best_dense_rank})")
        print(f"     Dense retrieval may be dragging down the RRF score")
    else:
        print(f"  → CASE C: Both Dense (rank {best_dense_rank}) and BM25 (rank {best_bm25_rank}) rank relevant chunk poorly")
        print(f"     Likely query-document semantic AND lexical mismatch")
    
    return {
        'question_id': question_id,
        'dense_scores': dense_scores,
        'bm25_results': bm25_results,
        'rrf_results': hybrid_results,
        'best_dense_rank': best_dense_rank,
        'best_bm25_rank': best_bm25_rank,
        'best_rrf_rank': best_rrf_rank
    }


async def main():
    """Run diagnostic analysis for q4 and q7."""
    db = SessionLocal()
    
    try:
        print("="*80)
        print("PHASE 8 RANKING DIAGNOSTIC")
        print("Analyzing why relevant chunks don't rank highly in final results")
        print("="*80)
        
        # Load dataset
        with open('evaluation/dataset.json', 'r') as f:
            dataset = json.load(f)
        
        # Analyze q4
        q4 = [q for q in dataset['questions'] if q['id'] == 'q4'][0]
        q4_results = await analyze_question_ranking(
            db=db,
            question_id='q4',
            question_text=q4['question'],
            relevant_pages=q4['relevant_pages']
        )
        
        # Analyze q7
        q7 = [q for q in dataset['questions'] if q['id'] == 'q7'][0]
        q7_results = await analyze_question_ranking(
            db=db,
            question_id='q7',
            question_text=q7['question'],
            relevant_pages=q7['relevant_pages']
        )
        
        # Summary
        print(f"\n\n{'='*80}")
        print("OVERALL DIAGNOSTIC SUMMARY")
        print('='*80)
        
        print(f"\nq4 (evaluation results/metrics):")
        print(f"  Best Dense Rank: {q4_results['best_dense_rank']}")
        print(f"  Best BM25 Rank: {q4_results['best_bm25_rank']}")
        print(f"  Best RRF Rank: {q4_results['best_rrf_rank']}")
        print(f"  In Final Top-10: {'YES' if q4_results['best_rrf_rank'] and q4_results['best_rrf_rank'] <= 10 else 'NO'}")
        
        print(f"\nq7 (CPU core restriction):")
        print(f"  Best Dense Rank: {q7_results['best_dense_rank']}")
        print(f"  Best BM25 Rank: {q7_results['best_bm25_rank']}")
        print(f"  Best RRF Rank: {q7_results['best_rrf_rank']}")
        print(f"  In Final Top-10: {'YES' if q7_results['best_rrf_rank'] and q7_results['best_rrf_rank'] <= 10 else 'NO'}")
        
        print("\n" + "="*80)
        
    finally:
        db.close()


if __name__ == '__main__':
    asyncio.run(main())
