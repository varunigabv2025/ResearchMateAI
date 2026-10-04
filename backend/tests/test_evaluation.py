"""
Tests for RAG evaluation metrics.

This test suite validates the mathematical correctness of evaluation metrics
including Hit Rate, Recall, Precision, MRR, and answer quality metrics.
"""
import pytest
from evaluation.metrics import (
    RetrievalMetrics,
    AnswerMetrics,
    CitationMetrics,
    LatencyMetrics,
    aggregate_retrieval_metrics,
    aggregate_answer_metrics,
    aggregate_citation_metrics
)


class TestRetrievalMetrics:
    """Test retrieval quality metrics."""
    
    def test_hit_rate_at_k_basic(self):
        """Test basic hit rate calculation."""
        retrieved = [1, 2, 3, 4, 5]
        relevant = [3, 6, 7]
        
        # Hit at position 3
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 1) == 0.0
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 3) == 1.0
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 5) == 1.0
    
    def test_hit_rate_at_k_no_hit(self):
        """Test hit rate when no relevant items retrieved."""
        retrieved = [1, 2, 3]
        relevant = [4, 5, 6]
        
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 1) == 0.0
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 5) == 0.0
    
    def test_hit_rate_at_k_empty_relevant(self):
        """Test hit rate with empty relevant set."""
        retrieved = [1, 2, 3]
        relevant = []
        
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 3) == 0.0
    
    def test_hit_rate_k_exceeds_retrieved(self):
        """Test hit rate when K > retrieved count."""
        retrieved = [1, 2]
        relevant = [2, 3]
        
        # Should still work with available items
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 10) == 1.0
    
    def test_recall_at_k_basic(self):
        """Test basic recall calculation."""
        retrieved = [1, 2, 3, 4, 5]
        relevant = [2, 3, 6]
        
        # 2 of 3 relevant items in top-5
        assert RetrievalMetrics.recall_at_k(retrieved, relevant, 5) == pytest.approx(2/3)
        
        # 1 of 3 relevant items in top-2
        assert RetrievalMetrics.recall_at_k(retrieved, relevant, 2) == pytest.approx(1/3)
    
    def test_recall_at_k_perfect(self):
        """Test recall when all relevant items retrieved."""
        retrieved = [1, 2, 3, 4]
        relevant = [1, 3]
        
        assert RetrievalMetrics.recall_at_k(retrieved, relevant, 4) == 1.0
    
    def test_recall_at_k_zero(self):
        """Test recall when no relevant items retrieved."""
        retrieved = [1, 2, 3]
        relevant = [4, 5, 6]
        
        assert RetrievalMetrics.recall_at_k(retrieved, relevant, 3) == 0.0
    
    def test_recall_at_k_empty_relevant(self):
        """Test recall with empty relevant set."""
        retrieved = [1, 2, 3]
        relevant = []
        
        assert RetrievalMetrics.recall_at_k(retrieved, relevant, 3) == 0.0
    
    def test_precision_at_k_basic(self):
        """Test basic precision calculation."""
        retrieved = [1, 2, 3, 4, 5]
        relevant = [2, 3, 6]
        
        # 2 relevant in top-5
        assert RetrievalMetrics.precision_at_k(retrieved, relevant, 5) == pytest.approx(2/5)
        
        # 1 relevant in top-2
        assert RetrievalMetrics.precision_at_k(retrieved, relevant, 2) == pytest.approx(1/2)
    
    def test_precision_at_k_perfect(self):
        """Test precision when all retrieved are relevant."""
        retrieved = [1, 2, 3]
        relevant = [1, 2, 3, 4, 5]
        
        assert RetrievalMetrics.precision_at_k(retrieved, relevant, 3) == 1.0
    
    def test_precision_at_k_zero(self):
        """Test precision when no relevant items retrieved."""
        retrieved = [1, 2, 3]
        relevant = [4, 5, 6]
        
        assert RetrievalMetrics.precision_at_k(retrieved, relevant, 3) == 0.0
    
    def test_precision_at_k_empty_retrieved(self):
        """Test precision with empty retrieved set."""
        retrieved = []
        relevant = [1, 2, 3]
        
        assert RetrievalMetrics.precision_at_k(retrieved, relevant, 3) == 0.0
    
    def test_mrr_basic(self):
        """Test basic MRR calculation."""
        retrieved = [1, 2, 3, 4, 5]
        relevant = [3, 6]
        
        # First relevant at position 3 (1-indexed)
        assert RetrievalMetrics.mean_reciprocal_rank(retrieved, relevant) == pytest.approx(1/3)
    
    def test_mrr_first_position(self):
        """Test MRR when relevant item is first."""
        retrieved = [5, 2, 3, 4]
        relevant = [5, 10]
        
        assert RetrievalMetrics.mean_reciprocal_rank(retrieved, relevant) == 1.0
    
    def test_mrr_no_relevant(self):
        """Test MRR when no relevant items retrieved."""
        retrieved = [1, 2, 3]
        relevant = [4, 5, 6]
        
        assert RetrievalMetrics.mean_reciprocal_rank(retrieved, relevant) == 0.0
    
    def test_mrr_empty_retrieved(self):
        """Test MRR with empty retrieved list."""
        retrieved = []
        relevant = [1, 2, 3]
        
        assert RetrievalMetrics.mean_reciprocal_rank(retrieved, relevant) == 0.0
    
    def test_mrr_empty_relevant(self):
        """Test MRR with empty relevant list."""
        retrieved = [1, 2, 3]
        relevant = []
        
        assert RetrievalMetrics.mean_reciprocal_rank(retrieved, relevant) == 0.0
    
    def test_multiple_relevant_chunks_same_page(self):
        """Test handling of multiple chunks from same page."""
        # Simulate duplicate page numbers (common in real retrieval)
        retrieved = [1, 1, 2, 3, 3]
        relevant = [1, 2]
        
        # Set conversion should handle duplicates
        assert RetrievalMetrics.hit_rate_at_k(retrieved, relevant, 3) == 1.0
        assert RetrievalMetrics.recall_at_k(retrieved, relevant, 5) == 1.0


