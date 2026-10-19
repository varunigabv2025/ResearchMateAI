# ResearchMate AI

ResearchMate AI is an AI-assisted research workspace for working with academic PDFs. It supports paper-specific question answering, structured comparison of multiple papers, and suggestions for possible research gaps.

AI-generated content is a research aid, not a substitute for reading the source papers or verifying claims against the literature.

## Features

- **Grounded Q&A:** Ask questions about one paper. The backend retrieves paper-specific excerpts and returns an answer with evidence citations and page/section source details.
- **Markdown answers:** The UI renders headings, lists, emphasis, inline code, and code blocks. ResearchMateAI evidence markers such as `[S1]` are visually distinguished from numbered references already present in a paper.
- **Paper comparison:** Compare 2–5 papers on methodology, datasets, reported results, and limitations.
- **Research gap suggestions:** Generate possible gaps or contradictions from the selected papers' structured comparison data. Outputs include a reminder to verify suggestions against the wider literature.
- **PDF workspace:** Upload PDFs, view processing status, open a paper for Q&A, and select papers for comparison or gap analysis.

## Technology stack

| Area | Implementation |
|---|---|
| Frontend | Next.js 15, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL with the pgvector extension |
| PDF text extraction | PyMuPDF |
| Embeddings | Local `Qwen/Qwen3-Embedding-0.6B`, configured for 1024 dimensions |
| LLM provider | Google Gemini API with a Gemma model, or an OpenAI-compatible API such as OpenRouter |
| Retrieval | Dense semantic retrieval; the retrieval service also implements BM25 lexical retrieval and hybrid Reciprocal Rank Fusion (RRF) |

The embedding model runs locally and does not require an embedding API key. Its first run downloads model weights and needs sufficient RAM or Windows virtual memory. The LLM provider is called over the network and has its own availability, quota, and data-use terms.

## Project layout

```text
ResearchMateAI/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── core/         # Settings and database session
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Request and response schemas
│   │   └── services/     # PDF processing, embeddings, retrieval, LLM workflows
│   ├── tests/            # Backend tests
│   ├── requirements.txt
│   └── .env.example
├── database/
│   ├── schema.sql
│   └── README.md
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
└── README.md
```

## Requirements

- Python 3.10 or newer
- Node.js 18.18 or newer for the pinned Next.js 15.1.4 dependency
- PostgreSQL 14 or newer, with pgvector installed
- A Google AI Studio API key for the configured Gemma option, or an OpenRouter API key for OpenRouter
- Enough memory / virtual memory to load the local Qwen embedding model

For database installation details, see [database/README.md](database/README.md).

## Run locally

Run the backend and frontend in separate terminals.

### 1. Create the database

Create the PostgreSQL database and enable pgvector if it is not already enabled:

```sql
CREATE DATABASE researchmate;
```

Then connect to `researchmate` and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Apply the schema from the repository root:

```bash
psql -U postgres -d researchmate -f database/schema.sql
```

Adjust the username and connection values for your local PostgreSQL setup.

### 2. Configure and start the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS/Linux, activate the environment with:

```bash
source .venv/bin/activate
```

Edit `.env` and set `DATABASE_URL` and the credentials for **one** LLM provider.

#### Option A: Google Gemini API with Gemma

```env
LLM_API_KEY=your_google_api_key
LLM_MODEL=gemma-4-26b-a4b-it
LLM_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta
LLM_PROVIDER=gemini
```

