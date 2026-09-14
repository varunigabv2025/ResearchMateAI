"""
Gap analysis service for identifying research gaps from paper comparisons.
"""
import json
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.comparison_service import comparison_service
from app.services.llm_service import llm_service
from app.services.prompts import GapAnalysisPrompt
from app.schemas.gap_analysis import ResearchGap


class GapAnalysisService:
    """
    Service for analyzing research gaps from paper comparison data.
    Makes exactly ONE LLM call per gap analysis request.
    """
    
    def __init__(self):
        self.comparison_service = comparison_service
        self.llm_service = llm_service
        self.prompt_template = GapAnalysisPrompt()
    
    async def analyze_gaps(
        self,
        db: Session,
        paper_ids: List[UUID]
    ) -> List[ResearchGap]:
        """
        Analyze research gaps from multiple papers.
        
        This method:
        1. Uses Feature 2 comparison service to get structured data
        2. Makes exactly ONE LLM call with comparison data
        3. Parses and validates the gap suggestions
        
        Args:
            db: Database session
            paper_ids: List of paper UUIDs to analyze (2-5 papers)
            
        Returns:
            List of ResearchGap objects (0-3 gaps)
            
        Raises:
            ValueError: If papers not found or validation fails
            Exception: If gap analysis fails
        """
        # Step 1: Get structured comparison data from Feature 2
        # This reuses the existing comparison service - no duplication
        try:
            comparison_results = await self.comparison_service.compare_papers(
                db, paper_ids
            )
        except Exception as e:
            raise Exception(f"Failed to get comparison data: {str(e)}")
        
        # Convert comparison results to dict format for prompt
        comparison_data = [
            {
                "paper_id": result.paper_id,
                "filename": result.filename,
                "method": result.method,
                "dataset": result.dataset,
                "metric_result": result.metric_result,
                "limitation": result.limitation
            }
            for result in comparison_results
        ]
        
        # Step 2: Build gap analysis prompt with comparison data
        messages = self.prompt_template.build_analysis_messages(comparison_data)
        
        # Step 3: Make exactly ONE LLM call for gap analysis
        try:
            response = await self.llm_service.generate_chat_completion(
                messages=messages,
                temperature=0.3,  # Slightly higher than extraction for reasoning
                max_tokens=1500   # Allow space for 2-3 detailed gaps
            )
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
        
        # Step 4: Parse and validate response
        gaps = self._parse_gaps_response(response)
        
        return gaps
    
    def _parse_gaps_response(self, response: str) -> List[ResearchGap]:
        """
        Parse and validate LLM gap analysis response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of ResearchGap objects (0-3 gaps)
            
        Raises:
            Exception: If response is malformed or invalid
        """
        # Clean up response (handle markdown code blocks)
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        # Parse JSON
        try:
            gaps_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")
        
        # Validate that it's a list
        if not isinstance(gaps_data, list):
            raise Exception(f"Expected JSON array, got {type(gaps_data).__name__}")
        
        # Empty list is valid (no gaps found)
        if len(gaps_data) == 0:
            return []
        
        # Validate max 3 gaps
        if len(gaps_data) > 3:
            # Truncate to first 3 gaps rather than failing
            gaps_data = gaps_data[:3]
        
        # Validate and convert each gap
        validated_gaps = []
        for i, gap_dict in enumerate(gaps_data):
            # Validate format
            if not self.prompt_template.validate_gap_format(gap_dict):
                raise Exception(
                    f"Gap {i+1} missing required fields or has invalid format. "
                    f"Required: title, description, basis (all non-empty strings)"
                )
            
            # Create ResearchGap object (will validate field lengths via Pydantic)
            try:
                gap = ResearchGap(
                    title=gap_dict["title"].strip(),
                    description=gap_dict["description"].strip(),
                    basis=gap_dict["basis"].strip()
                )
                validated_gaps.append(gap)
            except Exception as e:
                raise Exception(f"Gap {i+1} validation failed: {str(e)}")
        
        return validated_gaps


# Global instance
gap_analysis_service = GapAnalysisService()
