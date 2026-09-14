# ResearchMate AI

> **ResearchMate AI helps researchers compare papers, understand existing approaches, and surface possible research gaps — with answers grounded in the original papers.**

ResearchMate AI is not just another "chat with PDF" tool. It's an AI-powered research workspace specifically designed for academic paper analysis, comparison, and research gap discovery.

## 🎯 Core Features (MVP)

This MVP focuses on three essential capabilities:

1. **✅ Per-Paper Grounded Q&A** - Upload research papers and ask questions with answers tied back to specific pages and sections *(Implemented)*
2. **✅ Multi-Paper Comparison** - Compare 2-5 papers side-by-side to understand methodologies, results, and limitations *(Implemented)*
3. **✅ Research Gap Discovery** - AI-suggested research gaps based on paper comparison analysis *(Implemented)*

**Important:** AI-generated answers, comparisons, and research gaps are suggestions and not scientifically validated. Always verify with domain expertise and the original literature.

## 🏗️ Architecture

### Tech Stack

- **Frontend**: Next.js, TypeScript, Tailwind CSS *(to be implemented)*
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL with pgvector extension
- **PDF Processing**: PyMuPDF
- **AI**: Modular LLM/embedding API integration

### Project Structure

```
ResearchMate/
├── frontend/              # Next.js application (coming soon)
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic (PDF, chunking, etc.)
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── core/        # Configuration and database
│   ├── tests/           # Pytest test suite
│   ├── requirements.txt
│   └── .env.example
├── database/
│   ├── schema.sql       # PostgreSQL + pgvector schema
│   └── README.md
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 14+ with pgvector extension
- Virtual environment tool (venv, conda, etc.)

### Database Setup

1. **Install PostgreSQL and pgvector**

   See [database/README.md](database/README.md) for detailed installation instructions.

2. **Create Database**

   ```bash
   psql -U postgres
   CREATE DATABASE researchmate;
   \c researchmate
   \i database/schema.sql
   ```

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in your values:

   ```bash
   cp .env.example .env
   ```

   Required configuration:
   - `DATABASE_URL`: PostgreSQL connection string
   - `LLM_API_KEY`: Your LLM API key (OpenAI, Anthropic, etc.)
   - `LLM_MODEL`: Model name (e.g., gpt-4, claude-3-opus)
   - `EMBEDDING_API_KEY`: Your embedding API key
   - `EMBEDDING_MODEL`: Embedding model name (e.g., text-embedding-ada-002)
   
   See `.env.example` for all available options.

5. **Run the backend**

   ```bash
   # Development mode with auto-reload
   uvicorn app.main:app --reload
   
   # Or using Python
   python -m app.main
   ```

   The API will be available at `http://localhost:8000`

6. **Access API documentation**

   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

Run the test suite:

```bash
cd backend
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

View coverage report:

```bash
# Open htmlcov/index.html in your browser
```

## 📡 API Endpoints

### Health Check

```http
GET /health
```

### Papers

```http
POST   /api/papers/upload         # Upload and process a PDF
GET    /api/papers/               # List all papers (with pagination)
GET    /api/papers/{id}           # Get paper details
DELETE /api/papers/{id}           # Delete a paper
POST   /api/papers/{id}/ask       # Ask a question about a paper
POST   /api/papers/compare        # Compare 2-5 papers
POST   /api/papers/gaps           # Analyze research gaps (NEW)
```

### Example: Upload a Paper

```bash
curl -X POST "http://localhost:8000/api/papers/upload" \
  -F "file=@research_paper.pdf"
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "research_paper.pdf",
  "page_count": 12,
  "sections_detected": [
    "Abstract",
    "Introduction",
    "Methodology",
    "Results",
    "Conclusion",
    "References"
  ],
  "message": "Paper uploaded and processed successfully. Ready for Q&A."
}
```

### Example: Ask a Question

```bash
curl -X POST "http://localhost:8000/api/papers/{paper_id}/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What methodology does the paper use?"}'
```

Response:
```json
{
  "answer": "The authors use a transformer-based architecture with self-attention mechanisms. The model was trained on 100,000 examples using AdamW optimizer.",
  "sources": [
    {
      "chunk_id": "abc123...",
      "page_number": 7,
      "section": "Methodology",
      "similarity": 0.89
    },
    {
      "chunk_id": "def456...",
      "page_number": 9,
      "section": "Experiments",
      "similarity": 0.82
    }
  ],
  "paper_id": "123e4567-e89b-12d3-a456-426614174000",
  "question": "What methodology does the paper use?",
  "has_sufficient_context": true
}
```

### Example: Compare Papers

```bash
curl -X POST "http://localhost:8000/api/papers/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_ids": [
      "123e4567-e89b-12d3-a456-426614174000",
      "223e4567-e89b-12d3-a456-426614174001",
      "323e4567-e89b-12d3-a456-426614174002"
    ]
  }'
