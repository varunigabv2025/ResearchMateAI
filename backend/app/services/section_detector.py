"""
Section detection service for research papers.
Uses simple heading pattern matching to detect common paper sections.
"""
import re
from typing import List, Dict, Optional


class SectionDetector:
    """Detects sections in research papers using heading patterns."""
    
    # Common research paper sections with their pattern variations
    SECTION_PATTERNS = {
        "Abstract": [
            r"^\s*abstract\s*$",
            r"^\s*summary\s*$",
        ],
        "Introduction": [
            r"^\s*introduction\s*$",
            r"^\s*1\.\s*introduction\s*$",
            r"^\s*i\.\s*introduction\s*$",
        ],
        "Related Work": [
            r"^\s*related\s+work\s*$",
            r"^\s*literature\s+review\s*$",
            r"^\s*background\s*$",
            r"^\s*prior\s+work\s*$",
            r"^\s*\d+\.\s*related\s+work\s*$",
        ],
        "Methodology": [
            r"^\s*methodology\s*$",
            r"^\s*methods\s*$",
            r"^\s*materials\s+and\s+methods\s*$",
            r"^\s*approach\s*$",
            r"^\s*\d+\.\s*methodology\s*$",
            r"^\s*\d+\.\s*methods\s*$",
        ],
        "Experiments": [
            r"^\s*experiments\s*$",
            r"^\s*experimental\s+setup\s*$",
            r"^\s*experimental\s+results\s*$",
            r"^\s*\d+\.\s*experiments\s*$",
        ],
        "Results": [
            r"^\s*results\s*$",
            r"^\s*findings\s*$",
            r"^\s*experimental\s+results\s*$",
            r"^\s*\d+\.\s*results\s*$",
        ],
        "Discussion": [
            r"^\s*discussion\s*$",
            r"^\s*results\s+and\s+discussion\s*$",
            r"^\s*\d+\.\s*discussion\s*$",
        ],
        "Limitations": [
            r"^\s*limitations\s*$",
            r"^\s*threats\s+to\s+validity\s*$",
            r"^\s*\d+\.\s*limitations\s*$",
        ],
        "Conclusion": [
            r"^\s*conclusion\s*$",
            r"^\s*conclusions\s*$",
            r"^\s*concluding\s+remarks\s*$",
            r"^\s*\d+\.\s*conclusion\s*$",
        ],
        "Future Work": [
            r"^\s*future\s+work\s*$",
            r"^\s*future\s+directions\s*$",
            r"^\s*future\s+research\s*$",
        ],
        "References": [
            r"^\s*references\s*$",
            r"^\s*bibliography\s*$",
            r"^\s*works\s+cited\s*$",
        ],
    }
    
    @staticmethod
    def detect_section(text: str) -> Optional[str]:
        """
        Detect if a text line matches a section heading.
        
        Args:
            text: Text line to check
            
        Returns:
            Section name if matched, None otherwise
        """
        text_lower = text.lower().strip()
        
        # Skip very long lines (unlikely to be headings)
        if len(text_lower) > 100:
            return None
        
        # Check against all section patterns
        for section_name, patterns in SectionDetector.SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, text_lower, re.IGNORECASE):
                    return section_name
        
        return None
    
    @staticmethod
    def detect_sections_in_pages(pages_data: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Detect sections in extracted page data.
        Assigns section labels to text based on detected headings.
        
        Args:
            pages_data: List of page dictionaries with "page" and "text" keys
            
        Returns:
            List of dictionaries with page, section, and text:
            [
                {"page": 1, "section": "Abstract", "text": "..."},
                {"page": 2, "section": "Introduction", "text": "..."},
                ...
            ]
        """
        result = []
        current_section = None
        
        for page_data in pages_data:
            page_num = page_data["page"]
            text = page_data["text"]
            
            # Split text into lines to detect section headings
            lines = text.split('\n')
            page_text_parts = []
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check if this line is a section heading
                detected_section = SectionDetector.detect_section(line_stripped)
                
                if detected_section:
                    # Save accumulated text under previous section
                    if page_text_parts:
                        result.append({
                            "page": page_num,
                            "section": current_section,
                            "text": '\n'.join(page_text_parts).strip()
                        })
                        page_text_parts = []
                    
                    # Update current section
                    current_section = detected_section
                else:
                    # Add line to current section's text
                    if line_stripped:  # Skip empty lines
                        page_text_parts.append(line)
            
            # Add remaining text from this page
            if page_text_parts:
                result.append({
                    "page": page_num,
                    "section": current_section,
                    "text": '\n'.join(page_text_parts).strip()
                })
        
        return result
    
    @staticmethod
    def get_detected_sections(pages_with_sections: List[Dict[str, any]]) -> List[str]:
        """
        Get list of unique sections detected in the document.
        
        Args:
            pages_with_sections: List of page/section data
            
        Returns:
            List of unique section names (in order of appearance)
        """
        sections = []
        seen = set()
        
        for item in pages_with_sections:
            section = item.get("section")
            if section and section not in seen:
                sections.append(section)
                seen.add(section)
        
        return sections
