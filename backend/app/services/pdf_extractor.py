"""
PDF text extraction service using PyMuPDF.
Extracts text while preserving page numbers.
"""
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
from pathlib import Path


class PDFExtractor:
    """Handles PDF text extraction with page number preservation."""
    
    @staticmethod
    def validate_pdf(file_path: str) -> Tuple[bool, str]:
        """
        Validate that the file is a valid PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return False, "PDF file contains no pages"
            
            return True, ""
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"
    
    @staticmethod
    def extract_text_with_pages(file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF while preserving page numbers.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing page number and text:
            [
                {"page": 1, "text": "..."},
                {"page": 2, "text": "..."},
                ...
            ]
        """
        doc = fitz.open(file_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")  # Extract plain text
            
            # Store page data (page numbers are 1-indexed for users)
            pages_data.append({
                "page": page_num + 1,
                "text": text.strip()
            })
        
        doc.close()
        return pages_data
    
    @staticmethod
    def get_page_count(file_path: str) -> int:
        """
        Get the number of pages in a PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Number of pages
        """
        doc = fitz.open(file_path)
        count = len(doc)
        doc.close()
        return count
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, any]:
        """
        Extract PDF metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        doc = fitz.open(file_path)
        metadata = doc.metadata
        doc.close()
        
        # Clean up metadata (remove None values)
        return {k: v for k, v in metadata.items() if v is not None}
