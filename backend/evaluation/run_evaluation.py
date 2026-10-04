"""
RAG Evaluation Runner

This module runs evaluation against the EXISTING production RAG pipeline.
It does NOT modify embeddings, retrieval, chunking, or LLM configuration.

The evaluation:
1. Loads ground truth dataset
2. Calls existing retrieval_service and Q&A API
3. Measures retrieval quality, answer quality, citations, and latency
4. Generates baseline.json with detailed results
"""
import asyncio
import json
import time
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import existing services (DO NOT DUPLICATE LOGIC)
from app.core.database import SessionLocal
from app.models import Paper, PaperChunk
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.services.prompts import GroundedQAPrompt

# Import evaluation metrics
from evaluation.metrics import (
    RetrievalMetrics,
    AnswerMetrics,
    CitationMetrics,
    LatencyMetrics,
    aggregate_retrieval_metrics,
    aggregate_answer_metrics,
    aggregate_citation_metrics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """
    Evaluates the existing RAG pipeline without modification.
    """
    
    def __init__(self, dataset_path: str):
        """
        Initialize evaluator with dataset.
        
        Args:
            dataset_path: Path to evaluation dataset JSON
        """
        self.dataset_path = Path(dataset_path)
        self.dataset = self._load_dataset()
        
    def _load_dataset(self) -> Dict:
        """Load evaluation dataset from JSON."""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def evaluate_question(
        self,
        db,
        paper_id: UUID,
        question_data: Dict
    ) -> Dict:
        """
        Evaluate a single question using the EXISTING RAG pipeline.
        
        Args:
            db: Database session
            paper_id: UUID of the paper
            question_data: Question data from dataset
            
        Returns:
            Dictionary with evaluation results
        """
        question_id = question_data['id']
        question = question_data['question']
        expected_keywords = question_data.get('expected_answer_contains', [])
        relevant_pages = question_data.get('relevant_pages', [])
        answerable = question_data.get('answerable', True)
        
        logger.info(f"Evaluating {question_id}: {question[:50]}...")
        
        result = {
            'question_id': question_id,
            'question': question,
            'answerable': answerable,
            'category': question_data.get('category', 'unknown'),
            'error': None
        }
        
        try:
            # ===== RETRIEVAL PHASE =====
            retrieval_start = time.time()
            
            # Call EXISTING retrieval service
            retrieved_chunks = await retrieval_service.retrieve_relevant_chunks(
                db=db,
                paper_id=paper_id,
                question=question,
                top_k=10,  # Retrieve more for evaluation (measure @1,3,5,10)
                similarity_threshold=0.4
            )
            
            retrieval_latency = time.time() - retrieval_start
            
            # Extract retrieved pages
            retrieved_pages = [chunk['page_number'] for chunk in retrieved_chunks]
            
            # Compute retrieval metrics (if answerable)
            retrieval_metrics = {}
            if answerable and relevant_pages:
                retrieval_metrics = {
                    'hit_rate_at_1': RetrievalMetrics.hit_rate_at_k(retrieved_pages, relevant_pages, 1),
                    'hit_rate_at_3': RetrievalMetrics.hit_rate_at_k(retrieved_pages, relevant_pages, 3),
                    'hit_rate_at_5': RetrievalMetrics.hit_rate_at_k(retrieved_pages, relevant_pages, 5),
                    'hit_rate_at_10': RetrievalMetrics.hit_rate_at_k(retrieved_pages, relevant_pages, 10),
                    'recall_at_1': RetrievalMetrics.recall_at_k(retrieved_pages, relevant_pages, 1),
                    'recall_at_3': RetrievalMetrics.recall_at_k(retrieved_pages, relevant_pages, 3),
                    'recall_at_5': RetrievalMetrics.recall_at_k(retrieved_pages, relevant_pages, 5),
                    'recall_at_10': RetrievalMetrics.recall_at_k(retrieved_pages, relevant_pages, 10),
                    'precision_at_1': RetrievalMetrics.precision_at_k(retrieved_pages, relevant_pages, 1),
                    'precision_at_3': RetrievalMetrics.precision_at_k(retrieved_pages, relevant_pages, 3),
                    'precision_at_5': RetrievalMetrics.precision_at_k(retrieved_pages, relevant_pages, 5),
                    'precision_at_10': RetrievalMetrics.precision_at_k(retrieved_pages, relevant_pages, 10),
                    'mrr': RetrievalMetrics.mean_reciprocal_rank(retrieved_pages, relevant_pages)
                }
            
            result['retrieval_metrics'] = retrieval_metrics
            result['retrieved_pages'] = retrieved_pages
            result['retrieved_chunk_count'] = len(retrieved_chunks)
            
            # ===== ANSWER GENERATION PHASE =====
            
            # Use top-5 chunks for answer generation (production config)
            top_5_chunks = retrieved_chunks[:5]
            
            # Check sufficient context (using EXISTING logic)
            has_sufficient_context = GroundedQAPrompt.has_sufficient_context(
                top_5_chunks, min_chunks=1
            )
            
            if not has_sufficient_context:
                answer = GroundedQAPrompt.get_insufficient_context_response()
                llm_latency = 0.0
            else:
                # Build prompt using EXISTING prompt builder
                messages = GroundedQAPrompt.build_messages(question, top_5_chunks)
                
                # Call EXISTING LLM service
                llm_start = time.time()
                try:
                    answer = await llm_service.generate_chat_completion(messages)
                    llm_latency = time.time() - llm_start
                except Exception as llm_error:
                    logger.error(f"LLM error for {question_id}: {llm_error}")
                    answer = f"[LLM ERROR: {str(llm_error)}]"
                    llm_latency = 0.0
                    result['error'] = f"LLM generation failed: {str(llm_error)}"
            
            result['answer'] = answer
            result['has_sufficient_context'] = has_sufficient_context
            
            # ===== ANSWER EVALUATION =====
            answer_metrics = {}
            
            # Deterministic keyword matching (NOT semantic correctness)
            if expected_keywords:
                answer_metrics['keyword_match'] = AnswerMetrics.keyword_match_score(
                    answer, expected_keywords
                )
            
            # Faithfulness check (simple heuristic)
            retrieved_texts = [chunk['text'] for chunk in top_5_chunks]
            answer_metrics['faithfulness'] = AnswerMetrics.check_faithfulness(
                answer, retrieved_texts
            )
            
            # Unanswerable handling
            answer_metrics['unanswerable_handling'] = AnswerMetrics.check_unanswerable_handling(
                answer, has_sufficient_context
            )
            
            result['answer_metrics'] = answer_metrics
            
            # ===== CITATION EVALUATION =====
            cited_pages = [chunk['page_number'] for chunk in top_5_chunks]
            
            citation_metrics = {}
            if answerable and relevant_pages:
                citation_metrics = CitationMetrics.citation_page_accuracy(
                    cited_pages, relevant_pages
                )
            
            result['citation_metrics'] = citation_metrics
            result['cited_pages'] = cited_pages
            
            # ===== LATENCY METRICS =====
            total_latency = retrieval_latency + llm_latency
            
            result['latency'] = {
                'retrieval_seconds': retrieval_latency,
                'llm_seconds': llm_latency,
                'total_seconds': total_latency
            }
            
            logger.info(
                f"✓ {question_id}: "
                f"retrieved={len(retrieved_chunks)}, "
                f"latency={total_latency:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Evaluation failed for {question_id}: {e}")
            result['error'] = str(e)
        
        return result
    
    async def run_evaluation(self, paper_id: str) -> Dict:
        """
        Run full evaluation on all questions in the dataset.
        
        Args:
            paper_id: UUID string of the paper to evaluate
            
        Returns:
            Complete evaluation results
        """
        logger.info("="*60)
        logger.info("STARTING RAG BASELINE EVALUATION")
        logger.info("="*60)
        
        eval_start = time.time()
        
        # Convert paper_id to UUID
        paper_uuid = UUID(paper_id)
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Verify paper exists and is processed
            paper = db.query(Paper).filter(Paper.id == paper_uuid).first()
            if not paper:
                raise ValueError(f"Paper with id {paper_id} not found")
            
            if not paper.processed:
                raise ValueError(f"Paper {paper_id} is not fully processed")
            
            logger.info(f"Evaluating paper: {paper.filename}")
            logger.info(f"Questions in dataset: {len(self.dataset['questions'])}")
            
            # Evaluate each question
            per_question_results = []
            
            for question_data in self.dataset['questions']:
                result = await self.evaluate_question(db, paper_uuid, question_data)
                per_question_results.append(result)
                
                # Small delay to avoid overwhelming free-tier LLM
                await asyncio.sleep(1)
            
            eval_duration = time.time() - eval_start
            
            # ===== AGGREGATE METRICS =====
            
            # Retrieval metrics
            aggregated_retrieval = aggregate_retrieval_metrics(per_question_results)
            
            # Answer metrics
            aggregated_answer = aggregate_answer_metrics(per_question_results)
            
            # Citation metrics
            aggregated_citation = aggregate_citation_metrics(per_question_results)
            
            # Latency metrics
            retrieval_latencies = [
                r['latency']['retrieval_seconds']
                for r in per_question_results
                if 'latency' in r and not r.get('error')
            ]
            llm_latencies = [
                r['latency']['llm_seconds']
                for r in per_question_results
                if 'latency' in r and not r.get('error') and r['latency']['llm_seconds'] > 0
            ]
            total_latencies = [
                r['latency']['total_seconds']
                for r in per_question_results
                if 'latency' in r and not r.get('error')
            ]
            
            latency_metrics = {
                'retrieval': LatencyMetrics.compute_statistics(retrieval_latencies),
                'llm': LatencyMetrics.compute_statistics(llm_latencies),
                'end_to_end': LatencyMetrics.compute_statistics(total_latencies)
            }
            
            # ===== COMPILE RESULTS =====
            
            errors = [
                {
                    'question_id': r['question_id'],
                    'error': r['error']
                }
                for r in per_question_results
                if r.get('error')
            ]
            
            # Detect actual database and retrieval method used
            from app.services.retrieval_service import HAS_PGVECTOR
            from app.core.config import settings
            
            if HAS_PGVECTOR:
                retrieval_method = 'pgvector_cosine'
                database_info = 'PostgreSQL + pgvector'
            else:
                retrieval_method = 'python_numpy_cosine_fallback'
                # Extract database type from connection string
                db_url = settings.DATABASE_URL
                if 'sqlite' in db_url.lower():
                    database_info = f'SQLite ({db_url.split("///")[-1] if ":///" in db_url else "in-memory"})'
                elif 'postgresql' in db_url.lower():
                    database_info = 'PostgreSQL (without pgvector extension)'
                else:
                    database_info = db_url.split(':')[0] if ':' in db_url else 'unknown'
            
            results = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'evaluation_duration_seconds': eval_duration,
                'paper': {
                    'id': str(paper.id),
                    'filename': paper.filename,
                    'original_filename': paper.original_filename,
                    'page_count': paper.page_count
                },
                'dataset': {
                    'name': self.dataset.get('dataset_name'),
                    'description': self.dataset.get('description'),
                    'question_count': len(self.dataset['questions'])
                },
                'rag_config': {
                    'embedding_model': 'Qwen3-Embedding-0.6B',
                    'embedding_dimension': 1024,
                    'chunking': {
                        'chunk_size': 1000,
                        'overlap': 200
                    },
                    'retrieval': {
                        'method': retrieval_method,
                        'top_k': 5,
                        'similarity_threshold': 0.4
                    },
                    'llm_model': 'nvidia/nemotron-3-ultra-550b-a55b:free',
                    'llm_provider': 'OpenRouter',
                    'database': database_info
                },
                'retrieval_metrics': aggregated_retrieval,
                'answer_metrics': aggregated_answer,
                'citation_metrics': aggregated_citation,
                'latency_metrics': latency_metrics,
                'per_question_results': per_question_results,
                'errors': errors,
                'notes': [
                    'This is a baseline evaluation of the existing RAG pipeline',
                    'Dataset is limited to 10 questions on a single paper',
                    'Keyword matching is a lightweight signal, NOT semantic correctness',
                    'LLM latency may be variable due to free-tier OpenRouter model',
                    'Evaluation measures production pipeline without modifications'
                ]
            }
            
            logger.info("="*60)
            logger.info("EVALUATION COMPLETE")
            logger.info(f"Duration: {eval_duration:.2f}s")
            logger.info(f"Questions evaluated: {len(per_question_results)}")
            logger.info(f"Errors: {len(errors)}")
            logger.info("="*60)
            
            return results
            
        finally:
            db.close()
    
    def save_results(self, results: Dict, output_path: str):
        """
        Save evaluation results to JSON file.
        
        Args:
            results: Evaluation results dictionary
            output_path: Path to output JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_file}")


async def main():
    """
    Main entry point for running evaluation.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Run RAG evaluation on existing pipeline')
    parser.add_argument(
        '--paper-id',
        required=True,
        help='UUID of the paper to evaluate'
    )
    parser.add_argument(
        '--dataset',
        default='backend/evaluation/dataset.json',
        help='Path to evaluation dataset JSON'
    )
    parser.add_argument(
        '--output',
        default='backend/evaluation/results/baseline.json',
        help='Path to output results JSON'
    )
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = RAGEvaluator(args.dataset)
    
    # Run evaluation
    results = await evaluator.run_evaluation(args.paper_id)
    
    # Save results
    evaluator.save_results(results, args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Questions: {results['dataset']['question_count']}")
    print(f"Errors: {len(results['errors'])}")
    print("\nRetrieval Metrics:")
    for key, value in results['retrieval_metrics'].items():
        print(f"  {key}: {value:.3f}")
    print("\nAnswer Metrics:")
    for key, value in results['answer_metrics'].items():
        print(f"  {key}: {value:.3f}")
    print("\nCitation Metrics:")
    for key, value in results['citation_metrics'].items():
        print(f"  {key}: {value:.3f}")
    print("\nLatency (seconds):")
    print(f"  Retrieval: {results['latency_metrics']['retrieval']['mean']:.3f} ± {results['latency_metrics']['retrieval']['std_dev']:.3f}")
    print(f"  LLM: {results['latency_metrics']['llm']['mean']:.3f} ± {results['latency_metrics']['llm']['std_dev']:.3f}")
    print(f"  End-to-end: {results['latency_metrics']['end_to_end']['mean']:.3f} ± {results['latency_metrics']['end_to_end']['std_dev']:.3f}")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
