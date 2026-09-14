"""
Database models for papers and related entities.
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    # Fallback for testing without pgvector
    HAS_PGVECTOR = False
    Vector = None


class Paper(Base):
    """Model for research papers."""
    __tablename__ = "papers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    paper_metadata = Column("metadata", JSON, nullable=True)  # Use column name "metadata" but attribute "paper_metadata"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Paper(id={self.id}, filename={self.filename})>"


class PaperChunk(Base):
    """Model for text chunks extracted from papers."""
    __tablename__ = "paper_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    section = Column(String(100), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    char_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    paper = relationship("Paper", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PaperChunk(id={self.id}, paper_id={self.paper_id}, page={self.page_number}, section={self.section})>"


class Embedding(Base):
    """Model for vector embeddings."""
    __tablename__ = "embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("paper_chunks.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Vector column - uses pgvector if available, otherwise stored as JSON for testing
    if HAS_PGVECTOR and Vector is not None:
        # Use pgvector's Vector type for production
        # Dimension is set based on EMBEDDING_DIMENSION config (default 1536)
        from app.core.config import settings
        embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)
    else:
        # Fallback to JSON for testing without pgvector
        embedding = Column(JSON, nullable=False)
    
    model = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chunk = relationship("PaperChunk", back_populates="embedding")
    
    def __repr__(self):
        return f"<Embedding(id={self.id}, chunk_id={self.chunk_id}, model={self.model})>"
