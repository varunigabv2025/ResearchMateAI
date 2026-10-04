"""
RAG Evaluation Metrics

This module implements retrieval and answer evaluation metrics for the RAG system.
All metrics measure the EXISTING production pipeline without modification.

Metrics include:
- Retrieval: Hit Rate, Recall, Precision, MRR
- Answer: Deterministic keyword matching, faithfulness, citation accuracy
- Latency: Component-level and end-to-end timing

Mathematical definitions are documented for each metric.
"""
from typing import List, Dict, Set, Optional
import statistics


class RetrievalMetrics:
    """
    Metrics for evaluating retrieval quality.
    
    All metrics assume:
    - retrieved_chunks: List of chunk IDs or page numbers returned by retrieval
    - relevant_chunks: Ground truth relevant chunk IDs or page numbers
    - k: Number of top results to consider
    """
    
    @staticmethod
    def hit_rate_at_k(
        retrieved_pages: List[int],
        relevant_pages: List[int],
        k: int
    ) -> float:
        """
        Hit Rate@K: Fraction of queries where at least one relevant item appears in top-K.
        
        Mathematical definition:
            HR@K = (1 if |relevant ∩ top_k| > 0 else 0)
        
        For a set of queries:
            HR@K = (1/Q) * Σ(1 if query has hit else 0)
        
        Args:
            retrieved_pages: List of page numbers retrieved (in ranked order)
            relevant_pages: Ground truth relevant page numbers
            k: Number of top results to consider
            
        Returns:
            1.0 if at least one relevant page in top-k, 0.0 otherwise
        """
        if not relevant_pages:
            return 0.0
        
        # Get top-k retrieved pages
        top_k = retrieved_pages[:k] if len(retrieved_pages) >= k else retrieved_pages
        
        # Check if any relevant page appears in top-k
        relevant_set = set(relevant_pages)
        top_k_set = set(top_k)
        
        return 1.0 if len(relevant_set & top_k_set) > 0 else 0.0
    
    @staticmethod
    def recall_at_k(
        retrieved_pages: List[int],
        relevant_pages: List[int],
        k: int
    ) -> float:
        """
        Recall@K: Fraction of relevant items that appear in top-K results.
        
        Mathematical definition:
            Recall@K = |relevant ∩ top_k| / |relevant|
        
        Args:
            retrieved_pages: List of page numbers retrieved (in ranked order)
            relevant_pages: Ground truth relevant page numbers
            k: Number of top results to consider
            
        Returns:
            Recall score between 0.0 and 1.0
        """
        if not relevant_pages:
            return 0.0
        
        # Get top-k retrieved pages
        top_k = retrieved_pages[:k] if len(retrieved_pages) >= k else retrieved_pages
        
        # Calculate recall
        relevant_set = set(relevant_pages)
        top_k_set = set(top_k)
        
        hits = len(relevant_set & top_k_set)
        return hits / len(relevant_set)
    
    @staticmethod
    def precision_at_k(
        retrieved_pages: List[int],
        relevant_pages: List[int],
        k: int
    ) -> float:
        """
        Precision@K: Fraction of top-K results that are relevant.
        
        Mathematical definition:
            Precision@K = |relevant ∩ top_k| / K
        
        Args:
            retrieved_pages: List of page numbers retrieved (in ranked order)
            relevant_pages: Ground truth relevant page numbers
            k: Number of top results to consider
            
        Returns:
            Precision score between 0.0 and 1.0
        """
        if not relevant_pages:
            return 0.0
        
        # Get top-k retrieved pages
        top_k = retrieved_pages[:k] if len(retrieved_pages) >= k else retrieved_pages
        
        if not top_k:
            return 0.0
        
        # Calculate precision
        relevant_set = set(relevant_pages)
        top_k_set = set(top_k)
        
        hits = len(relevant_set & top_k_set)
        return hits / len(top_k)
    
    @staticmethod
    def mean_reciprocal_rank(
        retrieved_pages: List[int],
        relevant_pages: List[int]
    ) -> float:
        """
        Mean Reciprocal Rank: Reciprocal of the rank of the first relevant item.
        
        Mathematical definition:
            MRR = 1 / rank_of_first_relevant_item
        
        For a set of queries:
            MRR = (1/Q) * Σ(1 / rank_i)
        
        where rank_i is the position of the first relevant item for query i.
        If no relevant item is found, contributes 0 to the sum.
        
        Args:
            retrieved_pages: List of page numbers retrieved (in ranked order)
            relevant_pages: Ground truth relevant page numbers
            
        Returns:
            MRR score between 0.0 and 1.0
        """
        if not relevant_pages or not retrieved_pages:
            return 0.0
        
        relevant_set = set(relevant_pages)
        
        # Find rank of first relevant item (1-indexed)
        for rank, page in enumerate(retrieved_pages, start=1):
            if page in relevant_set:
                return 1.0 / rank
        
        # No relevant item found
        return 0.0