class TestAnswerMetrics:
    """Test answer quality metrics."""
    
    def test_keyword_match_all_matched(self):
        """Test keyword matching when all keywords present."""
        answer = "The CFS scheduling policy handles latency-sensitive workloads on edge hardware."
        keywords = ["CFS scheduling", "latency-sensitive", "edge hardware"]
        
        result = AnswerMetrics.keyword_match_score(answer, keywords)
        
        assert result['match_rate'] == 1.0
        assert result['all_matched'] is True
        assert len(result['matched_keywords']) == 3
        assert len(result['missed_keywords']) == 0
    
    def test_keyword_match_partial(self):
        """Test keyword matching with partial matches."""
        answer = "The system uses CFS scheduling for edge hardware."
        keywords = ["CFS scheduling", "latency-sensitive", "fairness bound"]
        
        result = AnswerMetrics.keyword_match_score(answer, keywords)
        
        assert result['match_rate'] == pytest.approx(1/3)
        assert result['all_matched'] is False
        assert "CFS scheduling" in result['matched_keywords']
        assert "latency-sensitive" in result['missed_keywords']
    
    def test_keyword_match_case_insensitive(self):
        """Test that keyword matching is case-insensitive."""
        answer = "The CFS SCHEDULING policy is used."
        keywords = ["cfs scheduling"]
        
        result = AnswerMetrics.keyword_match_score(answer, keywords)
        
        assert result['match_rate'] == 1.0
    
    def test_keyword_match_empty_keywords(self):
        """Test keyword matching with empty keyword list."""
        answer = "Some answer text"
        keywords = []
        
        result = AnswerMetrics.keyword_match_score(answer, keywords)
        
        assert result['match_rate'] == 0.0
    
    def test_faithfulness_high_overlap(self):
        """Test faithfulness with high context overlap."""
        answer = "The system uses containerised Linux edge nodes with CFS scheduling."
        contexts = [
            "PA-EIS targets containerised Linux edge nodes.",
            "The default CFS scheduling policy is used."
        ]
        
        result = AnswerMetrics.check_faithfulness(answer, contexts)
        
        assert result['has_overlap'] is True
        assert result['overlap_ratio'] > 0.5
    
    def test_faithfulness_low_overlap(self):
        """Test faithfulness with low context overlap."""
        answer = "Quantum computing revolutionizes machine learning algorithms."
        contexts = [
            "PA-EIS targets containerised Linux edge nodes.",
            "The system uses cgroup weights for scheduling."
        ]
        
        result = AnswerMetrics.check_faithfulness(answer, contexts)
        
        # Likely to have low overlap
        assert result['overlap_ratio'] < 0.5
    
    def test_faithfulness_empty_context(self):
        """Test faithfulness with empty context."""
        answer = "Some answer text"
        contexts = []
        
        result = AnswerMetrics.check_faithfulness(answer, contexts)
        
        assert result['has_overlap'] is False
        assert result['overlap_ratio'] == 0.0
    
    def test_faithfulness_empty_answer(self):
        """Test faithfulness with empty answer."""
        answer = ""
        contexts = ["Some context"]
        
        result = AnswerMetrics.check_faithfulness(answer, contexts)
        
        assert result['has_overlap'] is False
        assert result['overlap_ratio'] == 0.0
    
    def test_unanswerable_handling_insufficient_context(self):
        """Test detection of insufficient context indication."""
        answer = "I cannot answer this question based on the provided information."
        has_sufficient_context = False
        
        result = AnswerMetrics.check_unanswerable_handling(answer, has_sufficient_context)
        
        assert result['indicated_insufficient'] is True
        assert result['has_refusal_signal'] is True
    
    def test_unanswerable_handling_various_refusal_signals(self):
        """Test detection of various refusal phrases."""
        refusal_phrases = [
            "The information is insufficient.",
            "This is not found in the document.",
            "I cannot answer based on the available text.",
            "The paper does not mention this topic.",
            "No information is provided about this.",
            "I am unable to answer this question."
        ]
        
        for phrase in refusal_phrases:
            result = AnswerMetrics.check_unanswerable_handling(phrase, False)
            assert result['has_refusal_signal'] is True, f"Failed to detect refusal in: {phrase}"
    
    def test_unanswerable_handling_no_refusal(self):
        """Test that normal answers don't trigger refusal detection."""
        answer = "The system uses CFS scheduling for containerised workloads."
        has_sufficient_context = True
        
        result = AnswerMetrics.check_unanswerable_handling(answer, has_sufficient_context)
        
        assert result['indicated_insufficient'] is False
        assert result['has_refusal_signal'] is False


