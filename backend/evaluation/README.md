# RAG Evaluation & Benchmarking

This directory contains the evaluation framework for measuring the performance of the existing RAG (Retrieval-Augmented Generation) pipeline in ResearchMateAI.

## Important Notes

**This is baseline evaluation only.** The framework measures the EXISTING production RAG pipeline without modification. It does NOT:
- Change embedding models
- Modify retrieval strategies
- Alter chunking configuration
- Replace the LLM
- Modify database or pgvector settings

## Current RAG Configuration

### Embedding
- **Model**: Qwen3-Embedding-0.6B (local)
- **Dimension**: 1024
- **Mode**: Document and query embeddings

### Chunking
- **Chunk size**: 1000 characters
- **Overlap**: 200 characters
- **Metadata**: Page number, section, chunk index

### Retrieval
- **Method**: Cosine similarity vector search
- **Top-K**: 5 chunks (configurable for evaluation)
- **Similarity threshold**: 0.4
- **Database (Production)**: PostgreSQL with pgvector extension
- **Database (Baseline)**: SQLite (test.db) with Python/NumPy fallback
  - **Note**: The baseline evaluation in this directory used SQLite because pgvector was not available in the evaluation environment
  - The Python fallback computes cosine similarity using NumPy rather than native pgvector operators
  - Functionally equivalent but different performance characteristics

### LLM
- **Model**: nvidia/nemotron-3-ultra-550b-a55b:free
- **Provider**: OpenRouter
- **Mode**: Chat completion with grounded prompts

## Evaluation Dataset

**File**: `dataset.json`

**Paper**: PA-EIS (Priority-Aware Edge Inference Scheduling) IEEE paper
- First 5 pages only
- Real paper uploaded to system during Phase 2B

**Questions**: 10 covering:
1. **Motivation** - Core research problem
2. **Methodology** - Technical approach
3. **Dataset** - Evaluation workloads
4. **Results** - Reported metrics (intentionally missing)
5. **Limitations** - Stated constraints
6. **Technical detail** - Linux kernel features
7. **Conceptual** - Design rationale
8. **Multi-part** - Connected information
9. **Comparison/inference** - Synthesis required
10. **Out-of-scope** - Unanswerable question

### Ground Truth Labels

Each question includes:
- `expected_answer_contains`: Keywords for deterministic matching (**NOT semantic correctness**)
- `relevant_pages`: Ground truth page numbers
- `answerable`: Boolean flag
- `category`: Question type

**IMPORTANT**: The `expected_answer_contains` field is a **lightweight deterministic signal only**. It indicates whether expected terminology appears in the answer but does NOT measure semantic correctness, completeness, or quality.

## Evaluation Metrics

### Retrieval Metrics

**Hit Rate@K**
```
HR@K = 1 if at least one relevant page appears in top-K, else 0
```
Averaged across all queries.

**Recall@K**
```
Recall@K = |relevant ∩ top_k| / |relevant|
```
Fraction of relevant items retrieved in top-K.

**Precision@K**
```
Precision@K = |relevant ∩ top_k| / K
```
Fraction of top-K that are relevant.

**Mean Reciprocal Rank (MRR)**
```
MRR = 1 / rank_of_first_relevant_item
```
Averaged across queries. 0 if no relevant item retrieved.

All metrics are computed at K=1, 3, 5, 10.

### Answer Quality Metrics

**1. Deterministic Keyword Matching**
- Checks presence of expected keywords
- **NOT a measure of semantic correctness**
- Lightweight signal only
- Reports: match_rate, matched_keywords, missed_keywords

**2. Faithfulness / Groundedness**
- Simple heuristic checking phrase overlap between answer and retrieved context
- NOT comprehensive semantic validation
- Reports: has_overlap (boolean), overlap_ratio (0-1)

**3. Citation Accuracy**
- Compares cited pages to ground truth relevant pages
- Uses EXISTING citation metadata (page_number, chunk_id, similarity)
- Reports: precision, recall

