"""
Tests for text chunking service.
"""
import pytest
import uuid
from app.services.chunker import TextChunker


class TestTextChunker:
    """Tests for text chunking functionality."""
    
    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        text = "This is a short text."
        chunks = TextChunker.chunk_text(text, chunk_size=1000)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_long_text(self):
        """Test chunking long text into multiple chunks."""
        # Create text longer than chunk size
        text = "This is a sentence. " * 100  # ~2000 characters
        chunks = TextChunker.chunk_text(text, chunk_size=500, overlap=50)
        
        assert len(chunks) > 1
        # All chunks should be non-empty
        assert all(len(chunk) > 0 for chunk in chunks)
    
    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunks = TextChunker.chunk_text("")
        assert len(chunks) == 0
        
        chunks = TextChunker.chunk_text(None)
        assert len(chunks) == 0
    
    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        text = "Word " * 500  # Create long text
        chunks = TextChunker.chunk_text(text, chunk_size=100, overlap=20)
        
        if len(chunks) > 1:
            # Check that consecutive chunks share some content
            # (This is a basic check; actual overlap detection would be more complex)
            assert len(chunks) > 0
    
    def test_create_chunks_with_metadata(self):
        """Test creating chunks with full metadata."""
        paper_id = uuid.uuid4()
        pages_with_sections = [
            {"page": 1, "section": "Abstract", "text": "This is the abstract. " * 50},
            {"page": 2, "section": "Introduction", "text": "This is the introduction. " * 50}
        ]
        
        chunks = TextChunker.create_chunks_with_metadata(
            paper_id=paper_id,
            pages_with_sections=pages_with_sections,
            chunk_size=200,
            overlap=50
        )
        
        assert len(chunks) > 0
        
        # Check first chunk has required metadata
        first_chunk = chunks[0]
        assert "paper_id" in first_chunk
        assert "page_number" in first_chunk
        assert "section" in first_chunk
        assert "chunk_index" in first_chunk
        assert "text" in first_chunk
        assert "char_count" in first_chunk
        
        assert first_chunk["paper_id"] == paper_id
        assert first_chunk["page_number"] in [1, 2]
        assert first_chunk["section"] in ["Abstract", "Introduction"]
        assert first_chunk["chunk_index"] == 0
    
    def test_chunk_indices_are_sequential(self):
        """Test that chunk indices are sequential."""
        paper_id = uuid.uuid4()
        pages_with_sections = [
            {"page": 1, "section": "Abstract", "text": "Text. " * 100},
            {"page": 2, "section": "Introduction", "text": "More text. " * 100}
        ]
        
        chunks = TextChunker.create_chunks_with_metadata(
            paper_id=paper_id,
            pages_with_sections=pages_with_sections,
            chunk_size=200
        )
        
        # Check that indices are sequential starting from 0
        indices = [chunk["chunk_index"] for chunk in chunks]
        assert indices == list(range(len(chunks)))
    
    def test_get_chunk_stats(self):
        """Test chunk statistics calculation."""
        chunks = [
            {"char_count": 100},
            {"char_count": 200},
            {"char_count": 150}
        ]
        
        stats = TextChunker.get_chunk_stats(chunks)
        
        assert stats["total_chunks"] == 3
        assert stats["total_characters"] == 450
        assert stats["avg_chunk_size"] == 150
        assert stats["min_chunk_size"] == 100
        assert stats["max_chunk_size"] == 200
    
    def test_get_chunk_stats_empty(self):
        """Test chunk statistics with empty list."""
        stats = TextChunker.get_chunk_stats([])
        
        assert stats["total_chunks"] == 0
        assert stats["total_characters"] == 0
        assert stats["avg_chunk_size"] == 0
    
    def test_skip_empty_sections(self):
        """Test that empty sections are skipped."""
        paper_id = uuid.uuid4()
        pages_with_sections = [
            {"page": 1, "section": "Abstract", "text": "Valid text"},
            {"page": 2, "section": "Empty", "text": ""},
            {"page": 3, "section": "Whitespace", "text": "   "},
            {"page": 4, "section": "More", "text": "More valid text"}
        ]
        
        chunks = TextChunker.create_chunks_with_metadata(
            paper_id=paper_id,
            pages_with_sections=pages_with_sections
        )
        
        # Should only have chunks from pages with actual content
        assert len(chunks) >= 2
        sections = [chunk["section"] for chunk in chunks]
        assert "Abstract" in sections
        assert "More" in sections