class TestCitationMetrics:
    """Test citation accuracy metrics."""
    
    def test_citation_accuracy_perfect(self):
        """Test citation accuracy with perfect matches."""
        cited_pages = [1, 2, 3]
        relevant_pages = [1, 2, 3]
        
        result = CitationMetrics.citation_page_accuracy(cited_pages, relevant_pages)
        
        assert result['precision'] == 1.0
        assert result['recall'] == 1.0
        assert result['cited_count'] == 3
        assert result['relevant_count'] == 3
    
    def test_citation_accuracy_partial(self):
        """Test citation accuracy with partial overlap."""
        cited_pages = [1, 2, 5, 6]
        relevant_pages = [2, 3, 4]
        
        result = CitationMetrics.citation_page_accuracy(cited_pages, relevant_pages)
        
        # 1 correct citation (page 2) out of 4 cited
        assert result['precision'] == pytest.approx(1/4)
        # 1 correct citation (page 2) out of 3 relevant
        assert result['recall'] == pytest.approx(1/3)
    
    def test_citation_accuracy_no_overlap(self):
        """Test citation accuracy with no overlap."""
        cited_pages = [1, 2, 3]
        relevant_pages = [4, 5, 6]
        
        result = CitationMetrics.citation_page_accuracy(cited_pages, relevant_pages)
        
        assert result['precision'] == 0.0
        assert result['recall'] == 0.0
    
    def test_citation_accuracy_empty_citations(self):
        """Test citation accuracy with no citations."""
        cited_pages = []
        relevant_pages = [1, 2, 3]
        
        result = CitationMetrics.citation_page_accuracy(cited_pages, relevant_pages)
        
        assert result['precision'] == 0.0
        assert result['recall'] == 0.0
        assert result['cited_count'] == 0
    
    def test_citation_accuracy_duplicate_citations(self):
        """Test that duplicate citations are handled correctly."""
        cited_pages = [1, 1, 2, 2, 3]
        relevant_pages = [1, 2]
        
        result = CitationMetrics.citation_page_accuracy(cited_pages, relevant_pages)
        
        # Set conversion should handle duplicates
        # Cited set: {1, 2, 3}, relevant set: {1, 2}
        # Correct: {1, 2} = 2 items
        assert result['precision'] == pytest.approx(2/3)
        assert result['recall'] == 1.0


