"""
Tests for section detection service.
"""
import pytest
from app.services.section_detector import SectionDetector


class TestSectionDetector:
    """Tests for section detection functionality."""
    
    def test_detect_abstract_section(self):
        """Test detection of Abstract section."""
        assert SectionDetector.detect_section("Abstract") == "Abstract"
        assert SectionDetector.detect_section("ABSTRACT") == "Abstract"
        assert SectionDetector.detect_section("  abstract  ") == "Abstract"
    
    def test_detect_introduction_section(self):
        """Test detection of Introduction section."""
        assert SectionDetector.detect_section("Introduction") == "Introduction"
        assert SectionDetector.detect_section("1. Introduction") == "Introduction"
        assert SectionDetector.detect_section("I. Introduction") == "Introduction"
    
    def test_detect_methodology_section(self):
        """Test detection of Methodology section."""
        assert SectionDetector.detect_section("Methodology") == "Methodology"
        assert SectionDetector.detect_section("Methods") == "Methodology"
        assert SectionDetector.detect_section("Materials and Methods") == "Methodology"
    
    def test_detect_results_section(self):
        """Test detection of Results section."""
        assert SectionDetector.detect_section("Results") == "Results"
        assert SectionDetector.detect_section("Findings") == "Results"
        assert SectionDetector.detect_section("3. Results") == "Results"
    
    def test_detect_conclusion_section(self):
        """Test detection of Conclusion section."""
        assert SectionDetector.detect_section("Conclusion") == "Conclusion"
        assert SectionDetector.detect_section("Conclusions") == "Conclusion"
        assert SectionDetector.detect_section("5. Conclusion") == "Conclusion"
    
    def test_detect_references_section(self):
        """Test detection of References section."""
        assert SectionDetector.detect_section("References") == "References"
        assert SectionDetector.detect_section("Bibliography") == "References"
    
    def test_no_detection_for_regular_text(self):
        """Test that regular text is not detected as a section."""
        assert SectionDetector.detect_section("This is regular text") is None
        assert SectionDetector.detect_section("The methodology used in this paper") is None
    
    def test_no_detection_for_long_lines(self):
        """Test that very long lines are not considered headings."""
        long_text = "This is a very long line that should not be detected as a section heading " * 5
        assert SectionDetector.detect_section(long_text) is None
    
    def test_detect_sections_in_pages(self):
        """Test section detection across multiple pages."""
        pages_data = [
            {"page": 1, "text": "Abstract\nThis is the abstract text."},
            {"page": 2, "text": "Introduction\nThis is the introduction."},
            {"page": 3, "text": "Methods\nThis describes the methods."}
        ]
        
        result = SectionDetector.detect_sections_in_pages(pages_data)
        
        assert len(result) > 0
        # Check that sections were detected
        sections = [item.get("section") for item in result if item.get("section")]
        assert "Abstract" in sections
        assert "Introduction" in sections
        assert "Methodology" in sections
    
    def test_get_detected_sections(self):
        """Test getting unique sections from processed data."""
        pages_with_sections = [
            {"page": 1, "section": "Abstract", "text": "..."},
            {"page": 2, "section": "Introduction", "text": "..."},
            {"page": 3, "section": "Introduction", "text": "..."},  # Duplicate
            {"page": 4, "section": "Results", "text": "..."}
        ]
        
        sections = SectionDetector.get_detected_sections(pages_with_sections)
        
        assert len(sections) == 3  # Only unique sections
        assert "Abstract" in sections
        assert "Introduction" in sections
        assert "Results" in sections
    
    def test_section_patterns_exist(self):
        """Test that section patterns are defined."""
        assert hasattr(SectionDetector, 'SECTION_PATTERNS')
        assert isinstance(SectionDetector.SECTION_PATTERNS, dict)
        assert len(SectionDetector.SECTION_PATTERNS) > 0
        
        # Check for key sections
        expected_sections = ["Abstract", "Introduction", "Methodology", "Results", "Conclusion"]
        for section in expected_sections:
            assert section in SectionDetector.SECTION_PATTERNS
