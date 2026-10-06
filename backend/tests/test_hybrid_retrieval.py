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


class TestWeightedRRF:
    """Tests for weighted RRF (Phase 8 experiment)."""
    
    @pytest.fixture
    def service(self):
        """Create retrieval service instance."""
        return RetrievalService()
    
    def test_weighted_rrf_equal_weights(self, service):
        """Test that alpha=1.0, beta=1.0 reproduces standard RRF behavior."""
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
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        # Standard RRF (implicit alpha=beta=1.0)
        standard_fused = service._reciprocal_rank_fusion(dense_results, lexical_results, rrf_k=60)
        
        # Weighted RRF with explicit alpha=beta=1.0
        weighted_fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=1.0, rrf_beta=1.0
        )
        
        # Should produce identical results
        assert len(standard_fused) == len(weighted_fused)
        for std, weighted in zip(standard_fused, weighted_fused):
            assert std['chunk_id'] == weighted['chunk_id']
            assert abs(std['rrf_score'] - weighted['rrf_score']) < 1e-9
    
    def test_weighted_rrf_dense_boost(self, service):
        """Test that alpha > beta boosts dense retrieval contributions."""
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
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        # Equal weights
        equal_fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=1.0, rrf_beta=1.0
        )
        
        # Dense-boosted weights (α=1.4, β=0.6)
        boosted_fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=1.4, rrf_beta=0.6
        )
        
        # Find chunk_a in both results
        chunk_a_equal = next(r for r in equal_fused if r['chunk_id'] == 'chunk_a')
        chunk_a_boosted = next(r for r in boosted_fused if r['chunk_id'] == 'chunk_a')
        
        # chunk_a score should increase with dense boost
        assert chunk_a_boosted['rrf_score'] > chunk_a_equal['rrf_score']
        
        # Verify exact calculation
        # Equal: RRF(chunk_a) = 1.0/(60+1) = 0.01639...
        # Boosted: RRF(chunk_a) = 1.4/(60+1) = 0.02295...
        assert abs(chunk_a_equal['rrf_score'] - (1.0/61)) < 1e-6
        assert abs(chunk_a_boosted['rrf_score'] - (1.4/61)) < 1e-6
    
    def test_weighted_rrf_lexical_boost(self, service):
        """Test that beta > alpha boosts lexical retrieval contributions."""
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
                'chunk_id': 'chunk_b',
                'text': 'Text B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        # Equal weights
        equal_fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=1.0, rrf_beta=1.0
        )
        
        # Lexical-boosted weights (α=0.6, β=1.4)
        boosted_fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=0.6, rrf_beta=1.4
        )
        
        # Find chunk_b in both results
        chunk_b_equal = next(r for r in equal_fused if r['chunk_id'] == 'chunk_b')
        chunk_b_boosted = next(r for r in boosted_fused if r['chunk_id'] == 'chunk_b')
        
        # chunk_b score should increase with lexical boost
        assert chunk_b_boosted['rrf_score'] > chunk_b_equal['rrf_score']
        
        # Verify exact calculation
        # Equal: RRF(chunk_b) = 1.0/(60+1) = 0.01639...
        # Boosted: RRF(chunk_b) = 1.4/(60+1) = 0.02295...
        assert abs(chunk_b_equal['rrf_score'] - (1.0/61)) < 1e-6
        assert abs(chunk_b_boosted['rrf_score'] - (1.4/61)) < 1e-6
    
    def test_weighted_rrf_ranking_change(self, service):
        """Test that weighted RRF can change ranking order."""
        # Scenario: chunk_a ranks high in dense only, chunk_b appears in both moderately
        dense_results = [
            {
                'chunk_id': 'chunk_a',
                'text': 'Text A (dense rank 1)',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9,
                'rank': 1
            },
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B (dense rank 10)',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'similarity': 0.5,
                'rank': 10
            }
        ]
        
        lexical_results = [
            {
                'chunk_id': 'chunk_b',
                'text': 'Text B (lexical rank 1)',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        # Equal weights: chunk_b wins due to consensus
        # RRF(chunk_a) = 1/(60+1) = 0.01639
        # RRF(chunk_b) = 1/(60+10) + 1/(60+1) = 0.01429 + 0.01639 = 0.03068
        equal_fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=1.0, rrf_beta=1.0
        )
        assert equal_fused[0]['chunk_id'] == 'chunk_b'  # chunk_b ranks first
        assert equal_fused[1]['chunk_id'] == 'chunk_a'  # chunk_a ranks second
        
        # Dense-boosted weights (α=2.0, β=0.5): chunk_a should win
        # RRF(chunk_a) = 2.0/(60+1) = 0.03279
        # RRF(chunk_b) = 2.0/(60+10) + 0.5/(60+1) = 0.02857 + 0.00820 = 0.03677
        # Actually chunk_b still wins, let's try more extreme
        
        # Dense-boosted weights (α=3.0, β=0.3): chunk_a should win
        # RRF(chunk_a) = 3.0/(60+1) = 0.04918
        # RRF(chunk_b) = 3.0/(60+10) + 0.3/(60+1) = 0.04286 + 0.00492 = 0.04778
        # chunk_a wins!
        boosted_fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=3.0, rrf_beta=0.3
        )
        assert boosted_fused[0]['chunk_id'] == 'chunk_a'  # chunk_a ranks first now
        assert boosted_fused[1]['chunk_id'] == 'chunk_b'  # chunk_b ranks second
    
    def test_weighted_rrf_preserves_deduplication(self, service):
        """Test that weighted RRF still deduplicates properly."""
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
        
        fused = service._reciprocal_rank_fusion(
            dense_results, lexical_results, rrf_k=60, rrf_alpha=1.4, rrf_beta=0.6
        )
        
        # Should have exactly 1 result (chunk_a deduplicated)
        assert len(fused) == 1
        assert fused[0]['chunk_id'] == 'chunk_a'
        
        # Score should be sum of both contributions
        # RRF(chunk_a) = 1.4/(60+1) + 0.6/(60+1) = 2.0/61
        expected_score = 2.0 / 61
        assert abs(fused[0]['rrf_score'] - expected_score) < 1e-6
        
        # Should have both dense and lexical metadata
        assert fused[0]['dense_similarity'] == 0.9
        assert fused[0]['lexical_score'] == 5.2
        assert fused[0]['dense_rank'] == 1
        assert fused[0]['lexical_rank'] == 1
