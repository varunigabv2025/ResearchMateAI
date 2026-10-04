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
                max_tokens=1000    # Increased limit for complete structured output
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
        Parse and validate LLM extraction response with robust error handling.
        
        Args:
            response: Raw LLM response
            paper_filename: Paper filename for error messages
            
        Returns:
            Dictionary with extracted fields
            
        Raises:
            Exception: If response is malformed or missing required fields
        """
        import re
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Try multiple parsing strategies
        data = None
        parse_errors = []
        original_response = response
        
        # Strategy 1: Direct JSON parsing after basic cleanup
        try:
            cleaned_response = response.strip()
            
            # Remove markdown code fences
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            parse_errors.append(f"Direct parse: {str(e)}")
            
            # Strategy 2: Try to find complete JSON object using brace counting
            try:
                # Find first opening brace
                start_idx = cleaned_response.find('{')
                if start_idx == -1:
                    parse_errors.append("Brace counting: No opening brace found")
                else:
                    # Count braces to find matching closing brace
                    brace_count = 0
                    end_idx = -1
                    in_string = False
                    escape_next = False
                    
                    for i in range(start_idx, len(cleaned_response)):
                        char = cleaned_response[i]
                        
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\':
                            escape_next = True
                            continue
                        
                        if char == '"':
                            in_string = not in_string
                            continue
                        
                        if not in_string:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i + 1
                                    break
                    
                    if end_idx > start_idx:
                        json_str = cleaned_response[start_idx:end_idx]
                        data = json.loads(json_str)
                    else:
                        parse_errors.append("Brace counting: Could not find matching closing brace")
            except json.JSONDecodeError as e2:
                parse_errors.append(f"Brace counting parse: {str(e2)}")
                
                # Strategy 3: Try line-by-line repair for common issues
                try:
                    if 'json_str' in locals():
                        # Fix common issues: unescaped newlines in strings
                        # This is aggressive but controlled
                        repaired = json_str
                        # Replace actual newlines inside quoted strings with spaces
                        lines = repaired.split('\n')
                        result_lines = []
                        in_value = False
                        
                        for line in lines:
                            stripped = line.strip()
                            # Check if this line looks like it's inside a string value
                            if in_value and not stripped.startswith('"'):
                                # Continuation of previous value - append to last line
                                if result_lines:
                                    result_lines[-1] = result_lines[-1].rstrip(',') + ' ' + stripped
                                continue
                            
                            result_lines.append(line)
                            
                            # Track if we're entering a string value
                            if ':' in stripped and '"' in stripped:
                                # Count quotes after the colon
                                colon_pos = stripped.find(':')
                                after_colon = stripped[colon_pos:]
                                quote_count = after_colon.count('"')
                                # Odd number means we're inside a string
                                in_value = (quote_count % 2 == 1)
                            else:
                                in_value = False
                        
                        repaired = '\n'.join(result_lines)
                        data = json.loads(repaired)
                except (json.JSONDecodeError, Exception) as e3:
                    parse_errors.append(f"Line repair: {str(e3)}")
        
        # If all strategies failed, log and raise
        if data is None:
            logger.error(f"Failed to parse LLM response for {paper_filename}")
            logger.error(f"Response preview (first 1000 chars): {original_response[:1000]}")
            logger.error(f"Parse attempts: {'; '.join(parse_errors)}")
            raise Exception(
                f"Failed to parse JSON response for {paper_filename}. "
                f"The LLM returned malformed JSON. Try regenerating or check LLM model configuration."
            )
        
        # Validate required fields
        required_fields = ["method", "dataset", "metric_result", "limitation"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.error(f"Missing fields in extraction for {paper_filename}: {missing_fields}")
            logger.error(f"Received data keys: {list(data.keys())}")
            raise Exception(
                f"Missing required fields in extraction for {paper_filename}: {', '.join(missing_fields)}"
            )
        
        # Ensure all values are strings and clean them
        for field in required_fields:
            if not isinstance(data[field], str):
                data[field] = str(data[field])
            # Clean up any remaining escaped characters and normalize whitespace
            data[field] = data[field].strip()
            # Collapse multiple spaces
            data[field] = re.sub(r'\s+', ' ', data[field])
        
        logger.info(f"Successfully extracted data from {paper_filename}")
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
