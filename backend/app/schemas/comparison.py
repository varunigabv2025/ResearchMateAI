"""
Pydantic schemas for paper comparison.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID


class ComparePapersRequest(BaseModel):
    """Request schema for comparing papers."""
    paper_ids: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of 2-5 paper IDs to compare"
    )
    
    @field_validator('paper_ids')
    @classmethod
    def validate_paper_ids(cls, v):
        """Validate paper IDs."""
        if len(v) < 2:
            raise ValueError("At least 2 papers are required for comparison")
        if len(v) > 5:
            raise ValueError("Maximum 5 papers can be compared")
        
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate paper IDs are not allowed")
        
        # Validate UUIDs
        for paper_id in v:
            try:
                UUID(paper_id)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {paper_id}")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "paper_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "223e4567-e89b-12d3-a456-426614174001",
                    "323e4567-e89b-12d3-a456-426614174002"
                ]
            }
        }
    }


class SourceReference(BaseModel):
    """Reference to source chunk."""
    page: int
    section: Optional[str] = None
    chunk_id: str


class ExtractedField(BaseModel):
    """Extracted field with optional source references."""
    value: str
    sources: Optional[List[SourceReference]] = None


class PaperComparisonResult(BaseModel):
    """Structured comparison result for a single paper."""
    paper_id: str
    filename: str
    method: str = Field(..., description="Methodology, model, or approach used")
    dataset: str = Field(..., description="Dataset(s), benchmark(s), or data sources")
    metric_result: str = Field(..., description="Key evaluation metrics or results")
    limitation: str = Field(..., description="Limitations stated in the paper")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "paper_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "transformer_paper.pdf",
                "method": "Transformer architecture with multi-head self-attention",
                "dataset": "WMT 2014 English-to-German and English-to-French",
                "metric_result": "BLEU score of 28.4 on WMT 2014 EN-DE",
                "limitation": "Requires large amounts of training data and computational resources"
            }
        }
    }


class ComparePapersResponse(BaseModel):
    """Response schema for paper comparison."""
    papers: List[PaperComparisonResult]
    total_papers: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "papers": [
                    {
                        "paper_id": "123e4567-e89b-12d3-a456-426614174000",
                        "filename": "transformer_paper.pdf",
                        "method": "Transformer architecture with multi-head self-attention",
                        "dataset": "WMT 2014 English-to-German and English-to-French",
                        "metric_result": "BLEU score of 28.4 on WMT 2014 EN-DE",
                        "limitation": "Requires large amounts of training data"
                    },
                    {
                        "paper_id": "223e4567-e89b-12d3-a456-426614174001",
                        "filename": "bert_paper.pdf",
                        "method": "Bidirectional encoder representations from transformers",
                        "dataset": "BooksCorpus and English Wikipedia",
                        "metric_result": "11 tasks including GLUE benchmark improvements",
                        "limitation": "Pre-training is computationally expensive"
                    }
                ],
                "total_papers": 2
            }
        }
    }