**4. Unanswerable Question Handling**
- Checks whether system indicates insufficient information
- Detects refusal signals ("insufficient", "not found", "cannot answer", etc.)
- Reports: indicated_insufficient, has_refusal_signal

**5. LLM-as-a-judge (Optional)**
- NOT IMPLEMENTED in baseline
- If added: Must be labeled as "LLM-based evaluation", NOT ground truth
- Must record: judge model, rubric, score, reasoning
- Should be optional due to free-tier LLM rate limits

### Citation Metrics

**Citation Page Accuracy**
```
Precision = |cited_relevant| / |cited|
Recall = |cited_relevant| / |relevant|
```
Measures whether the pages cited by the Q&A system match ground truth relevant pages.

### Latency Metrics

Measured separately for:
- **Query embedding**: Time to generate question embedding
- **Retrieval**: Time to perform vector search
- **LLM generation**: Time for answer generation
- **End-to-end**: Total request latency

For each component, reports:
- Mean, median, min, max, standard deviation
- Count of successful measurements

**Note**: LLM latency may be highly variable due to free-tier OpenRouter model.

## Running Evaluation

### Prerequisites

1. Backend is running with database initialized
2. PA-EIS paper is uploaded and fully processed
3. Environment variables configured (.env)

### Get Paper ID

```bash
# List papers to find PA-EIS paper ID
curl http://localhost:8000/api/papers

# Look for PA-EIS_IEEE_first5pages.pdf in the response
# Copy the "id" field (UUID)
```

### Run Evaluation

```bash
cd backend

# Run evaluation with paper UUID
python evaluation/run_evaluation.py --paper-id <PAPER_UUID>

# Optional: Specify custom paths
python evaluation/run_evaluation.py \
  --paper-id <PAPER_UUID> \
  --dataset evaluation/dataset.json \
  --output evaluation/results/baseline.json
```

### Output

Results are saved to `evaluation/results/baseline.json` with:
- Timestamp and configuration
- Aggregated metrics
- Per-question detailed results
- Error records (if any)
- Latency statistics

## Baseline Results Format

```json
{
  "timestamp": "2026-10-04T...",
  "evaluation_duration_seconds": 45.2,
  "paper": {
    "id": "...",
    "filename": "PA-EIS_IEEE_first5pages.pdf",
    "title": "..."
  },
  "rag_config": {
    "embedding_model": "Qwen3-Embedding-0.6B",
    "retrieval": {
      "method": "python_numpy_cosine_fallback",  // Actual method used
      "top_k": 5,
      "similarity_threshold": 0.4
    },
    "llm_model": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "database": "SQLite (test.db)"  // Actual database used
  },
  "retrieval_metrics": {
    "hit_rate_at_1": 0.75,
    "recall_at_5": 0.65,
    "mrr": 0.82
  },
  "answer_metrics": {
    "avg_keyword_match_rate": 0.70,
    "avg_faithfulness_ratio": 0.75
  },
  "citation_metrics": {
    "avg_citation_precision": 0.80,
    "avg_citation_recall": 0.60
  },
  "latency_metrics": {
    "retrieval": { "mean": 0.15, "std_dev": 0.02 },
    "llm": { "mean": 5.2, "std_dev": 2.1 },
    "end_to_end": { "mean": 5.35, "std_dev": 2.1 }
  },
  "per_question_results": [ ... ],
  "errors": [ ... ],
  "notes": [
    "This baseline used SQLite with Python/NumPy cosine fallback",
    "Results should NOT be interpreted as PostgreSQL+pgvector benchmark"
  ]
}
```

## Implementation Details

### Integration with Existing Pipeline

The evaluator **reuses existing services**:

```python
# Calls EXISTING retrieval service
await retrieval_service.retrieve_relevant_chunks(
    db=db,
    paper_id=paper_id,
    question=question,
    top_k=10,
    similarity_threshold=0.4
)

# Calls EXISTING LLM service with EXISTING prompt builder
messages = GroundedQAPrompt.build_messages(question, chunks)
answer = await llm_service.generate_chat_completion(messages)
```