class TestLatencyMetrics:
    """Test latency statistics computation."""
    
    def test_latency_statistics_basic(self):
        """Test basic latency statistics."""
        latencies = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        result = LatencyMetrics.compute_statistics(latencies)
        
        assert result['mean'] == 3.0
        assert result['median'] == 3.0
        assert result['min'] == 1.0
        assert result['max'] == 5.0
        assert result['count'] == 5
        assert result['std_dev'] > 0
    
    def test_latency_statistics_single_value(self):
        """Test latency statistics with single value."""
        latencies = [2.5]
        
        result = LatencyMetrics.compute_statistics(latencies)
        
        assert result['mean'] == 2.5
        assert result['median'] == 2.5
        assert result['min'] == 2.5
        assert result['max'] == 2.5
        assert result['std_dev'] == 0.0
        assert result['count'] == 1
    
    def test_latency_statistics_empty(self):
        """Test latency statistics with empty list."""
        latencies = []
        
        result = LatencyMetrics.compute_statistics(latencies)
        
        assert result['mean'] == 0.0
        assert result['median'] == 0.0
        assert result['min'] == 0.0
        assert result['max'] == 0.0
        assert result['std_dev'] == 0.0
        assert result['count'] == 0


class TestAggregation:
    """Test metric aggregation functions."""
    
    def test_aggregate_retrieval_metrics(self):
        """Test aggregation of retrieval metrics across questions."""
        per_question = [
            {
                'answerable': True,
                'retrieval_metrics': {
                    'hit_rate_at_1': 1.0,
                    'recall_at_5': 0.8,
                    'precision_at_5': 0.6,
                    'mrr': 1.0
                }
            },
            {
                'answerable': True,
                'retrieval_metrics': {
                    'hit_rate_at_1': 0.0,
                    'recall_at_5': 0.4,
                    'precision_at_5': 0.4,
                    'mrr': 0.5
                }
            }
        ]
        
        result = aggregate_retrieval_metrics(per_question)
        
        assert result['hit_rate_at_1'] == pytest.approx(0.5)
        assert result['recall_at_5'] == pytest.approx(0.6)
        assert result['precision_at_5'] == pytest.approx(0.5)
        assert result['mrr'] == pytest.approx(0.75)
    
    def test_aggregate_answer_metrics(self):
        """Test aggregation of answer metrics."""
        per_question = [
            {
                'answer_metrics': {
                    'keyword_match': {'match_rate': 1.0},
                    'faithfulness': {'overlap_ratio': 0.8}
                }
            },
            {
                'answer_metrics': {
                    'keyword_match': {'match_rate': 0.5},
                    'faithfulness': {'overlap_ratio': 0.6}
                }
            }
        ]
        
        result = aggregate_answer_metrics(per_question)
        
        assert result['avg_keyword_match_rate'] == pytest.approx(0.75)
        assert result['avg_faithfulness_ratio'] == pytest.approx(0.7)
        assert result['questions_evaluated'] == 2
    
    def test_aggregate_citation_metrics(self):
        """Test aggregation of citation metrics."""
        per_question = [
            {
                'citation_metrics': {
                    'precision': 1.0,
                    'recall': 0.8
                }
            },
            {
                'citation_metrics': {
                    'precision': 0.6,
                    'recall': 0.6
                }
            }
        ]
        
        result = aggregate_citation_metrics(per_question)
        
        assert result['avg_citation_precision'] == pytest.approx(0.8)
        assert result['avg_citation_recall'] == pytest.approx(0.7)
    
    def test_aggregate_with_empty_results(self):
        """Test aggregation with empty results."""
        per_question = []
        
        ret_result = aggregate_retrieval_metrics(per_question)
        ans_result = aggregate_answer_metrics(per_question)
        cit_result = aggregate_citation_metrics(per_question)
        
        assert ret_result == {}
        assert ans_result == {}
        assert cit_result == {}
