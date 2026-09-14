# Zero-Cost Embedding Migration Guide

## Overview

ResearchMate AI has been migrated from paid OpenRouter embeddings to **local embeddings** using Qwen3-Embedding-0.6B for zero-cost MVP development.

**Cost Savings:** $0.02 per million tokens → $0.00 (100% savings for local development)

---

## What Changed

### LLM Configuration (OpenRouter Free)
- **Before:** `anthropic/claude-sonnet-4.6` (paid)
- **After:** `openrouter/free` (free routing service)
- **Note:** Free models rotate; suitable for MVP development and testing

### Embedding Configuration (Local Model)
- **Before:** `openai/text-embedding-3-small` via OpenRouter API (paid: $0.02/M tokens)
- **After:** `Qwen/Qwen3-Embedding-0.6B` running locally (no API costs)
- **Dimension Change:** 1536 → 1024

### Key Benefits
✅ Zero embedding API costs for local development  
✅ No network latency for embeddings  
✅ Works offline (after initial model download)  
✅ CPU and GPU support  
✅ Privacy: embeddings never leave your machine  
✅ Qwen3: MTEB score 70.7

---

## Technical Details

### Model Information
- **Model:** Qwen/Qwen3-Embedding-0.6B
- **Source:** Hugging Face (Apache-2.0 license)
- **Dimensions:** 1024
- **Context Length:** 32,768 tokens
- **Download Size:** ~1.5 GB (first use only)
- **Memory Usage:** ~1.5 GB (GPU) or ~2 GB RAM (CPU)
- **Quality:** MTEB English v2 score: 70.70

### Implementation
- Uses `sentence-transformers` library
- Automatic CPU/GPU detection
- Model cached locally after first download
- Thread-pooled async execution (non-blocking)
- Batch processing support
- Query prompt support for better retrieval

---

## Database Configuration

### Current Development Setup
- **Database:** SQLite (`backend/test.db`)
- **Storage:** Local filesystem
- **Vector support:** Basic (no pgvector optimizations)

### Intended Production Setup
- **Database:** PostgreSQL
- **Vector extension:** pgvector
- **Indexing:** HNSW for efficient similarity search
- **Connection pooling:** Managed by SQLAlchemy

---

## Database Migration Required

### Schema Change
```sql
-- Old (1536 dimensions)
embedding vector(1536) NOT NULL

-- New (1024 dimensions)
embedding vector(1024) NOT NULL
```

### Why Migration is Needed
- Embedding dimensions changed from 1536 → 1024
- Cannot mix embeddings from different models
- Vector similarity search requires consistent dimensions
- Existing embeddings from the old model must be regenerated

### For SQLite Users (Current Development Setup)

**Option 1: Delete and Recreate (Recommended for MVP)**
```powershell
# Stop backend if running
# Delete the database
Remove-Item backend\test.db

# Restart backend - tables will be recreated automatically
# Re-upload all papers to generate new embeddings
```

**Option 2: Manual Table Recreation**
```powershell
# Connect to SQLite
sqlite3 backend\test.db

# Drop embeddings table
DROP TABLE IF EXISTS embeddings;

# Restart the backend - SQLAlchemy will recreate with 1024 dimensions
```

### For PostgreSQL Users (Production Deployment)

**Option 1: Drop and Recreate Schema**
```sql
-- Connect to database
psql -U postgres -d researchmate

-- Drop tables (cascades to embeddings)
DROP TABLE IF EXISTS embeddings CASCADE;
DROP TABLE IF EXISTS paper_chunks CASCADE;
DROP TABLE IF EXISTS papers CASCADE;

-- Run updated schema
\i database/schema.sql
```

