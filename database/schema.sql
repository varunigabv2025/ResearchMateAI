-- ResearchMate AI Database Schema
-- PostgreSQL with pgvector extension

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Papers table: stores uploaded research papers
CREATE TABLE IF NOT EXISTS papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    page_count INTEGER NOT NULL,
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Paper chunks table: stores extracted text chunks with metadata
CREATE TABLE IF NOT EXISTS paper_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    section VARCHAR(100),
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paper FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
);

-- Embeddings table: stores vector embeddings for chunks
-- The vector dimension should match your embedding model (e.g., 1536 for OpenAI ada-002)
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES paper_chunks(id) ON DELETE CASCADE,
    embedding vector(1536) NOT NULL,
    model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chunk FOREIGN KEY (chunk_id) REFERENCES paper_chunks(id) ON DELETE CASCADE,
    CONSTRAINT unique_chunk_embedding UNIQUE (chunk_id)
);

-- Indexes for performance

-- Index on paper_id for fast chunk retrieval
CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_id ON paper_chunks(paper_id);

-- Index on section for filtering by paper section
CREATE INDEX IF NOT EXISTS idx_paper_chunks_section ON paper_chunks(section);

-- Index on page_number for page-based queries
CREATE INDEX IF NOT EXISTS idx_paper_chunks_page ON paper_chunks(page_number);

-- Composite index for paper + page queries
CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_page ON paper_chunks(paper_id, page_number);

-- Index on chunk_id for fast embedding lookup
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);

-- HNSW index for fast vector similarity search
-- Using cosine distance (most common for text embeddings)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_cosine 
ON embeddings USING hnsw (embedding vector_cosine_ops);

-- Alternative: L2 distance index (uncomment if needed)
-- CREATE INDEX IF NOT EXISTS idx_embeddings_vector_l2 
-- ON embeddings USING hnsw (embedding vector_l2_ops);

-- Function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at on papers table
CREATE TRIGGER update_papers_updated_at 
    BEFORE UPDATE ON papers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE papers IS 'Stores metadata about uploaded research papers';
COMMENT ON TABLE paper_chunks IS 'Stores extracted text chunks from papers with section and page metadata';
COMMENT ON TABLE embeddings IS 'Stores vector embeddings for semantic search';
COMMENT ON COLUMN embeddings.embedding IS 'Vector embedding for similarity search (dimension must match embedding model)';