class AnswerMetrics:
    """
    Metrics for evaluating answer quality.
    
    IMPORTANT: expected_answer_contains is a lightweight deterministic signal,
    NOT a measure of semantic answer correctness.
    """
    
    @staticmethod
    def keyword_match_score(
        answer: str,
        expected_keywords: List[str]
    ) -> Dict[str, any]:
        """
        Deterministic keyword matching (NOT semantic correctness).
        
        This is a lightweight signal indicating whether the answer contains
        expected terminology. It does NOT evaluate whether the answer is
        semantically correct or complete.
        
        Args:
            answer: Generated answer text
            expected_keywords: List of expected keywords/phrases
            
        Returns:
            Dictionary with:
            - matched_keywords: List of keywords found
            - missed_keywords: List of keywords not found
            - match_rate: Fraction of keywords found
            - all_matched: Boolean indicating complete match
        """
        answer_lower = answer.lower()
        
        matched = []
        missed = []
        
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                matched.append(keyword)
            else:
                missed.append(keyword)
        
        match_rate = len(matched) / len(expected_keywords) if expected_keywords else 0.0
        
        return {
            'matched_keywords': matched,
            'missed_keywords': missed,
            'match_rate': match_rate,
            'all_matched': len(missed) == 0
        }
    
    @staticmethod
    def check_faithfulness(
        answer: str,
        retrieved_contexts: List[str]
    ) -> Dict[str, any]:
        """
        Check if answer appears grounded in retrieved context.
        
        This is a simple heuristic check, NOT a comprehensive faithfulness measure.
        Looks for direct phrase overlap between answer and context.
        
        Args:
            answer: Generated answer text
            retrieved_contexts: List of retrieved chunk texts
            
        Returns:
            Dictionary with:
            - has_overlap: Boolean indicating phrase overlap detected
            - overlap_ratio: Approximate ratio of answer content in context
        """
        if not retrieved_contexts:
            return {
                'has_overlap': False,
                'overlap_ratio': 0.0
            }
        
        # Combine all contexts
        combined_context = ' '.join(retrieved_contexts).lower()
        
        # Split answer into phrases (simple word-based)
        answer_words = answer.lower().split()
        
        if not answer_words:
            return {
                'has_overlap': False,
                'overlap_ratio': 0.0
            }
        
        # Count words from answer that appear in context
        overlap_count = sum(1 for word in answer_words if word in combined_context)
        overlap_ratio = overlap_count / len(answer_words)
        
        return {
            'has_overlap': overlap_ratio > 0.3,  # Heuristic threshold
            'overlap_ratio': overlap_ratio
        }
    
    @staticmethod
    def check_unanswerable_handling(
        answer: str,
        has_sufficient_context: bool
    ) -> Dict[str, any]:
        """
        Check if system appropriately indicates insufficient information.
        
        For unanswerable questions, the system should indicate it cannot
        answer rather than hallucinating.
        
        Args:
            answer: Generated answer text
            has_sufficient_context: Flag from Q&A system
            
        Returns:
            Dictionary with:
            - indicated_insufficient: Boolean
            - has_refusal_signal: Boolean (detected refusal phrases)
        """
        refusal_signals = [
            'insufficient',
            'not found',
            'cannot answer',
            'does not',
            'not mentioned',
            'not provided',
            'no information',
            'unable to answer'
        ]
        
        answer_lower = answer.lower()
        has_refusal = any(signal in answer_lower for signal in refusal_signals)
        
        return {
            'indicated_insufficient': not has_sufficient_context,
            'has_refusal_signal': has_refusal
        }