Create a key in [Google AI Studio](https://aistudio.google.com/).

#### Option B: OpenRouter

Use this configuration instead of the Gemma values above:

```env
LLM_API_KEY=your_openrouter_api_key
LLM_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
LLM_API_BASE_URL=https://openrouter.ai/api/v1
LLM_PROVIDER=openai
```

Get a key from [OpenRouter](https://openrouter.ai/keys). The example model is only a configuration example; model availability can change.

#### Embedding configuration

The default local embedding settings are:

```env
EMBEDDING_API_KEY=
EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
EMBEDDING_API_BASE_URL=local
EMBEDDING_DIMENSION=1024
```

No embedding API key is needed for this local configuration. Do not change the embedding model or dimension for an existing database unless you have a migration/re-embedding plan.

Start the API while still in the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Check the health endpoint at [http://localhost:8000/health](http://localhost:8000/health) and open the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Configure and start the frontend

In a second terminal:

```powershell
cd frontend
npm ci
```

Optionally create `frontend/.env.local` if your backend is not at the default address:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the development server:

```powershell
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## How the main workflows work

### Grounded Q&A

1. The uploaded PDF is validated and its text is extracted with page metadata.
2. Extracted text is split into chunks, each associated with the paper, page, section, and chunk order.
3. The local Qwen model generates embeddings for the chunks.
4. A question is embedded and retrieved against the selected paper's content.
5. The grounded prompt asks the LLM to answer only from the supplied excerpts.
6. The response includes evidence markers (for example, `[S1]`) and a source list with page/section details.

The Q&A endpoint currently uses dense retrieval by default. The retrieval service also supports BM25 lexical search and hybrid RRF modes for evaluation or explicit use. The configured default top-k is 5 and the calibrated dense similarity threshold is 0.25; these are retrieval settings, not guarantees of answer quality.

### Compare papers

Select 2–5 processed papers. The backend selects relevant paper sections and asks the configured LLM to extract each paper's method, dataset, reported results, and limitations into a structured format. The frontend displays the results in a comparison view.

### Research gap analysis

Select 2–5 processed papers. The current workflow first extracts comparison fields for each paper, then makes an additional LLM call to suggest possible gaps from those fields. As a result, a request for two papers normally requires three LLM calls (one extraction per paper plus one gap-analysis call); five papers normally require six. Failed calls and provider retries may add more requests.

Gap suggestions are hypotheses based on the selected papers and may miss relevant literature. Verify them against the original papers and broader research.

## API endpoints

The FastAPI application exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/papers/upload` | Upload and process a PDF |
| `GET` | `/api/papers/` | List papers |
| `GET` | `/api/papers/{id}` | Get paper details |
| `DELETE` | `/api/papers/{id}` | Delete a paper |
| `POST` | `/api/papers/{id}/ask` | Ask a question about a paper |
| `POST` | `/api/papers/compare` | Compare 2–5 papers |
| `POST` | `/api/papers/gaps` | Analyze possible research gaps |

Example Q&A request:

```bash
curl -X POST "http://localhost:8000/api/papers/<PAPER_ID>/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What methodology does this paper use?"}'
```

For the exact schemas and response models, use the interactive API documentation at `/docs`.

## Testing and build checks

Run backend tests from the `backend` directory:

```bash
python -m pytest
```

Run the focused Gemini retry tests:

```bash
python -m pytest tests/test_gemini_retry.py -q
```

Run the frontend production build from `frontend`:

```bash
npm run build
```

These commands are provided for local verification; run them on the current branch before merging changes. This repository does not currently define a GitHub Actions workflow that automatically runs these checks.

## Operational notes and known limitations

- **Gemma free tier is not unlimited.** Google applies project/model-specific RPM, input-token-per-minute, and requests-per-day limits. A large comparison or gap-analysis request can exceed the input-token quota. Check the active values in [Google AI Studio rate limits](https://aistudio.google.com/rate-limit) and the [Gemini API rate-limit documentation](https://ai.google.dev/gemini-api/docs/rate-limits).
- **HTTP 429:** quota/rate-limit errors are surfaced to the caller; the backend does not automatically retry 429 responses. Wait for the specified retry delay, reduce repeated requests or input size, or review the project's active limits.
- **Transient server errors:** the Gemini client retries HTTP 500, 502, 503, and 504 responses a limited number of times. These retries cannot resolve persistent provider outages.
- **Upload-size configuration needs alignment:** the frontend currently defines a 20 MiB file-size constant, while the backend example defaults `MAX_UPLOAD_SIZE_MB` to 50. Confirm and align the limits before relying on a single maximum across the application.
- **Local embedding resource use:** the Qwen weights are downloaded on first use. On Windows, insufficient RAM or paging-file space can prevent the backend from starting.
- **Grounding and citations:** evidence citations are generated by the model and displayed alongside retrieved source metadata. Review cited excerpts in the original paper; formatting and source metadata do not guarantee every claim is correct.
- **Data privacy:** review the selected LLM provider's current terms before sending sensitive or unpublished research content. The Google Gemini API free-tier data-use terms can differ from paid-tier terms.
- **Authentication:** the current MVP does not implement user authentication or per-user workspaces. Do not expose a local development instance to an untrusted network without adding appropriate access controls.
- **CORS:** the current backend configuration allows all origins for development. Restrict CORS origins before production deployment.
- **License:** no `LICENSE` file is currently included. Usage and redistribution rights are therefore not explicitly granted by this repository.

## Security

- Keep real API keys and secrets in local environment files; never commit them.
- Do not include database files, uploaded PDFs, local environment files, or generated secrets in commits.
- Review logs before sharing them; request errors should not include API keys.
- Restrict database and API access appropriately before deployment.

## Contributing

Keep changes focused on grounded paper analysis, structured comparison, and carefully qualified research-gap suggestions. Include regression tests for behavior changes and verify both backend tests and the frontend production build before merging.