```

Response:
```json
{
  "papers": [
    {
      "paper_id": "123e4567-e89b-12d3-a456-426614174000",
      "filename": "transformer_paper.pdf",
      "method": "Transformer architecture with multi-head self-attention",
      "dataset": "WMT 2014 English-to-German and English-to-French",
      "metric_result": "BLEU score of 28.4 on WMT 2014 EN-DE",
      "limitation": "Requires large amounts of training data and computational resources"
    },
    {
      "paper_id": "223e4567-e89b-12d3-a456-426614174001",
      "filename": "bert_paper.pdf",
      "method": "Bidirectional encoder representations from transformers",
      "dataset": "BooksCorpus and English Wikipedia",
      "metric_result": "11 tasks including GLUE benchmark improvements",
      "limitation": "Pre-training is computationally expensive"
    },
    {
      "paper_id": "323e4567-e89b-12d3-a456-426614174002",
      "filename": "gpt_paper.pdf",
      "method": "Generative pre-training with transformer decoder",
      "dataset": "BooksCorpus dataset",
      "metric_result": "State-of-the-art on 9 out of 12 tasks",
      "limitation": "Limited understanding of sentence relationships"
    }
  ],
  "total_papers": 3
}
```

### Example: Analyze Research Gaps

```bash
curl -X POST "http://localhost:8000/api/papers/gaps" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_ids": [
      "123e4567-e89b-12d3-a456-426614174000",
      "223e4567-e89b-12d3-a456-426614174001",
      "323e4567-e89b-12d3-a456-426614174002"
    ]
  }'
```

Response:
```json
{
  "paper_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "223e4567-e89b-12d3-a456-426614174001",
    "323e4567-e89b-12d3-a456-426614174002"
  ],
  "gaps": [
    {
      "title": "Limited dataset diversity across studies",
      "description": "The compared papers evaluate their approaches on relatively narrow or similar datasets (WMT 2014, BooksCorpus), which may limit understanding of generalizability across different domains and languages.",
      "basis": "All three papers use similar benchmark datasets (WMT 2014 or BooksCorpus) while their stated limitations mention computational cost rather than dataset diversity."
    },
    {
      "title": "Direct methodological comparison under unified conditions",
      "description": "The papers employ different transformer-based approaches (encoder-only, decoder-only, encoder-decoder) but do not directly compare these architectural choices under the same experimental setup.",
      "basis": "Papers use different methods (Transformer, BERT, GPT) and report results on different task sets, making direct performance comparison difficult."
    }
  ],
  "disclaimer": "AI-suggested — verify against the literature yourself."
}
```

**⚠️ Important:** These gap suggestions are generated from the provided papers only. They are not definitive claims about the entire research field and should be verified against the broader literature before use in research or academic writing.

## 🔬 How It Works

### Complete Q&A Pipeline

```
PDF Upload
    ↓
Validation (file type, size)
    ↓
Text Extraction (PyMuPDF)
    ↓
Section Detection (pattern matching)
    ↓
Text Chunking (with metadata)
    ↓
Embedding Generation (API)
    ↓
Vector Storage (pgvector)
    ↓
Ready for Q&A
```

### Grounded Q&A Flow

```
User Question
    ↓
Question Embedding
    ↓
Vector Similarity Search (paper-specific)
    ↓
Retrieve Top-K Relevant Chunks
    ↓
Build Grounded Prompt (with retrieved excerpts)
    ↓
LLM Generation (strict grounding instructions)
    ↓
Answer + Citations (page, section)
```

### Multi-Paper Comparison Flow

```
User Selects 2-5 Papers
    ↓
Validate Papers Exist
    ↓
For Each Paper:
  - Select Relevant Sections (prioritized)
  - Build Extraction Prompt
  - LLM Extraction Call (method, dataset, metrics, limitations)
  - Parse & Validate JSON
    ↓
Structured Comparison Table
```

**Key Design:**
- Exactly **one LLM call per paper** (not agents, not multi-step)
- Prioritized section selection (Abstract, Methods, Results, etc.)
- Strict JSON schema validation
- "Not specified in the paper" for missing information
- No fabrication or guessing

### Research Gap Analysis Flow

```
User Selects 2-5 Papers
    ↓
Feature 2 Structured Comparison
    ↓
Comparison Data (method, dataset, results, limitations)
    ↓
