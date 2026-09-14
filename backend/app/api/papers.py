"""
API endpoints for paper management.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.models import Paper, PaperChunk, Embedding
from app.schemas import (
    PaperResponse,
    PaperDetailResponse,
    PaperUploadResponse,
    PaperListResponse,
    QuestionRequest,
    QuestionResponse,
    SourceCitation,
    ComparePapersRequest,
    ComparePapersResponse,
    AnalyzeGapsRequest,
    AnalyzeGapsResponse,
)
from app.services import PDFExtractor, SectionDetector, TextChunker, embedding_service

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("/upload", response_model=PaperUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> PaperUploadResponse:
    """
    Upload and process a research paper PDF.
    
    Steps:
    1. Validate PDF file
    2. Save to disk
    3. Extract text with page numbers
    4. Detect sections
    5. Create chunks with metadata
    6. Store in database
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_id = uuid.uuid4()
    filename = f"{file_id}.pdf"
    file_path = upload_dir / filename
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Validate PDF
    is_valid, error_msg = PDFExtractor.validate_pdf(str(file_path))
    if not is_valid:
        # Clean up file
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    try:
        # Extract text with page numbers
        pages_data = PDFExtractor.extract_text_with_pages(str(file_path))
        page_count = len(pages_data)
        
        # Detect sections
        pages_with_sections = SectionDetector.detect_sections_in_pages(pages_data)
        sections_detected = SectionDetector.get_detected_sections(pages_with_sections)
        
        # Extract PDF metadata
        pdf_metadata = PDFExtractor.extract_metadata(str(file_path))
        
        # Create paper record
        paper = Paper(
            filename=filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            page_count=page_count,
            processed=True,
            paper_metadata=pdf_metadata
        )
        
        db.add(paper)
        db.flush()  # Get paper ID without committing
        
        # Create chunks with metadata
        chunks_data = TextChunker.create_chunks_with_metadata(
            paper_id=paper.id,
            pages_with_sections=pages_with_sections
        )
        
        # Save chunks to database
        chunk_objects = []
        for chunk_data in chunks_data:
            chunk = PaperChunk(**chunk_data)
            db.add(chunk)
            chunk_objects.append(chunk)
        
        db.flush()  # Flush to get chunk IDs
        
        # Generate embeddings for all chunks
        # Mark paper as not fully processed until embeddings are done
        paper.processed = False
        paper.processing_error = None
        
        try:
            # Extract texts for embedding
            chunk_texts = [chunk.text for chunk in chunk_objects]
            
            # Generate embeddings (async call within sync context)
            embeddings = await embedding_service.generate_embeddings_batch(chunk_texts)
            
            # Store embeddings
            for chunk_obj, embedding_vector in zip(chunk_objects, embeddings):
                embedding_record = Embedding(
                    chunk_id=chunk_obj.id,
                    embedding=embedding_vector,
                    model=embedding_service.model
                )
                db.add(embedding_record)
            
            # Mark paper as fully processed
            paper.processed = True
            
        except Exception as embed_error:
            # Store error but keep the paper and chunks
            paper.processed = False
            paper.processing_error = f"Embedding generation failed: {str(embed_error)}"
            # Continue - paper is uploaded but not ready for Q&A
        
        db.commit()
        db.refresh(paper)
        
        # Prepare response message
        if paper.processed:
            message = "Paper uploaded and processed successfully. Ready for Q&A."
        else:
            message = f"Paper uploaded but processing incomplete: {paper.processing_error}"
        
        return PaperUploadResponse(
            id=paper.id,
            filename=paper.original_filename,
            page_count=page_count,
            sections_detected=sections_detected,
            message=message
        )
        
    except Exception as e:
        db.rollback()
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )


@router.get("/", response_model=PaperListResponse)
def list_papers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> PaperListResponse:
    """
    List all uploaded papers with pagination.
    """
    papers = db.query(Paper).order_by(Paper.upload_timestamp.desc()).offset(skip).limit(limit).all()
    total = db.query(Paper).count()
    
    return PaperListResponse(
        papers=[PaperResponse.model_validate(p) for p in papers],
        total=total
    )


