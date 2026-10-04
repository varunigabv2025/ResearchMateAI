"""
Tests for retrieval service.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from app.services.retrieval_service import RetrievalService
from app.models import Paper, PaperChunk, Embedding


class TestRetrievalService:
    """Tests for retrieval service."""
    
    @pytest.fixture
    def service(self):
        """Create retrieval service instance."""
        return RetrievalService()
    
    @pytest.fixture
    def mock_paper(self):
        """Create mock paper."""
        paper = Mock(spec=Paper)
        paper.id = uuid.uuid4()
        paper.processed = True
        paper.processing_error = None
        return paper
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_paper_not_found(self, service):
        """Test retrieval with non-existent paper."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        paper_id = uuid.uuid4()
        
        with pytest.raises(ValueError, match="Paper with id .* not found"):
            await service.retrieve_relevant_chunks(
                mock_db, paper_id, "test question"
            )
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_paper_not_processed(self, service, mock_paper):
        """Test retrieval with unprocessed paper."""
        mock_paper.processed = False
        mock_paper.processing_error = "Embedding failed"
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        with pytest.raises(ValueError, match="Paper has not been fully processed"):
            await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question"
            )
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_success(self, service, mock_paper):
        """Test successful chunk retrieval."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Mock embedding service
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding', 
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            # Mock the search method
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Test chunk 1',
                    'page_number': 1,
                    'section': 'Introduction',
                    'chunk_index': 0,
                    'similarity': 0.9
                },
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Test chunk 2',
                    'page_number': 2,
                    'section': 'Methods',
                    'chunk_index': 1,
                    'similarity': 0.8
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question", top_k=2
                )
                
                assert len(results) == 2
                assert results[0]['similarity'] == 0.9
                assert results[0]['page_number'] == 1
                assert results[0]['section'] == 'Introduction'
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks_filters_by_threshold(self, service, mock_paper):
        """Test that chunks below similarity threshold are filtered."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Relevant chunk',
                    'page_number': 1,
                    'section': 'Introduction',
                    'chunk_index': 0,
                    'similarity': 0.9  # Above threshold
                },
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Irrelevant chunk',
                    'page_number': 2,
                    'section': 'Methods',
                    'chunk_index': 1,
                    'similarity': 0.5  # Below threshold
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question",
                    top_k=5, similarity_threshold=0.7
                )
                
                # Only the chunk above threshold should be returned
                assert len(results) == 1
                assert results[0]['similarity'] == 0.9
    
    def test_search_with_fallback(self, service):
        """Test fallback search method."""
        import numpy as np
        
        paper_id = uuid.uuid4()
        chunk_id1 = uuid.uuid4()
        chunk_id2 = uuid.uuid4()
        
        # Mock database results
        mock_result1 = Mock()
        mock_result1.chunk_id = chunk_id1
        mock_result1.text = "Test text 1"
        mock_result1.page_number = 1
        mock_result1.section = "Introduction"
        mock_result1.chunk_index = 0
        mock_result1.embedding = [0.9, 0.1, 0.0] + [0.0] * 1021  # Similar to query
        
        mock_result2 = Mock()
        mock_result2.chunk_id = chunk_id2
        mock_result2.text = "Test text 2"
        mock_result2.page_number = 2
        mock_result2.section = "Methods"
        mock_result2.chunk_index = 1
        mock_result2.embedding = [0.1, 0.9, 0.0] + [0.0] * 1021  # Less similar
        
        mock_db = Mock()
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [
            mock_result1, mock_result2
        ]
        
        query_embedding = [1.0, 0.0, 0.0] + [0.0] * 1021
        
        results = service._search_with_fallback(mock_db, paper_id, query_embedding, top_k=2)
        
        assert len(results) == 2
        # First result should be more similar
        assert results[0]['chunk_id'] == chunk_id1
        assert results[0]['similarity'] > results[1]['similarity']