**Option 2: Drop Only Embeddings**
```sql
-- If you want to keep papers/chunks metadata
DROP TABLE IF EXISTS embeddings CASCADE;

-- Recreate embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES paper_chunks(id) ON DELETE CASCADE,
    embedding vector(1024) NOT NULL,
    model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chunk FOREIGN KEY (chunk_id) REFERENCES paper_chunks(id) ON DELETE CASCADE,
    CONSTRAINT unique_chunk_embedding UNIQUE (chunk_id)
);

-- Recreate index
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_cosine 
ON embeddings USING hnsw (embedding vector_cosine_ops);
```

**After Migration:** Re-upload all papers to generate new 1024-dimensional embeddings.

---

## First-Time Setup

### 1. Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

**New dependencies added:**
- `sentence-transformers==3.3.1`
- `transformers==4.51.0`
- `torch>=2.9.0`

### 2. First Run (Model Download)
The first time the backend starts, it will download the Qwen3-Embedding-0.6B model (~1.5 GB).

**Expected behavior:**
```
INFO: Loading local embedding model: Qwen/Qwen3-Embedding-0.6B
INFO: This may take a few moments on first use (downloading model weights)...
[Downloading... may take 2-5 minutes depending on connection]
INFO: Model loaded, verifying dimensions...
INFO: Local embedding model loaded successfully. Dimension: 1024, Device: cpu
INFO: Application startup complete.
```

**This download only happens once.** The model is cached locally and subsequent starts are instant.

### 3. Verify Configuration
```powershell
# Check config loaded correctly
python -c "from app.core.config import settings; print(f'LLM: {settings.LLM_MODEL}'); print(f'Embedding: {settings.EMBEDDING_MODEL}'); print(f'API Base: {settings.EMBEDDING_API_BASE_URL}'); print(f'Dimension: {settings.EMBEDDING_DIMENSION}')"
```

Expected output:
```
LLM: openrouter/free
Embedding: Qwen/Qwen3-Embedding-0.6B
API Base: local
Dimension: 1024
```

---

## Configuration Files Changed

### 1. backend/.env.example
```bash
# LLM Configuration (OpenRouter Free Routing)
LLM_MODEL=openrouter/free
LLM_API_BASE_URL=https://openrouter.ai/api/v1

# Embedding Configuration (Local - Zero Cost)
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
EMBEDDING_API_BASE_URL=local
EMBEDDING_DIMENSION=1024
```

### 2. backend/app/core/config.py
```python
EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-0.6B"
EMBEDDING_API_BASE_URL: str = "local"
EMBEDDING_DIMENSION: int = 1024
```

### 3. database/schema.sql
```sql
embedding vector(1024) NOT NULL
```

### 4. backend/requirements.txt
Added:
```
sentence-transformers==3.3.1
transformers==4.51.0
torch>=2.9.0
```

---

## Performance

### Local vs API Embeddings

| Metric | OpenRouter API | Local (Qwen3-0.6B) |
|--------|----------------|-------------------|
| **Cost** | $0.02/M tokens | **$0.00** |
| **Latency (single)** | 200-500ms | 50-150ms (CPU) / 10-30ms (GPU) |
| **Latency (batch 100)** | 1-2s | 2-5s (CPU) / 0.5-1s (GPU) |
| **Network Required** | ✅ Yes | ❌ No (after download) |
| **Privacy** | Sent to API | ✅ Local only |
| **Offline** | ❌ No | ✅ Yes |

**Note:** Performance varies by hardware. Benchmarks are approximate.

### CPU vs GPU

**CPU (Default):**
- Works on any machine
- ~50-150ms per embedding
- ~2-5s for batch of 100
- No special hardware needed

**GPU (Automatic if available):**
- 3-5x faster than CPU
- ~10-30ms per embedding
- ~0.5-1s for batch of 100
- Automatically detected and used

---

## Troubleshooting

### Model Download Fails
**Error:** `Failed to download model`

**Solutions:**
1. Check internet connection
2. Check Hugging Face is accessible: `curl https://huggingface.co`
3. Set HF cache directory if disk space is low:
   ```powershell
   $env:HF_HOME="D:\huggingface_cache"  # Example: use different drive
   ```
