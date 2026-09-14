"""
Text chunking service with metadata preservation.
Splits text into manageable chunks while maintaining paper, page, and section context.
"""
from typing import List, Dict
from uuid import UUID


class TextChunker:
    """Handles text chunking with metadata preservation."""
    
    # Chunking configuration
    DEFAULT_CHUNK_SIZE = 1000  # characters
    DEFAULT_OVERLAP = 200      # characters for context preservation
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) == 0:
            return []
        
        # If text is shorter than chunk size, return as single chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Get chunk
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary if not at the end
            if end < len(text):
                # Look for sentence-ending punctuation in the last 200 chars
                last_part = chunk[-200:]
                sentence_ends = ['.', '!', '?', '\n']
                
                best_break = -1
                for punct in sentence_ends:
                    pos = last_part.rfind(punct)
                    if pos > best_break:
                        best_break = pos
                
                if best_break != -1:
                    # Adjust chunk to end at sentence boundary
                    actual_end = start + (chunk_size - 200) + best_break + 1
                    chunk = text[start:actual_end]
                    end = actual_end
            
            chunks.append(chunk.strip())
            
            # Move start position (with overlap)
            start = end - overlap
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    @staticmethod
    def create_chunks_with_metadata(
        paper_id: UUID,
        pages_with_sections: List[Dict[str, any]],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP
    ) -> List[Dict[str, any]]:
        """
        Create chunks with full metadata (paper_id, page, section, chunk_index).
        
        Args:
            paper_id: UUID of the paper
            pages_with_sections: List of dicts with page, section, and text
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries with metadata:
            [
                {
                    "paper_id": UUID,
                    "page": 1,
                    "section": "Introduction",
                    "chunk_index": 0,
                    "text": "...",
                    "char_count": 950
                },
                ...
            ]
        """
        all_chunks = []
        global_chunk_index = 0
        
        for page_section in pages_with_sections:
            page_num = page_section["page"]
            section = page_section.get("section")
            text = page_section["text"]
            
            # Skip empty text
            if not text or len(text.strip()) == 0:
                continue
            
            # Chunk the text
            text_chunks = TextChunker.chunk_text(text, chunk_size, overlap)
            
            # Add metadata to each chunk
            for chunk_text in text_chunks:
                chunk_data = {
                    "paper_id": paper_id,
                    "page_number": page_num,
                    "section": section,
                    "chunk_index": global_chunk_index,
                    "text": chunk_text,
                    "char_count": len(chunk_text)
                }
                all_chunks.append(chunk_data)
                global_chunk_index += 1
        
        return all_chunks
    
    @staticmethod
    def get_chunk_stats(chunks: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0
            }
        
        char_counts = [c["char_count"] for c in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_characters": sum(char_counts),
            "avg_chunk_size": sum(char_counts) // len(char_counts),
            "min_chunk_size": min(char_counts),
            "max_chunk_size": max(char_counts)
        }
