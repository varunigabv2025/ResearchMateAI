"""
Tests for hybrid retrieval and Reciprocal Rank Fusion (RRF).
"""
import pytest
from app.services.retrieval_service import RetrievalService


class TestReciprocalRankFusion:
    """Tests for RRF algorithm."""
    
    @pytest.fixture
    def service(self):
        """Create retrieval service instance."""
        return RetrievalService()
    
    def test_rrf_basic_fusion(self, service):
        """Test basic RRF fusion with overlapping results."""
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            },
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'similarity': 0.8,
                'rank': 2
            }
        ]
        
        lexical_results = [
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            },
            {
                'chunk_id': 'chunk_c',
                'text': 'Text C',
                'page_number': 3,
                'section': 'Results',
                'chunk_index': 2,
                'bm25_score': 3.1,
                'rank': 2
            }
        ]
        
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        # Should have 3 unique chunks
        assert len(fused) == 3
        
        # chunk_b appears in both sources, should have highest RRF score
        # RRF(chunk_b) = 1/(60+1) + 1/(60+1) = 2/61 ≈ 0.0328
        # RRF(chunk_a) = 1/(60+1) = 1/61 ≈ 0.0164
        # RRF(chunk_c) = 1/(60+2) = 1/62 ≈ 0.0161
        
        chunk_ids = [r['chunk_id'] for r in fused]
        assert 'chunk_a' in chunk_ids
        assert 'chunk_b' in chunk_ids
        assert 'chunk_c' in chunk_ids
        
        # chunk_b should rank first
        assert fused[0]['chunk_id'] == 'chunk_b'
        assert fused[0]['rrf_score'] > fused[1]['rrf_score']
    
    def test_rrf_single_source_dense_only(self, service):
        """Test RRF with only dense results."""
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            }
        ]
        
        lexical_results = []
        
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        assert len(fused) == 1
        assert fused[0]['chunk_id'] == 'chunk_a'
        assert fused[0]['dense_similarity'] == 0.9
        assert fused[0]['lexical_score'] is None
    
    def test_rrf_single_source_lexical_only(self, service):
        """Test RRF with only lexical results."""
        dense_results = []
        
        lexical_results = [
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        assert len(fused) == 1
        assert fused[0]['chunk_id'] == 'chunk_b'
        assert fused[0]['dense_similarity'] is None
        assert fused[0]['lexical_score'] == 5.2
    
    def test_rrf_both_empty(self, service):
        """Test RRF with no results from either source."""
        dense_results = []
        lexical_results = []
        
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        assert len(fused) == 0
    
    def test_rrf_deduplication(self, service):
        """Test that duplicate chunks are properly merged."""
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            }
        ]
        
        lexical_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        # Should have only 1 result (deduplicated)
        assert len(fused) == 1
        assert fused[0]['chunk_id'] == 'chunk_a'
        assert fused[0]['dense_similarity'] == 0.9
        assert fused[0]['lexical_score'] == 5.2
        assert fused[0]['dense_rank'] == 1
        assert fused[0]['lexical_rank'] == 1
    
    def test_rrf_formula_correctness(self, service):
        """Test that RRF formula is correctly applied."""
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            }
        ]
        
        lexical_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'bm25_score': 5.2,
                'rank': 2
            }
        ]
        
        rrf_k = 60
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=rrf_k)
        
        # Expected RRF = 1/(60+1) + 1/(60+2) = 1/61 + 1/62
        expected_rrf = 1.0 / (rrf_k + 1) + 1.0 / (rrf_k + 2)
        
        assert len(fused) == 1
        assert abs(fused[0]['rrf_score'] - expected_rrf) < 1e-6
    
    def test_rrf_tie_breaking(self, service):
        """Test deterministic tie-breaking by chunk_id."""
        # Create two chunks with same RRF score
        dense_results = [
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'similarity': 0.8,
                'rank': 1
            },
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.8,
                'rank': 2
            }
        ]
        
        lexical_results = []
        
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        # Both have same RRF score (only from dense), but should be ordered by chunk_id
        assert len(fused) == 2
        # Sorted by descending RRF score, then by chunk_id
        # Since RRF scores differ (rank 1 vs rank 2), chunk_b should be first
        assert fused[0]['chunk_id'] == 'chunk_b'
    
    def test_rrf_preserves_metadata(self, service):
        """Test that all chunk metadata is preserved."""
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A with content',
                'page_number': 1,
                'section': 'Introduction',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            }
        ]
        
        lexical_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A with content',
                'page_number': 1,
                'section': 'Introduction',
                'chunk_index': 0,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        assert len(fused) == 1
        result = fused[0]
        
        # Check all metadata is preserved
        assert result['chunk_id'] == 'chunk_a'
        assert result['text'] == 'Text A with content'
        assert result['page_number'] == 1
        assert result['section'] == 'Introduction'
        assert result['chunk_index'] == 0
        assert result['dense_similarity'] == 0.9
        assert result['lexical_score'] == 5.2
        assert result['dense_rank'] == 1
        assert result['lexical_rank'] == 1
        assert 'rrf_score' in result
    
    def test_rrf_ranking_stability(self, service):
        """Test that RRF ranking is stable across calls."""
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            },
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'similarity': 0.8,
                'rank': 2
            }
        ]
        
        lexical_results = [
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        fused1 = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        fused2 = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        assert len(fused1) == len(fused2)
        for r1, r2 in zip(fused1, fused2):
            assert r1['chunk_id'] == r2['chunk_id']
            assert r1['rrf_score'] == r2['rrf_score']
    
    def test_rrf_different_k_values(self, service):
        """Test RRF with different k values."""
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            }
        ]
        
        lexical_results = []
        
        fused_k60 = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        fused_k100 = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=100)
        
        # Different k values should produce different scores
        assert fused_k60[0]['rrf_score'] != fused_k100[0]['rrf_score']
        # k=60 should have higher score than k=100 for rank=1
        assert fused_k60[0]['rrf_score'] > fused_k100[0]['rrf_score']