class CitationMetrics:
    """
    Metrics for evaluating citation accuracy.
    
    Uses EXISTING citation metadata from the Q&A system:
    - page_number
    - section
    - chunk_id
    - similarity score
    """
    
    @staticmethod
    def citation_page_accuracy(
        cited_pages: List[int],
        relevant_pages: List[int]
    ) -> Dict[str, any]:
        """
        Check if cited pages match ground truth relevant pages.
        
        Args:
            cited_pages: Page numbers cited in the answer
            relevant_pages: Ground truth relevant page numbers
            
        Returns:
            Dictionary with:
            - precision: Fraction of citations that are relevant
            - recall: Fraction of relevant pages that were cited
            - cited_count: Number of pages cited
            - relevant_count: Number of relevant pages
        """
        if not cited_pages:
            return {
                'precision': 0.0,
                'recall': 0.0,
                'cited_count': 0,
                'relevant_count': len(relevant_pages)
            }
        
        cited_set = set(cited_pages)
        relevant_set = set(relevant_pages)
        
        correct_citations = len(cited_set & relevant_set)
        
        precision = correct_citations / len(cited_set) if cited_set else 0.0
        recall = correct_citations / len(relevant_set) if relevant_set else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'cited_count': len(cited_set),
            'relevant_count': len(relevant_set)
        }


class LatencyMetrics:
    """
    Metrics for measuring system latency.
    
    Tracks latency at different stages:
    - Query embedding generation
    - Vector retrieval
    - LLM answer generation
    - End-to-end request
    """
    
    @staticmethod
    def compute_statistics(latencies: List[float]) -> Dict[str, float]:
        """
        Compute latency statistics.
        
        Args:
            latencies: List of latency measurements in seconds
            
        Returns:
            Dictionary with mean, median, min, max, std_dev
        """
        if not latencies:
            return {
                'mean': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std_dev': 0.0,
                'count': 0
            }
        
        return {
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'min': min(latencies),
            'max': max(latencies),
            'std_dev': statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
            'count': len(latencies)
        }


def aggregate_retrieval_metrics(
    per_question_results: List[Dict]
) -> Dict[str, float]:
    """
    Aggregate retrieval metrics across all questions.
    
    Args:
        per_question_results: List of per-question evaluation results
        
    Returns:
        Dictionary with averaged metrics
    """
    if not per_question_results:
        return {}
    
    # Extract retrieval metrics from answerable questions
    answerable_results = [
        r for r in per_question_results
        if r.get('answerable', True)
    ]
    
    if not answerable_results:
        return {}
    
    metrics = {
        'hit_rate_at_1': [],
        'hit_rate_at_3': [],
        'hit_rate_at_5': [],
        'hit_rate_at_10': [],
        'recall_at_1': [],
        'recall_at_3': [],
        'recall_at_5': [],
        'recall_at_10': [],
        'precision_at_1': [],
        'precision_at_3': [],
        'precision_at_5': [],
        'precision_at_10': [],
        'mrr': []
    }
    
    for result in answerable_results:
        ret_metrics = result.get('retrieval_metrics', {})
        for key in metrics.keys():
            if key in ret_metrics:
                metrics[key].append(ret_metrics[key])
    
    # Compute averages
    return {
        key: statistics.mean(values) if values else 0.0
        for key, values in metrics.items()
    }


def aggregate_answer_metrics(
    per_question_results: List[Dict]
) -> Dict[str, any]:
    """
    Aggregate answer quality metrics across all questions.
    
    Args:
        per_question_results: List of per-question evaluation results
        
    Returns:
        Dictionary with aggregated answer metrics
    """
    if not per_question_results:
        return {}
    
    keyword_match_rates = []
    faithfulness_ratios = []
    
    for result in per_question_results:
        ans_metrics = result.get('answer_metrics', {})
        
        if 'keyword_match' in ans_metrics:
            keyword_match_rates.append(ans_metrics['keyword_match']['match_rate'])
        
        if 'faithfulness' in ans_metrics:
            faithfulness_ratios.append(ans_metrics['faithfulness']['overlap_ratio'])
    
    return {
        'avg_keyword_match_rate': statistics.mean(keyword_match_rates) if keyword_match_rates else 0.0,
        'avg_faithfulness_ratio': statistics.mean(faithfulness_ratios) if faithfulness_ratios else 0.0,
        'questions_evaluated': len(per_question_results)
    }


def aggregate_citation_metrics(
    per_question_results: List[Dict]
) -> Dict[str, float]:
    """
    Aggregate citation accuracy metrics.
    
    Args:
        per_question_results: List of per-question evaluation results
        
    Returns:
        Dictionary with averaged citation metrics
    """
    if not per_question_results:
        return {}
    
    precisions = []
    recalls = []
    
    for result in per_question_results:
        cit_metrics = result.get('citation_metrics', {})
        if 'precision' in cit_metrics:
            precisions.append(cit_metrics['precision'])
        if 'recall' in cit_metrics:
            recalls.append(cit_metrics['recall'])
    
    return {
        'avg_citation_precision': statistics.mean(precisions) if precisions else 0.0,
        'avg_citation_recall': statistics.mean(recalls) if recalls else 0.0
    }