@router.get("/{paper_id}", response_model=PaperDetailResponse)
def get_paper(
    paper_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> PaperDetailResponse:
    """
    Get detailed information about a specific paper.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )
    
    # Get unique sections from chunks
    chunks = db.query(PaperChunk).filter(PaperChunk.paper_id == paper_id).all()
    sections_detected = []
    seen_sections = set()
    
    for chunk in chunks:
        if chunk.section and chunk.section not in seen_sections:
            sections_detected.append(chunk.section)
            seen_sections.add(chunk.section)
    
    # Convert to response model
    response = PaperDetailResponse.model_validate(paper)
    response.sections_detected = sections_detected
    
    return response


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paper(
    paper_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a paper and all its associated data.
    Cascade deletion will remove chunks and embeddings automatically.
    """
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )
    
    # Delete file from disk
    if os.path.exists(paper.file_path):
        try:
            os.remove(paper.file_path)
        except Exception as e:
            # Log but don't fail the request
            print(f"Warning: Failed to delete file {paper.file_path}: {str(e)}")
    
    # Delete from database (cascade will handle chunks and embeddings)
    db.delete(paper)
    db.commit()


# Q&A Endpoint

@router.post("/{paper_id}/ask", response_model=QuestionResponse)
async def ask_question(
    paper_id: uuid.UUID,
    request: QuestionRequest,
    db: Session = Depends(get_db)
) -> QuestionResponse:
    """
    Ask a question about a specific paper and get a grounded answer with citations.
    
    The answer is generated ONLY from the paper's content, with citations to
    specific pages and sections.
    
    Args:
        paper_id: UUID of the paper to query
        request: Question request containing the question text
        db: Database session
        
    Returns:
        Answer with source citations
        
    Raises:
        404: Paper not found
        400: Paper not fully processed or question invalid
        500: Embedding/LLM API failure
    """
    from app.services import retrieval_service, llm_service, GroundedQAPrompt
    
    question = request.question.strip()
    
    # Validate question
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )
    
    # Validate paper exists
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with id {paper_id} not found"
        )
    
    # Check if paper is fully processed
    if not paper.processed:
        error_msg = "Paper has not been fully processed"
        if paper.processing_error:
            error_msg += f": {paper.processing_error}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    try:
        # Retrieve relevant chunks
        relevant_chunks = await retrieval_service.retrieve_relevant_chunks(
            db=db,
            paper_id=paper_id,
            question=question,
            top_k=5,
            similarity_threshold=0.7
        )
        
        # Check if we have sufficient context
        has_sufficient_context = GroundedQAPrompt.has_sufficient_context(
            relevant_chunks, min_chunks=1
        )
        
        if not has_sufficient_context:
            # Return insufficient context response
            return QuestionResponse(
                answer=GroundedQAPrompt.get_insufficient_context_response(),
                sources=[],
                paper_id=str(paper_id),
                question=question,
                has_sufficient_context=False
            )
        
        # Build prompt with retrieved chunks
        messages = GroundedQAPrompt.build_messages(question, relevant_chunks)
        
        # Generate answer from LLM
        try:
            answer = await llm_service.generate_chat_completion(messages)
        except Exception as llm_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate answer: {str(llm_error)}"
            )
        
        # Format sources with citation information
        sources = _format_sources(relevant_chunks)
        
        return QuestionResponse(
            answer=answer,
            sources=sources,
            paper_id=str(paper_id),
            question=question,
            has_sufficient_context=True
        )
        
    except ValueError as e:
        # Handle validation errors from retrieval service
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )


