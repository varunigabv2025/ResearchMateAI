"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class PaperChunkResponse(BaseModel):
    """Response schema for a paper chunk."""
    id: UUID
    paper_id: UUID
    page_number: int
    section: Optional[str] = None
    chunk_index: int
    text: str
    char_count: int
    
    model_config = ConfigDict(from_attributes=True)


class PaperResponse(BaseModel):
    """Response schema for a paper."""
    id: UUID
    filename: str
    original_filename: str
    file_size_bytes: int
    page_count: int
    upload_timestamp: datetime
    processed: bool
    processing_error: Optional[str] = None
    paper_metadata: Optional[dict] = Field(None, alias="metadata")  # Accept "metadata" in API but use "paper_metadata" internally
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaperDetailResponse(PaperResponse):
    """Detailed paper response including sections detected."""
    sections_detected: Optional[List[str]] = None


class PaperUploadResponse(BaseModel):
    """Response after uploading a paper."""
    id: UUID
    filename: str
    page_count: int
    sections_detected: List[str]
    message: str = "Paper uploaded and processed successfully"


class PaperListResponse(BaseModel):
    """Response for listing papers."""
    papers: List[PaperResponse]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    app_name: str
    version: str


# Q&A Schemas

class QuestionRequest(BaseModel):
    """Request schema for asking a question about a paper."""
    question: str = Field(..., min_length=1, max_length=1000, description="Question about the paper")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "What methodology does the paper use?"
            }
        }
    )


class SourceCitation(BaseModel):
    """Citation information for a source chunk."""
    chunk_id: str
    page_number: int
    section: Optional[str] = None
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score between 0 and 1")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chunk_id": "123e4567-e89b-12d3-a456-426614174000",
                "page_number": 7,
                "section": "Methodology",
                "similarity": 0.89
            }
        }
    )


class QuestionResponse(BaseModel):
    """Response schema for a Q&A answer."""
    answer: str = Field(..., description="Answer generated from the paper")
    sources: List[SourceCitation] = Field(..., description="Source citations supporting the answer")
    paper_id: str
    question: str
    has_sufficient_context: bool = Field(..., description="Whether sufficient context was found to answer")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer": "The authors use a transformer-based architecture with attention mechanisms...",
                "sources": [
                    {
                        "chunk_id": "123e4567-e89b-12d3-a456-426614174000",
                        "page_number": 7,
                        "section": "Methodology",
                        "similarity": 0.89
                    },
                    {
                        "chunk_id": "223e4567-e89b-12d3-a456-426614174001",
                        "page_number": 9,
                        "section": "Experiments",
                        "similarity": 0.82
                    }
                ],
                "paper_id": "323e4567-e89b-12d3-a456-426614174002",
                "question": "What methodology does the paper use?",
                "has_sufficient_context": True
            }
        }
    )
