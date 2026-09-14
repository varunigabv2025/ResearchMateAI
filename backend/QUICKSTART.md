# Quick Start Guide

## Prerequisites

1. **Python 3.9+** installed
2. **PostgreSQL 14+** with pgvector extension (for production)
3. **Virtual environment** recommended

## Installation

### 1. Set up virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your values:
- `DATABASE_URL`: Your PostgreSQL connection string
- `LLM_API_KEY`: Your LLM API key
- `EMBEDDING_API_KEY`: Your embedding API key

**For testing without a database**, the app will use SQLite by default.

## Running the Application

### Method 1: Using the run script

```bash
python run.py
```

### Method 2: Using uvicorn directly

```bash
uvicorn app.main:app --reload
```

### Method 3: Using Python module

```bash
python -m app.main
```

The server will start at: **http://localhost:8000**

## Verify Installation

### Check the API is running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "ResearchMate AI",
  "version": "0.1.0"
}
```

### Access API documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=app --cov-report=html
```

## Testing the Upload Endpoint

If you have a PDF file, you can test the upload endpoint:

```bash
curl -X POST "http://localhost:8000/api/papers/upload" \
  -F "file=@path/to/your/paper.pdf"
```

Or use the interactive API docs at http://localhost:8000/docs

## Database Setup (PostgreSQL)

If you want to use PostgreSQL instead of SQLite:

1. Create database:
```sql
CREATE DATABASE researchmate;
```

2. Run schema:
```bash
psql -U postgres -d researchmate -f ../database/schema.sql
```

3. Update DATABASE_URL in .env:
```
DATABASE_URL=postgresql://username:password@localhost:5432/researchmate
```

## Troubleshooting

### Import Errors

Make sure you're in the `backend` directory and the virtual environment is activated.

### Database Connection Errors

- For testing: The app defaults to SQLite if DATABASE_URL is not set properly
- For production: Verify PostgreSQL is running and credentials are correct

### Port Already in Use

Change the port in `run.py` or use:
```bash
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. Upload a research paper PDF
2. Verify it's processed correctly
3. Check the detected sections
4. View the created chunks in the database

Ready to build the Q&A and comparison features!