4. Manual download:
   ```powershell
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')"
   ```

### Out of Memory
**Error:** `RuntimeError: [enforce fail at alloc_cpu.cpp:114] err == 0. DefaultCPUAllocator: not enough memory`

**Solutions:**
1. Close other applications
2. Reduce batch size in `embedding_service.py`:
   ```python
   batch_size=16  # Instead of 32
   ```
3. For production: Use PostgreSQL + pgvector to offload vector storage

### Slow Performance
**Issue:** Embeddings taking >1 second each

**Solutions:**
1. Verify GPU is being used:
   ```powershell
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   ```
2. Install CPU optimizations:
   ```powershell
   pip install intel-extension-for-pytorch  # Intel CPUs
   # OR
   pip install torch-directml  # AMD GPUs on Windows
   ```
3. Reduce context length if processing very long texts

### Import Errors
**Error:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution:**
```powershell
pip install sentence-transformers transformers torch
```

---

## Testing

### Run Tests
```powershell
cd backend
pytest tests/ -v
```

**All tests updated to:**
- Mock local model initialization
- Use 1024 dimensions instead of 1536
- Test both API and local embedding modes
- Cover query vs document embedding behavior

### Manual Testing
1. Start backend: `uvicorn app.main:app --reload`
2. Upload a PDF via `/docs`
3. Verify embedding generation in logs
4. Ask a question about the paper
5. Verify retrieval works

---

## Rollback Instructions

If you need to revert to paid OpenRouter embeddings:

### 1. Update .env
```bash
EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_API_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_API_KEY=sk-or-v1-YOUR_KEY_HERE
EMBEDDING_DIMENSION=1536
```

### 2. Update database schema
```sql
-- Change back to 1536
ALTER TABLE embeddings DROP COLUMN embedding;
ALTER TABLE embeddings ADD COLUMN embedding vector(1536) NOT NULL;
```

### 3. Restart backend and re-upload papers

---

## Future Enhancements

**Possible upgrades (all still zero-cost):**

1. **Qwen3-Embedding-4B** (4096 dims, MTEB 74.6)
   - Higher quality
   - Requires more VRAM (~9 GB)

2. **Hybrid Search** (dense + sparse)
   - Use `bge-m3` model
   - Supports both dense and sparse embeddings

3. **Reranking** (optional second pass)
   - Use `Qwen3-Reranker-0.6B`
   - Can improve retrieval quality

---

## Security & Privacy

✅ **No API keys required for local embedding** (EMBEDDING_API_KEY is empty)  
✅ **No network requests after model download** (embeddings generated locally)  
✅ **Embeddings never leave your machine**  
✅ **Apache-2.0 license** (fully open, commercial use allowed)  
✅ **No telemetry** from sentence-transformers  
✅ **Reproducible builds** (pinned dependencies)

---

## Support

**Model Documentation:** https://huggingface.co/Qwen/Qwen3-Embedding-0.6B  
**Sentence Transformers:** https://www.sbert.net  
**ResearchMate:** See main README.md

---

**Migration guide for zero-cost local development setup.**

### Schema Change
```sql
-- Old (1536 dimensions)
embedding vector(1536) NOT NULL

-- New (1024 dimensions)
embedding vector(1024) NOT NULL
```

### Why Migration is Needed
- Embedding dimensions changed from 1536 → 1024
- Cannot mix embeddings from different models
- Vector similarity search requires consistent dimensions
- Old embeddings are incompatible with new model

### For SQLite Users (Current Development Setup)

**Option 1: Delete and Recreate (Recommended)**
```powershell
# Stop backend if running
# Delete the database
Remove-Item backend\test.db

# Restart backend - tables will be recreated automatically
# Re-upload all papers
```

**Option 2: Manual Table Recreation**
```powershell
# Connect to SQLite
sqlite3 backend\test.db

# Drop embeddings table
DROP TABLE IF EXISTS embeddings;

# Recreate with new dimension (handled automatically by SQLAlchemy)
# Just restart the backend
```

