"""
Comparison service for structured multi-paper extraction and comparison.
"""
import json
from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session

from app.models import Paper
from app.services.content_selector import ContentSelector
from app.services.llm_service import llm_service
from app.services.prompts import ComparisonExtractionPrompt
from app.schemas.comparison import PaperComparisonResult


class ComparisonService:
    """
    Service for comparing multiple research papers.
    Makes exactly one LLM extraction call per paper.
    """
    
    def __init__(self):
        self.content_selector = ContentSelector()
        self.llm_service = llm_service
        self.prompt_template = ComparisonExtractionPrompt()
    
    async def compare_papers(
        self,
        db: Session,
        paper_ids: List[UUID]
    ) -> List[PaperComparisonResult]:
        """
        Compare multiple papers by extracting structured information from each.
        
        Makes exactly one LLM call per paper for extraction.
        
        Args:
            db: Database session
            paper_ids: List of paper UUIDs to compare (2-5 papers)
            
        Returns:
            List of PaperComparisonResult objects
            
        Raises:
            ValueError: If papers not found or validation fails
            Exception: If extraction fails
        """
        results = []
        
        for paper_id in paper_ids:
            try:
                result = await self._extract_paper_info(db, paper_id)
                results.append(result)
            except Exception as e:
                # Re-raise with context about which paper failed
                raise Exception(f"Failed to extract information from paper {paper_id}: {str(e)}")
        
        return results
    
    async def _extract_paper_info(
        self,
        db: Session,
        paper_id: UUID
    ) -> PaperComparisonResult:
        """
        Extract structured information from a single paper.
        
        Args:
            db: Database session
            paper_id: Paper UUID
            
        Returns:
            PaperComparisonResult with extracted information
            
        Raises:
            ValueError: If paper not found or has no content
            Exception: If LLM extraction fails
        """
        # Get paper metadata
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise ValueError(f"Paper {paper_id} not found")
        
        # Get relevant content
        paper_content, source_chunks = self.content_selector.get_paper_content_for_comparison(
            db, paper_id
        )
        
        # Build extraction prompt
        messages = self.prompt_template.build_extraction_messages(
            paper_content, paper.original_filename
        )
        
        # Call LLM for extraction (exactly one call per paper)
        try:
            response = await self.llm_service.generate_chat_completion(
                messages=messages,
                temperature=0.1,  # Low temperature for factual extraction
                max_tokens=500    # Limit for structured output
            )
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
        
        # Parse and validate response
        extracted_data = self._parse_extraction_response(response, paper.original_filename)
        
        # Create result object
        result = PaperComparisonResult(
            paper_id=str(paper_id),
            filename=paper.original_filename,
            method=extracted_data["method"],
            dataset=extracted_data["dataset"],
            metric_result=extracted_data["metric_result"],
            limitation=extracted_data["limitation"]
        )
        
        return result
    
    def _parse_extraction_response(
        self,
        response: str,
        paper_filename: str
    ) -> Dict[str, str]:
        """
        Parse and validate LLM extraction response.
        
        Args:
            response: Raw LLM response
            paper_filename: Paper filename for error messages
            
        Returns:
            Dictionary with extracted fields
            
        Raises:
            Exception: If response is malformed or missing required fields
        """
        # Try to parse JSON
        try:
            # Clean up response (some LLMs might wrap in markdown code blocks)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response for {paper_filename}: {str(e)}")
        
        # Validate required fields
        required_fields = ["method", "dataset", "metric_result", "limitation"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise Exception(
                f"Missing required fields in extraction for {paper_filename}: {', '.join(missing_fields)}"
            )
        
        # Ensure all values are strings
        for field in required_fields:
            if not isinstance(data[field], str):
                data[field] = str(data[field])
        
        return data
    
    def validate_papers_exist(
        self,
        db: Session,
        paper_ids: List[UUID]
    ) -> tuple[bool, str]:
        """
        Validate that all requested papers exist and have content.
        
        Args:
            db: Database session
            paper_ids: List of paper UUIDs
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for paper_id in paper_ids:
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            
            if not paper:
                return False, f"Paper {paper_id} not found"
            
            # Check if paper has chunks (content extracted)
            if not paper.chunks:
                return False, f"Paper {paper_id} has no extracted content"
        
        return True, ""


# Global instance
comparison_service = ComparisonService()
