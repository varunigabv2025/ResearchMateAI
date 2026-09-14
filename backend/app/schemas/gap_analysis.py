"""
Schemas for research gap analysis.
"""
from typing import List
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class AnalyzeGapsRequest(BaseModel):
    """Request schema for gap analysis."""
    paper_ids: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of 2-5 paper IDs to analyze for research gaps"
    )
    
    @field_validator('paper_ids')
    @classmethod
    def validate_paper_ids(cls, v):
        """Validate paper IDs."""
        if len(v) < 2:
            raise ValueError("At least 2 papers are required for gap analysis")
        if len(v) > 5:
            raise ValueError("Maximum 5 papers allowed for gap analysis")
        
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate paper IDs are not allowed")
        
        # Validate UUIDs
        for paper_id in v:
            try:
                UUID(paper_id)
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid UUID format: {paper_id}")
        
        return v


class ResearchGap(BaseModel):
    """A single research gap or contradiction."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Brief title of the research gap"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Detailed description of the research gap"
    )
    basis: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Evidence from comparison data supporting this gap"
    )


class AnalyzeGapsResponse(BaseModel):
    """Response schema for gap analysis."""
    paper_ids: List[str] = Field(
        ...,
        description="Paper IDs that were analyzed"
    )
    gaps: List[ResearchGap] = Field(
        ...,
        description="List of 0-3 suggested research gaps or contradictions"
    )
    disclaimer: str = Field(
        default="AI-suggested — verify against the literature yourself.",
        description="Disclaimer about AI-generated suggestions"
    )
    
    @field_validator('gaps')
    @classmethod
    def validate_gaps(cls, v):
        """Validate gaps list."""
        if len(v) > 3:
            raise ValueError("Maximum 3 research gaps allowed")
        return v
