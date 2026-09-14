"""API schemas."""
from app.schemas.paper import (
    PaperResponse,
    PaperDetailResponse,
    PaperUploadResponse,
    PaperListResponse,
    PaperChunkResponse,
    HealthResponse,
    QuestionRequest,
    QuestionResponse,
    SourceCitation,
)
from app.schemas.comparison import (
    ComparePapersRequest,
    ComparePapersResponse,
    PaperComparisonResult,
    ExtractedField,
    SourceReference,
)
from app.schemas.gap_analysis import (
    AnalyzeGapsRequest,
    ResearchGap,
    AnalyzeGapsResponse,
)

__all__ = [
    "PaperResponse",
    "PaperDetailResponse",
    "PaperUploadResponse",
    "PaperListResponse",
    "PaperChunkResponse",
    "HealthResponse",
    "QuestionRequest",
    "QuestionResponse",
    "SourceCitation",
    "ComparePapersRequest",
    "ComparePapersResponse",
    "PaperComparisonResult",
    "ExtractedField",
    "SourceReference",
    "AnalyzeGapsRequest",
    "ResearchGap",
    "AnalyzeGapsResponse",
]