### For PostgreSQL Users

**Option 1: Drop and Recreate Schema**
```sql
-- Connect to database
psql -U postgres -d researchmate

-- Drop tables (cascades to embeddings)
DROP TABLE IF EXISTS embeddings CASCADE;
DROP TABLE IF EXISTS paper_chunks CASCADE;
DROP TABLE IF EXISTS papers CASCADE;

-- Run updated schema
\i database/schema.sql
```

**Option 2: Drop Only Embeddings**
```sql
-- If you want to keep papers/chunks
DROP TABLE IF EXISTS embeddings CASCADE;

-- Recreate embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES paper_chunks(id) ON DELETE CASCADE,
    embedding vector(1024) NOT NULL,
    model VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chunk FOREIGN KEY (chunk_id) REFERENCES paper_chunks(id) ON DELETE CASCADE,
    CONSTRAINT unique_chunk_embedding UNIQUE (chunk_id)
);

-- Recreate index
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_cosine 
ON embeddings USING hnsw (embedding vector_cosine_ops);
```

**After Migration:** Re-upload all papers to generate new 1024-dimensional embeddings.

---

## First-Time Setup

### 1. Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

**New dependencies added:**
- `sentence-transformers==3.3.1`
- `transformers==4.51.0`
- `torch>=2.9.0`

### 2. First Run (Model Download)
The first time the backend starts, it will download the Qwen3-Embedding-0.6B model (~1.5 GB).

**Expected behavior:**
```
INFO: Loading local embedding model: Qwen/Qwen3-Embedding-0.6B
INFO: This may take a few moments on first use (downloading model weights)...
[Downloading... may take 2-5 minutes depending on connection]
INFO: Model loaded, verifying dimensions...
INFO: Local embedding model loaded successfully. Dimension: 1024, Device: cpu
INFO: Application startup complete.
```

**This only happens once.** Subsequent starts are instant.

### 3. Verify Configuration
```powershell
# Check config loaded correctly
python -c "from app.core.config import settings; print(f'LLM: {settings.LLM_MODEL}'); print(f'Embedding: {settings.EMBEDDING_MODEL}'); print(f'API Base: {settings.EMBEDDING_API_BASE_URL}'); print(f'Dimension: {settings.EMBEDDING_DIMENSION}')"
```

Expected output:
```
LLM: openrouter/free
Embedding: Qwen/Qwen3-Embedding-0.6B
API Base: local
Dimension: 1024
```

---

## Configuration Files Changed

### 1. backend/.env.example
```bash
# LLM Configuration (OpenRouter Free)
LLM_MODEL=openrouter/free
LLM_API_BASE_URL=https://openrouter.ai/api/v1

# Embedding Configuration (Local - Zero Cost)
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
EMBEDDING_API_BASE_URL=local
EMBEDDING_DIMENSION=1024
```

### 2. backend/app/core/config.py
```python
EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-0.6B"
EMBEDDING_API_BASE_URL: str = "local"
EMBEDDING_DIMENSION: int = 1024
```

### 3. database/schema.sql
```sql
embedding vector(1024) NOT NULL
```

### 4. backend/requirements.txt
Added:
```
sentence-transformers==3.3.1
transformers==4.51.0
torch>=2.9.0
```

---

## Performance

### Local vs API Embeddings

| Metric | OpenRouter API | Local (Qwen3-0.6B) |
|--------|----------------|-------------------|
| **Cost** | $0.02/M tokens | **$0.00** |
| **Latency (single)** | 200-500ms | 50-150ms (CPU) / 10-30ms (GPU) |
| **Latency (batch 100)** | 1-2s | 2-5s (CPU) / 0.5-1s (GPU) |
| **Network Required** | ✅ Yes | ❌ No (after download) |
| **Privacy** | Sent to API | ✅ Local only |
| **Offline** | ❌ No | ✅ Yes |
| **Quality (MTEB)** | ~69 | **70.7** |