ONE LLM Analysis Call
    ↓
2-3 Possible Research Gaps
    ↓
Response with Disclaimer
```

**Key Design:**
- Reuses Feature 2 comparison data (no duplication)
- Exactly **ONE LLM call per analysis** (not per paper, not per gap)
- Analyzes ONLY provided comparison data (no outside knowledge)
- Returns 0-3 gaps (not forced to find gaps)
- Cautious language (suggests, appears, possible)
- Always includes disclaimer

### Section Detection

The system detects common research paper sections:

- Abstract
- Introduction
- Related Work / Literature Review
- Methodology / Methods / Materials and Methods
- Experiments / Experimental Setup
- Results / Findings
- Discussion
- Limitations
- Conclusion
- Future Work
- References

Detection uses simple heading pattern matching (not ML-based).

### Chunking Strategy

- **Chunk Size**: ~1000 characters (configurable)
- **Overlap**: 200 characters for context preservation
- **Metadata Preserved**: paper_id, page_number, section, chunk_index

Each chunk maintains:
```json
{
  "paper_id": "uuid",
  "page_number": 7,
  "section": "Methodology",
  "chunk_index": 23,
  "text": "...",
  "char_count": 987
}
```

### Grounding Strategy

**Critical Design Principle:** Answers must be grounded in the uploaded paper.

1. **Retrieval Filtering**: Vector search is restricted to the specific paper_id
2. **Similarity Threshold**: Only chunks above 0.7 similarity are used (configurable)
3. **Insufficient Context Handling**: If no relevant chunks are found, returns explicit "insufficient information" message
4. **Citation Tracking**: Every answer includes source chunks with page and section
5. **Prompt Engineering**: LLM receives strict instructions to answer only from provided excerpts
6. **No Fabrication**: LLM explicitly instructed not to invent page numbers or citations

### Embedding & Vector Search

- **Embedding Model**: Configurable via environment (default: text-embedding-ada-002)
- **Vector Dimension**: 1536 (configurable)
- **Similarity Metric**: Cosine distance
- **Index**: HNSW for fast approximate nearest neighbor search
- **Top-K**: 5 chunks retrieved by default
- **Provider**: Modular API integration (OpenAI-compatible)

## 🔒 Security Notes

- Never commit `.env` files or API keys
- Upload directory is excluded from git
- File size limits enforced (default: 50MB)
- PDF validation before processing
- SQL injection protection via SQLAlchemy ORM

## 🛣️ Roadmap

### ✅ Feature 1: Grounded Q&A (Complete)
- [x] PDF upload and validation
- [x] Text extraction with page numbers
- [x] Section detection
- [x] Chunking with metadata
- [x] Embedding generation and storage
- [x] Vector similarity search (pgvector)
- [x] Grounded Q&A endpoint
- [x] Citation with page/section
- [x] Insufficient context handling
- [x] Comprehensive test suite

### ✅ Feature 2: Multi-Paper Comparison (Complete)
- [x] Compare 2-5 papers
- [x] Structured extraction (method, dataset, metrics, limitations)
- [x] Section-aware content selection
- [x] One LLM call per paper
- [x] JSON schema validation
- [x] "Not specified" handling
- [x] Comparison endpoint
- [x] Comprehensive tests

### ✅ Feature 3: Research Gap Discovery (Complete)
- [x] AI-suggested research gaps
- [x] Gap analysis from comparison data
- [x] Single LLM call per analysis
- [x] Evidence-based suggestions
- [x] Cautious language (suggests/appears)
- [x] 0-3 gaps per analysis
- [x] Disclaimer always included
- [x] Comprehensive tests

### 🚧 Additional Features (Future)
- [ ] Frontend (Next.js)
- [ ] Authentication
- [ ] User workspaces
- [ ] External literature search
- [ ] Citation recommendations

## 🤝 Contributing

This is an MVP project. Contributions should maintain focus on the core use case: comparing research papers and discovering gaps.

**Not in scope for MVP:**
- General document chat
- Literature mapping/visualization
- Citation recommendation
- Writing assistance
- Advanced UI features

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [pgvector](https://github.com/pgvector/pgvector)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

**Status**: � MVP Complete | All 3 Core Features Implemented

**Features 1-3** are fully implemented and tested. The complete MVP workflow is ready:`n`n1. **Upload papers** ? PDF processing, chunking, embeddings`n2. **Ask questions** ? Grounded Q&A with citations`n3. **Compare papers** ? Structured extraction (method/dataset/results/limitations)`n4. **Analyze gaps** ? AI-suggested research opportunities from comparison data`n`nAll features include comprehensive test coverage and proper validation.

