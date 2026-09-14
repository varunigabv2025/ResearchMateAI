# Database Setup

This directory contains the database schema for ResearchMate AI.

## Prerequisites

- PostgreSQL 14+ installed
- pgvector extension available

## Installation

### 1. Install PostgreSQL

Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

### 2. Install pgvector Extension

#### On Ubuntu/Debian:
```bash
sudo apt install postgresql-14-pgvector
```

#### On macOS with Homebrew:
```bash
brew install pgvector
```

#### On Windows:
Download from [pgvector releases](https://github.com/pgvector/pgvector/releases)

### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE researchmate;

# Connect to the new database
\c researchmate

# Run the schema file
\i schema.sql
```

Or run from command line:
```bash
psql -U postgres -d researchmate -f schema.sql
```

## Configuration

Update your `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/researchmate
```

## Schema Overview

### Tables

- **papers**: Stores uploaded PDF metadata
- **paper_chunks**: Stores extracted text chunks with page and section info
- **embeddings**: Stores vector embeddings for semantic search

### Key Features

- Automatic UUID generation for all IDs
- Cascade deletion (deleting a paper removes its chunks and embeddings)
- HNSW index for fast vector similarity search
- Indexes optimized for common query patterns
- Automatic timestamp management

## Verify Installation

```sql
-- Check if pgvector is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- List all tables
\dt

-- Check embeddings table structure
\d embeddings;
```