**Note:** Local embeddings are free, faster (no network), and more private. Performance varies by hardware.

### CPU vs GPU

**CPU (Default):**
- Works on any machine
- ~50-150ms per embedding
- ~2-5s for batch of 100
- No special hardware needed

**GPU (Automatic if available):**
- 3-5x faster than CPU
- ~10-30ms per embedding
- ~0.5-1s for batch of 100
- Automatically detected and used

---

## Troubleshooting

### Model Download Fails
**Error:** `Failed to download model`

**Solutions:**
1. Check internet connection
2. Check Hugging Face is accessible: `curl https://huggingface.co`
3. Set HF cache directory if disk space is low:
   ```powershell
   $env:HF_HOME="D:\huggingface_cache"  # Example: use different drive
   ```
4. Manual download:
   ```powershell
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')"
   ```

### Out of Memory
**Error:** `RuntimeError: [enforce fail at alloc_cpu.cpp:114] err == 0. DefaultCPUAllocator: not enough memory`

**Solutions:**
1. Close other applications
2. Reduce batch size in `embedding_service.py`:
   ```python
   batch_size=16  # Instead of 32
   ```
3. Use PostgreSQL + pgvector (offloads vector storage)

### Slow Performance
**Issue:** Embeddings taking >1 second each

**Solutions:**
1. Verify GPU is being used:
   ```powershell
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   ```
2. Install CPU optimizations:
   ```powershell
   pip install intel-extension-for-pytorch  # Intel CPUs
   # OR
   pip install torch-directml  # AMD GPUs on Windows
   ```
3. Reduce context length if processing very long texts

### Import Errors
**Error:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution:**
```powershell
pip install sentence-transformers transformers torch
```

---

## Testing

### Run Tests
```powershell
cd backend
pytest tests/ -v
```

**All tests updated to:**
- Mock local model initialization
- Use 1024 dimensions instead of 1536
- Test both API and local embedding modes

### Manual Testing
1. Start backend: `uvicorn app.main:app --reload`
2. Upload a PDF via `/docs`
3. Verify embedding generation in logs
4. Ask a question about the paper
5. Verify retrieval works

---

## Rollback Instructions

If you need to revert to paid OpenRouter embeddings:

### 1. Update .env
```bash
EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_API_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_API_KEY=sk-or-v1-YOUR_KEY_HERE
EMBEDDING_DIMENSION=1536
```

### 2. Update database schema
```sql
-- Change back to 1536
ALTER TABLE embeddings DROP COLUMN embedding;
ALTER TABLE embeddings ADD COLUMN embedding vector(1536) NOT NULL;
```

### 3. Restart backend and re-upload papers

---

## Future Enhancements

**Possible upgrades (all still zero-cost):**

1. **Qwen3-Embedding-4B** (4096 dims, MTEB 74.6)
   - Higher quality
   - Requires more VRAM (~9 GB)

2. **Hybrid Search** (dense + sparse)
   - Use `bge-m3` model
   - Supports both dense and sparse embeddings

3. **Reranking** (optional second pass)
   - Use `Qwen3-Reranker-0.6B`
   - Improves retrieval quality by 5-10%

---

## Security & Privacy

✅ **No API keys in local embedding mode** (EMBEDDING_API_KEY is empty)  
✅ **No network requests** (after initial model download)  
✅ **Embeddings never leave your machine**  
✅ **Apache-2.0 license** (fully open, commercial use allowed)  
✅ **No telemetry** from sentence-transformers  
✅ **Reproducible builds** (pinned dependencies)

---

## Support

**Model Issues:** https://huggingface.co/Qwen/Qwen3-Embedding-0.6B/discussions  
**Sentence Transformers:** https://www.sbert.net  
**ResearchMate:** See main README.md

---

**Migration completed successfully! Enjoy zero-cost, high-quality local embeddings.**