class TestRetrievalModes:
    """Tests for different retrieval modes (dense, lexical, hybrid)."""
    
    @pytest.fixture
    def service(self):
        """Create retrieval service instance."""
        return RetrievalService()
    
    @pytest.fixture
    def mock_paper(self):
        """Create mock paper."""
        paper = Mock(spec=Paper)
        paper.id = uuid.uuid4()
        paper.processed = True
        paper.processing_error = None
        return paper
    
    @pytest.mark.asyncio
    async def test_default_mode_is_dense(self, service, mock_paper):
        """Test that default retrieval mode is DENSE."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Test chunk',
                    'page_number': 1,
                    'section': 'Intro',
                    'chunk_index': 0,
                    'similarity': 0.9
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                # Call without mode parameter
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question"
                )
                
                # Should return dense results with similarity field
                assert len(results) == 1
                assert 'similarity' in results[0]
                assert 'bm25_score' not in results[0]
                assert 'rrf_score' not in results[0]
    
    @pytest.mark.asyncio
    async def test_dense_mode_explicit(self, service, mock_paper):
        """Test explicit DENSE mode."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Test chunk',
                    'page_number': 1,
                    'section': 'Intro',
                    'chunk_index': 0,
                    'similarity': 0.9
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question", mode=RetrievalMode.DENSE
                )
                
                assert len(results) == 1
                assert 'similarity' in results[0]
    
    @pytest.mark.asyncio
    async def test_lexical_mode(self, service, mock_paper):
        """Test LEXICAL mode."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_lexical_results = [
            {
                'chunk_id': str(uuid.uuid4()),
                'text': 'Test chunk with Docker',
                'page_number': 1,
                'section': 'Methods',
                'chunk_index': 0,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        with patch.object(service.lexical_service, 'search_chunks', return_value=mock_lexical_results):
            results = await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "Docker", mode=RetrievalMode.LEXICAL
            )
            
            assert len(results) == 1
            assert 'bm25_score' in results[0]
            assert 'similarity' not in results[0]
            assert 'rrf_score' not in results[0]
    
    @pytest.mark.asyncio
    async def test_hybrid_mode(self, service, mock_paper):
        """Test HYBRID mode with RRF fusion."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        
        # Mock dense results
        mock_dense_results = [
            {
                'chunk_id': uuid.uuid4(),
                'text': 'Test chunk A',
                'page_number': 1,
                'section': 'Intro',
                'chunk_index': 0,
                'similarity': 0.9
            }
        ]
        
        # Mock lexical results
        mock_lexical_results = [
            {
                'chunk_id': str(uuid.uuid4()),
                'text': 'Test chunk B',
                'page_number': 2,
                'section': 'Methods',
                'chunk_index': 1,
                'bm25_score': 5.2,
                'rank': 1
            }
        ]
        
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            with patch.object(service, '_search_with_fallback', return_value=mock_dense_results):
                with patch.object(service.lexical_service, 'search_chunks', return_value=mock_lexical_results):
                    results = await service.retrieve_relevant_chunks(
                        mock_db, mock_paper.id, "test question", mode=RetrievalMode.HYBRID
                    )
                    
                    # Should return fused results
                    assert len(results) >= 1
                    # Hybrid results should have RRF score
                    assert 'rrf_score' in results[0]
                    # Should also preserve source scores
                    assert 'dense_similarity' in results[0] or 'lexical_score' in results[0]
    
    @pytest.mark.asyncio
    async def test_hybrid_mode_uses_larger_candidate_pools(self, service, mock_paper):
        """Test that hybrid mode uses larger candidate pools."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            with patch.object(service, '_search_with_fallback', return_value=[]) as mock_dense:
                with patch.object(service.lexical_service, 'search_chunks', return_value=[]) as mock_lexical:
                    await service.retrieve_relevant_chunks(
                        mock_db, mock_paper.id, "test", 
                        mode=RetrievalMode.HYBRID,
                        top_k=5,
                        dense_k=20,
                        lexical_k=20
                    )
                    
                    # Verify dense search was called with dense_k
                    assert mock_dense.called
                    call_args = mock_dense.call_args
                    # The k parameter should be 20 (dense_k), not 5 (top_k)
                    assert call_args[0][3] == 20  # 4th positional arg is k
                    
                    # Verify lexical search was called with lexical_k
                    assert mock_lexical.called
                    lexical_call_args = mock_lexical.call_args
                    assert lexical_call_args[1]['top_k'] == 20
    
    @pytest.mark.asyncio
    async def test_invalid_mode_raises_error(self, service, mock_paper):
        """Test that invalid retrieval mode raises error."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        with pytest.raises(ValueError, match="Unknown retrieval mode"):
            await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test", mode="invalid_mode"
            )
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_no_mode_parameter(self, service, mock_paper):
        """Test backward compatibility when mode parameter is not provided."""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Test chunk',
                    'page_number': 1,
                    'section': 'Intro',
                    'chunk_index': 0,
                    'similarity': 0.9
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                # Call with old API (no mode parameter)
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question", top_k=5
                )
                
                # Should work and return dense results
                assert len(results) == 1
                assert 'similarity' in results[0]

    @pytest.mark.asyncio
    async def test_reranked_mode_exists(self, service):
        """Test that RERANKED mode exists in RetrievalMode enum."""
        from app.services.retrieval_service import RetrievalMode
        
        assert hasattr(RetrievalMode, 'RERANKED')
        assert RetrievalMode.RERANKED == "reranked"
    
    @pytest.mark.asyncio
    async def test_reranked_mode_uses_hybrid_candidates(self, service, mock_paper):
        """Test that RERANKED mode uses hybrid RRF candidates."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Mock hybrid results
        mock_hybrid_results = [
            {
                'text': f'Chunk {i}',
                'page_number': i,
                'section': 'Test',
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': i,
                'rrf_score': 1.0 - (i * 0.01),
                'dense_similarity': 0.8,
                'lexical_score': 10.0,
                'dense_rank': i + 1,
                'lexical_rank': i + 1
            }
            for i in range(20)
        ]
        
        # Mock reranker predictions
        mock_reranker_scores = [0.9 - (i * 0.01) for i in range(20)]
        
        # Create mock reranker
        mock_reranker = Mock()
        mock_reranker.predict.return_value = mock_reranker_scores
        service.reranker = mock_reranker
        
        with patch.object(service, '_retrieve_hybrid', new_callable=AsyncMock, return_value=mock_hybrid_results):
            results = await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question", 
                mode=RetrievalMode.RERANKED, top_k=5
            )
            
            # Verify hybrid was called
            service._retrieve_hybrid.assert_called_once()
            
            # Verify reranker was called with 20 candidates
            service.reranker.predict.assert_called_once()
            call_args = service.reranker.predict.call_args[0][0]
            assert len(call_args) == 20  # rerank_pool_size default
            
            # Verify results have reranker_score
            assert len(results) == 5
            for result in results:
                assert 'reranker_score' in result
    
    @pytest.mark.asyncio
    async def test_reranked_mode_sorts_by_reranker_score(self, service, mock_paper):
        """Test that RERANKED mode sorts results by reranker score."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Mock hybrid results
        mock_hybrid_results = [
            {
                'text': f'Chunk {i}',
                'page_number': i,
                'section': 'Test',
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': i,
                'rrf_score': 1.0 - (i * 0.01),
                'dense_similarity': 0.8,
                'lexical_score': 10.0,
                'dense_rank': i + 1,
                'lexical_rank': i + 1
            }
            for i in range(10)
        ]
        
        # Mock reranker scores that reverse the order
        # Reranker prefers later chunks
        mock_reranker_scores = [0.5 + (i * 0.01) for i in range(10)]
        
        # Create mock reranker
        mock_reranker = Mock()
        mock_reranker.predict.return_value = mock_reranker_scores
        service.reranker = mock_reranker
        
        with patch.object(service, '_retrieve_hybrid', new_callable=AsyncMock, return_value=mock_hybrid_results):
            results = await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question", 
                mode=RetrievalMode.RERANKED, top_k=5
            )
            
            # Verify results are sorted by reranker score (descending)
            assert len(results) == 5
            for i in range(len(results) - 1):
                assert results[i]['reranker_score'] >= results[i + 1]['reranker_score']
    
    @pytest.mark.asyncio
    async def test_reranked_mode_respects_final_top_k(self, service, mock_paper):
        """Test that RERANKED mode respects final_top_k parameter."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Mock hybrid results
        mock_hybrid_results = [
            {
                'text': f'Chunk {i}',
                'page_number': i,
                'section': 'Test',
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': i,
                'rrf_score': 1.0,
                'dense_similarity': 0.8,
                'lexical_score': 10.0,
                'dense_rank': i + 1,
                'lexical_rank': i + 1
            }
            for i in range(20)
        ]
        
        mock_reranker_scores = [0.9] * 20
        
        # Create mock reranker
        mock_reranker = Mock()
        mock_reranker.predict.return_value = mock_reranker_scores
        service.reranker = mock_reranker
        
        with patch.object(service, '_retrieve_hybrid', new_callable=AsyncMock, return_value=mock_hybrid_results):
            results = await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question", 
                mode=RetrievalMode.RERANKED, top_k=3
            )
            
            # Verify exactly top_k=3 results returned
            assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_reranked_mode_preserves_metadata(self, service, mock_paper):
        """Test that RERANKED mode preserves all metadata from hybrid."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Mock hybrid results with full metadata
        test_chunk_id = str(uuid.uuid4())
        mock_hybrid_results = [
            {
                'text': 'Test chunk',
                'page_number': 1,
                'section': 'Introduction',
                'chunk_id': test_chunk_id,
                'chunk_index': 0,
                'rrf_score': 0.95,
                'dense_similarity': 0.85,
                'lexical_score': 12.5,
                'dense_rank': 1,
                'lexical_rank': 2
            }
        ]
        
        mock_reranker_scores = [0.92]
        
        # Create mock reranker
        mock_reranker = Mock()
        mock_reranker.predict.return_value = mock_reranker_scores
        service.reranker = mock_reranker
        
        with patch.object(service, '_retrieve_hybrid', new_callable=AsyncMock, return_value=mock_hybrid_results):
            results = await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question", 
                mode=RetrievalMode.RERANKED, top_k=1
            )
            
            # Verify all metadata preserved
            assert len(results) == 1
            result = results[0]
            assert result['text'] == 'Test chunk'
            assert result['page_number'] == 1
            assert result['section'] == 'Introduction'
            assert result['chunk_id'] == test_chunk_id
            assert result['chunk_index'] == 0
            assert result['rrf_score'] == 0.95
            assert result['dense_similarity'] == 0.85
            assert result['lexical_score'] == 12.5
            assert result['dense_rank'] == 1
            assert result['lexical_rank'] == 2
            assert result['reranker_score'] == 0.92
    
    @pytest.mark.asyncio
    async def test_reranked_mode_fallback_when_reranker_none(self, service, mock_paper):
        """Test that RERANKED mode falls back to HYBRID when reranker is None."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Set reranker to None (simulating unavailable model)
        service.reranker = None
        
        # Mock hybrid results
        mock_hybrid_results = [
            {
                'text': 'Test chunk',
                'page_number': 1,
                'section': 'Test',
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': 0,
                'rrf_score': 0.95,
                'dense_similarity': 0.8,
                'lexical_score': 10.0,
                'dense_rank': 1,
                'lexical_rank': 1
            }
        ]
        
        with patch.object(service, '_retrieve_hybrid', new_callable=AsyncMock, return_value=mock_hybrid_results):
            results = await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question", 
                mode=RetrievalMode.RERANKED, top_k=5
            )
            
            # Verify hybrid was called (fallback)
            service._retrieve_hybrid.assert_called()
            
            # Verify results returned (no crash)
            assert len(results) == 1
            assert results[0]['text'] == 'Test chunk'
    
    @pytest.mark.asyncio
    async def test_reranked_mode_fallback_on_inference_error(self, service, mock_paper):
        """Test that RERANKED mode falls back to HYBRID when reranker inference fails."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        # Mock hybrid results
        mock_hybrid_results = [
            {
                'text': 'Test chunk',
                'page_number': 1,
                'section': 'Test',
                'chunk_id': str(uuid.uuid4()),
                'chunk_index': 0,
                'rrf_score': 0.95,
                'dense_similarity': 0.8,
                'lexical_score': 10.0,
                'dense_rank': 1,
                'lexical_rank': 1
            }
        ]
        
        # Create mock reranker that raises an error
        mock_reranker = Mock()
        mock_reranker.predict.side_effect = RuntimeError("Model inference failed")
        service.reranker = mock_reranker
        
        with patch.object(service, '_retrieve_hybrid', new_callable=AsyncMock, return_value=mock_hybrid_results):
            results = await service.retrieve_relevant_chunks(
                mock_db, mock_paper.id, "test question", 
                mode=RetrievalMode.RERANKED, top_k=5
            )
            
            # Verify results returned despite error (fallback to RRF ranking)
            assert len(results) == 1
            assert results[0]['text'] == 'Test chunk'
            # No reranker_score since inference failed
            assert 'reranker_score' not in results[0]
    
    @pytest.mark.asyncio
    async def test_dense_mode_unchanged_after_reranked_addition(self, service, mock_paper):
        """Test that DENSE mode behavior is unchanged after adding RERANKED."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_embedding = [0.1] * 1024
        with patch.object(service.embedding_service, 'generate_embedding',
                         new_callable=AsyncMock, return_value=mock_embedding):
            
            mock_results = [
                {
                    'chunk_id': uuid.uuid4(),
                    'text': 'Dense result',
                    'page_number': 1,
                    'section': 'Intro',
                    'chunk_index': 0,
                    'similarity': 0.9
                }
            ]
            
            with patch.object(service, '_search_with_fallback', return_value=mock_results):
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question", mode=RetrievalMode.DENSE
                )
                
                # Verify DENSE behavior unchanged
                assert len(results) == 1
                assert results[0]['text'] == 'Dense result'
                assert 'similarity' in results[0]
                assert 'reranker_score' not in results[0]
    
    @pytest.mark.asyncio
    async def test_hybrid_mode_unchanged_after_reranked_addition(self, service, mock_paper):
        """Test that HYBRID mode behavior is unchanged after adding RERANKED."""
        from app.services.retrieval_service import RetrievalMode
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_paper
        
        mock_dense_results = [
            {'chunk_id': str(uuid.uuid4()), 'text': 'Dense 1', 'page_number': 1,
             'section': 'S1', 'chunk_index': 0, 'similarity': 0.9, 'rank': 1}
        ]
        
        mock_lexical_results = [
            {'chunk_id': str(uuid.uuid4()), 'text': 'Lexical 1', 'page_number': 2,
             'section': 'S2', 'chunk_index': 1, 'bm25_score': 10.0, 'rank': 1}
        ]
        
        with patch.object(service, '_search_with_fallback', return_value=mock_dense_results):
            with patch.object(service.lexical_service, 'search_chunks', return_value=mock_lexical_results):
                results = await service.retrieve_relevant_chunks(
                    mock_db, mock_paper.id, "test question", mode=RetrievalMode.HYBRID
                )
                
                # Verify HYBRID behavior unchanged
                assert len(results) >= 1
                assert 'rrf_score' in results[0]
                assert 'reranker_score' not in results[0]