**No duplication of RAG logic.** The evaluation measures the production pipeline as-is.

### Files

- `dataset.json` - Evaluation questions and ground truth
- `metrics.py` - Metric computation (Hit Rate, Recall, Precision, MRR, etc.)
- `run_evaluation.py` - Main evaluation runner
- `results/baseline.json` - Generated baseline results
- `README.md` - This file

### Tests

Unit tests in `backend/tests/test_evaluation.py` cover:
- Hit Rate, Recall, Precision, MRR edge cases
- K > retrieved count
- Empty results
- Zero relevant documents
- Multiple relevant chunks per page
- Keyword matching
- Faithfulness heuristics
- Citation accuracy
- Unanswerable question detection
- Latency statistics
- Aggregation functions

## Limitations

### Dataset Limitations
- **Small scale**: Only 10 questions
- **Single paper**: PA-EIS paper only (first 5 pages)
- **Manual labels**: Ground truth created by inspection, not multi-annotator
- **Limited diversity**: Questions focus on one engineering paper domain

### Metric Limitations
- **Keyword matching**: NOT semantic answer correctness
- **Faithfulness**: Simple heuristic, not comprehensive groundedness verification
- **Citation accuracy**: Evaluates page-level only, not claim-level
- **No human evaluation**: No human judges for answer quality

### System Limitations
- **Free-tier LLM**: Latency may be highly variable
- **SQLite database**: Baseline used SQLite (test.db), NOT production PostgreSQL
- **No pgvector**: Baseline used Python/NumPy cosine fallback, not native pgvector operators
- **Fallback performance**: Python fallback loads all embeddings into memory, different characteristics from native pgvector
- **No retry logic**: Timeouts recorded as-is
- **Single run**: Baseline is one-shot, not averaged over multiple runs
- **NOT a PostgreSQL+pgvector benchmark**: Results reflect SQLite fallback behavior only

### Evaluation Scope
- Measures **existing pipeline only**
- Does NOT evaluate alternative configurations
- Does NOT compare different embedding models
- Does NOT test hybrid retrieval approaches

## Reproducibility

To reproduce baseline evaluation:

1. **Environment**: Windows, Python 3.14
2. **Backend**: Use exact dependencies from requirements.txt
3. **Database**: SQLite (test.db) - pgvector optional for production but not required for evaluation
4. **Paper**: PA-EIS_IEEE_first5pages.pdf (uploaded during Phase 2B)
5. **RAG config**: Default settings (chunk_size=1000, overlap=200, top_k=5, threshold=0.4)
6. **Dataset**: evaluation/dataset.json (unchanged)
7. **Run**: Single-pass evaluation with 1-second delay between questions

**Note**: LLM responses may vary due to non-deterministic generation, even with identical configuration.

**Database Configuration**:
- The current baseline used SQLite with Python/NumPy fallback because pgvector was not installed
- To run with PostgreSQL+pgvector: install pgvector extension and update DATABASE_URL in .env
- The evaluator will automatically detect and report which method was used

## Future Work (NOT in Phase 4)

Potential improvements for later phases:
- Larger, multi-paper dataset
- Multi-annotator ground truth
- Semantic answer evaluation (e.g., RAGAS, BERTScore)
- Claim-level citation verification
- Alternative retrieval configurations
- Ablation studies
- Human evaluation

**Phase 4 is baseline measurement only.** No changes to RAG pipeline.

## References

- Dataset: PA-EIS (Priority-Aware Edge Inference Scheduling) IEEE paper
- RAG architecture: Phase 2B implementation
- Evaluation metrics: Standard IR and RAG evaluation practices

---

**Last Updated**: Phase 4 - RAG Evaluation & Benchmarking
**Status**: Baseline evaluation framework complete
