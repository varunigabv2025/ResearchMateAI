"""
Content selection service for paper comparison.
Selects relevant sections and chunks from papers.
"""
from typing import List, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Paper, PaperChunk


class ContentSelector:
    """
    Service for selecting relevant content from papers for comparison extraction.
    Uses a deterministic strategy prioritizing key sections.
    """
    
    # Sections prioritized for comparison (in order of importance)
    PRIORITY_SECTIONS = [
        "Abstract",
        "Introduction",
        "Methodology",
        "Methods",
        "Materials and Methods",
        "Approach",
        "Experiments",
        "Experimental Setup",
        "Results",
        "Findings",
        "Discussion",
        "Limitations",
        "Conclusion",
        "Future Work"
    ]
    
    # Maximum characters to include (to manage token limits)
    MAX_CONTENT_LENGTH = 8000  # Conservative limit for context window
    
    @staticmethod
    def get_paper_content_for_comparison(
        db: Session,
        paper_id: UUID,
        max_length: int = MAX_CONTENT_LENGTH
    ) -> tuple[str, List[Dict]]:
        """
        Get relevant content from a paper for comparison extraction.
        
        Prioritizes sections in order and limits total length.
        
        Args:
            db: Database session
            paper_id: UUID of the paper
            max_length: Maximum content length in characters
            
        Returns:
            Tuple of (concatenated_content, source_chunks)
            
        Raises:
            ValueError: If paper not found or has no content
        """
        # Get paper
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError(f"Paper {paper_id} not found")
        
        # Get all chunks for this paper, ordered by chunk_index
        all_chunks = db.query(PaperChunk).filter(
            PaperChunk.paper_id == paper_id
        ).order_by(
            PaperChunk.chunk_index
        ).all()
        
        if not all_chunks:
            raise ValueError(f"Paper {paper_id} has no extracted content")
        
        # Group chunks by section
        chunks_by_section = {}
        for chunk in all_chunks:
            section = chunk.section if chunk.section else "Unknown"
            if section not in chunks_by_section:
                chunks_by_section[section] = []
            chunks_by_section[section].append(chunk)
        
        # Select content in priority order
        selected_chunks = []
        total_length = 0
        
        # First pass: Add priority sections
        for priority_section in ContentSelector.PRIORITY_SECTIONS:
            if priority_section in chunks_by_section:
                for chunk in chunks_by_section[priority_section]:
                    if total_length + chunk.char_count <= max_length:
                        selected_chunks.append(chunk)
                        total_length += chunk.char_count
                    else:
                        break
            
            if total_length >= max_length:
                break
        
        # Second pass: If still under limit, add remaining chunks
        if total_length < max_length:
            for section, chunks in chunks_by_section.items():
                if section not in ContentSelector.PRIORITY_SECTIONS:
                    for chunk in chunks:
                        if total_length + chunk.char_count <= max_length:
                            # Check if not already selected
                            if chunk not in selected_chunks:
                                selected_chunks.append(chunk)
                                total_length += chunk.char_count
                        else:
                            break
                
                if total_length >= max_length:
                    break
        
        # If no priority sections matched, use first available chunks
        if not selected_chunks and all_chunks:
            for chunk in all_chunks:
                if total_length + chunk.char_count <= max_length:
                    selected_chunks.append(chunk)
                    total_length += chunk.char_count
                else:
                    break
        
        # Build concatenated content with section markers
        content_parts = []
        current_section = None
        
        for chunk in selected_chunks:
            section = chunk.section if chunk.section else "Content"
            
            # Add section header when section changes
            if section != current_section:
                content_parts.append(f"\n=== {section} ===\n")
                current_section = section
            
            content_parts.append(chunk.text)
        
        concatenated_content = "\n\n".join(content_parts)
        
        # Build source metadata
        source_chunks = [
            {
                "chunk_id": str(chunk.id),
                "page": chunk.page_number,
                "section": chunk.section,
                "char_count": chunk.char_count
            }
            for chunk in selected_chunks
        ]
        
        return concatenated_content, source_chunks
    
    @staticmethod
    def get_content_summary(source_chunks: List[Dict]) -> Dict:
        """
        Get summary statistics about selected content.
        
        Args:
            source_chunks: List of source chunk metadata
            
        Returns:
            Dictionary with summary statistics
        """
        if not source_chunks:
            return {
                "total_chunks": 0,
                "total_chars": 0,
                "sections_included": [],
                "page_range": None
            }
        
        sections = list(set(chunk["section"] for chunk in source_chunks if chunk["section"]))
        pages = [chunk["page"] for chunk in source_chunks]
        
        return {
            "total_chunks": len(source_chunks),
            "total_chars": sum(chunk["char_count"] for chunk in source_chunks),
            "sections_included": sections,
            "page_range": f"{min(pages)}-{max(pages)}" if pages else None
        }