def _format_sources(chunks: List[Dict]) -> List[SourceCitation]:
    """
    Format retrieved chunks into source citations.
    Deduplicates citations from the same page/section.
    
    Args:
        chunks: Retrieved chunks with metadata
        
    Returns:
        List of SourceCitation objects
    """
    from app.schemas import SourceCitation
    
    if not chunks:
        return []
    
    # Track unique page/section combinations to avoid duplicates
    seen_citations = set()
    sources = []
    
    for chunk in chunks:
        page = chunk.get('page_number')
        section = chunk.get('section')
        chunk_id = chunk.get('chunk_id')
        similarity = chunk.get('similarity', 0.0)
        
        # Create citation key for deduplication
        citation_key = (page, section)
        
        # Only add if we haven't seen this page/section combination
        if citation_key not in seen_citations:
            seen_citations.add(citation_key)
            
            sources.append(SourceCitation(
                chunk_id=chunk_id,
                page_number=page,
                section=section,
                similarity=similarity
            ))
    
    return sources


# Comparison Endpoint

@router.post("/compare", response_model=ComparePapersResponse)
async def compare_papers(
    request: ComparePapersRequest,
    db: Session = Depends(get_db)
) -> ComparePapersResponse:
    """
    Compare 2-5 research papers by extracting structured information.
    
    Extracts method, dataset, metrics/results, and limitations from each paper
    based only on the paper's content.
    
    Args:
        request: Comparison request with 2-5 paper IDs
        db: Database session
        
    Returns:
        Structured comparison results for all papers
        
    Raises:
        400: Invalid request (wrong number of papers, duplicates, missing papers)
        500: Extraction or LLM failure
    """
    from app.services import comparison_service
    from uuid import UUID
    
    # Convert string IDs to UUIDs
    try:
        paper_uuids = [UUID(pid) for pid in request.paper_ids]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid paper ID format: {str(e)}"
        )
    
    # Validate papers exist and have content
    is_valid, error_msg = comparison_service.validate_papers_exist(db, paper_uuids)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Extract information from each paper
    try:
        comparison_results = await comparison_service.compare_papers(db, paper_uuids)
    except ValueError as e:
        # Validation errors (paper not found, no content, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # LLM or extraction errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}"
        )
    
    return ComparePapersResponse(
        papers=comparison_results,
        total_papers=len(comparison_results)
    )



@router.post("/gaps", response_model=AnalyzeGapsResponse)
async def analyze_research_gaps(
    request: AnalyzeGapsRequest,
    db: Session = Depends(get_db)
) -> AnalyzeGapsResponse:
    """
    Analyze research gaps and contradictions from multiple papers.
    
    This endpoint:
    1. Validates the paper IDs (2-5 papers, no duplicates, valid UUIDs)
    2. Verifies all papers exist and have content
    3. Uses Feature 2 comparison service to get structured data
    4. Makes ONE LLM call to analyze gaps from comparison data
    5. Returns 0-3 suggested research gaps with disclaimer
    
    Args:
        request: Gap analysis request with 2-5 paper IDs
        db: Database session
        
    Returns:
        Research gap suggestions with disclaimer
        
    Raises:
        400: Invalid request (wrong number of papers, duplicates, missing papers)
        500: Analysis or LLM failure
    """
    from app.services import gap_analysis_service
    from uuid import UUID
    
    # Convert string IDs to UUIDs
    try:
        paper_uuids = [UUID(pid) for pid in request.paper_ids]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid paper ID format: {str(e)}"
        )
    
    # Validate papers exist and have content (reuse comparison service validation)
    from app.services import comparison_service
    is_valid, error_msg = comparison_service.validate_papers_exist(db, paper_uuids)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Analyze gaps using Feature 2 comparison data
    try:
        gaps = await gap_analysis_service.analyze_gaps(db, paper_uuids)
    except ValueError as e:
        # Validation errors (paper not found, no content, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # LLM or analysis errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gap analysis failed: {str(e)}"
        )
    
    # Return response with disclaimer (always included)
    return AnalyzeGapsResponse(
        paper_ids=request.paper_ids,
        gaps=gaps,
        disclaimer="AI-suggested — verify against the literature yourself."
    )
