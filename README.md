# 🔬 Enterprise Research Assistant RAG

> **Production-ready AI Research Workflow Application** — automatically generates structured PDF reports from massive document corpora using Gemini, ChromaDB, FlashRank, and ReAct reasoning.

**Project Status:** Active and fully implemented.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [API Documentation](#api-documentation)
- [Features](#features)
- [Configuration](#configuration)
- [Testing](#testing)
- [Security](#security)
- [Database Schema](#database-schema)

---

## Overview

This is **not a chatbot**. It is a full enterprise research workflow application that:

1. **Ingests** documents (PDF, DOCX, TXT) up to 5,000+ pages
2. **Chunks** text with configurable size and overlap
3. **Embeds** using Google Gemini / SentenceTransformers
4. **Indexes** into ChromaDB with metadata (document_id, page_number, timestamps)
5. **Retrieves** via hybrid search (vector + BM25) → Top-20
6. **Reranks** using FlashRank cross-encoder → Top-5
7. **Reasons** using ReAct framework (Thought → Action → Observation)
8. **Generates** structured research reports with citations
9. **Exports** professional PDF with executive summary, findings, analysis, references
10. **Validates** output against source chunks with confidence scoring

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│  Input Guards   │ ← Prompt injection, jailbreak, role override detection
└────────┬────────┘
         │
    ▼
┌─────────────────────────────────┐
│       Hybrid Retrieval          │
│  Vector Search (ChromaDB)       │ ← Gemini / SentenceTransformer embeddings
│  + BM25 Sparse Search           │ ← Reciprocal Rank Fusion
│  → Top-20 Results               │
└────────┬────────────────────────┘
         │
    ▼
┌─────────────────┐
│  FlashRank      │ ← Cross-encoder reranking
│  → Top-5        │
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ Context Compress│ ← Dedup, token limit, relevance sort
└────────┬────────┘
         │
    ▼
┌──────────────────────────────────────┐
│  ReAct Agent                         │
│  Thought → Action → Observation      │ ← LLM: Gemini 2.5 Flash (primary)
│  → Final Answer                      │ ← Fallback: OpenAI GPT-4o
└────────┬─────────────────────────────┘ ← Last resort: Raw chunks
         │
    ▼
┌─────────────────┐
│ Output Validator│ ← Citation check, confidence score, hallucination detection
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│  PDF Generator  │ ← ReportLab: Title, Summary, Findings, Analysis, References
└────────┬────────┘
         │
    ▼
  📥 Download PDF
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Primary LLM | Google Gemini 2.5 Flash |
| Fallback LLM | OpenAI GPT-4o |
| Vector DB | ChromaDB (persistent) |
| Secondary Index | FAISS |
| Embeddings | Gemini text-embedding-004 / SentenceTransformers |
| Document Parsing | PyPDF + Unstructured |
| Reranking | FlashRank (ms-marco cross-encoder) |
| Report Generation | ReportLab |
| Database | SQLite / PostgreSQL (SQLAlchemy) |
| Logging | Loguru |
| Monitoring | LangSmith support |
| Testing | pytest |
| Deployment | Docker + docker-compose |

---

## Quick Start

### Option 1: Automated Startup (Windows)

Double-click **`START_PROJECT.bat`** in the project root directory.

This will automatically:
1. ✅ Activate the virtual environment
2. ✅ Start the FastAPI backend on `http://localhost:8000`

**Access points:**
- API Docs: http://localhost:8000/docs
- Frontend: Open `app/frontend/index.html` in a browser

### Option 2: Manual Startup (CLI)

#### Prerequisites
```bash
git clone https://github.com/your-org/enterprise-rag
cd enterprise-rag

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

#### Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys:
# GOOGLE_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here (optional fallback)
```

#### Run Backend (FastAPI)
```bash
cd "c:\Users\Yashaswi A R\OneDrive\Desktop\prompt\Enterprise-RAG"
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

#### Frontend
Open `app/frontend/index.html` directly in a browser.

---

## Corpus Setup

Use the new bulk loader to download and index a large public-domain corpus into ChromaDB.

```bash
python data/bulk_corpus_loader.py --test-run
```

This downloads and ingests a small sample of files first so you can verify end-to-end operation.

Then run the full download and ingestion:

```bash
python data/bulk_corpus_loader.py
```

Verify the estimated page count:

```bash
python data/bulk_corpus_loader.py --estimate-pages
```

Expected output includes a summary like:

"Total corpus: ~X,XXX pages across Y documents"

You can also download only or ingest only:

```bash
python data/bulk_corpus_loader.py --download-only
python data/bulk_corpus_loader.py --ingest-only
```

Or run the automation wrapper scripts:

```bash
bash data/run_corpus_setup.sh
```

On Windows:

```cmd
data\run_corpus_setup.bat
```

---

## Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f backend
# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

Services:
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## API Documentation

Full interactive docs at `/docs` (Swagger) and `/redoc`.

### Document CRUD

```http
POST   /api/v1/documents/upload          Upload & index document
GET    /api/v1/documents/                List all documents
GET    /api/v1/documents/{id}            Get document metadata
DELETE /api/v1/documents/{id}            Delete document + all chunks
DELETE /api/v1/documents/{id}/pages      Delete specific pages only
PUT    /api/v1/documents/{id}/pages      Re-index specific pages only
GET    /api/v1/documents/{id}/chunks     Get document chunks
```

### Report Generation

```http
POST   /api/v1/reports/generate          Generate PDF research report
GET    /api/v1/reports/                  List all reports
GET    /api/v1/reports/{id}              Get report metadata
GET    /api/v1/reports/{id}/download     Download PDF
DELETE /api/v1/reports/{id}             Delete report
POST   /api/v1/reports/feedback          Submit feedback
```

### Search

```http
POST   /api/v1/search/                   Hybrid search knowledge base
```

### System

```http
GET    /api/v1/system/stats              System statistics
GET    /api/v1/system/health             Health check
GET    /api/v1/system/audit-logs         Audit log entries
GET    /api/v1/system/security-events    Security events
GET    /api/v1/system/analytics          Usage analytics
POST   /api/v1/system/cache/clear        Clear all caches
```

### Example: Generate Report

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/reports/generate",
    json={
        "query": "What are the key findings regarding ML model deployment?",
        "use_react": True,
    }
)
result = response.json()
print(f"Report ID: {result['report_id']}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"PDF: GET /api/v1/reports/{result['report_id']}/download")
```

---

## Features

### Document CRUD
- ✅ Add documents (PDF, DOCX, TXT, MD)
- ✅ Delete entire documents
- ✅ Delete specific pages only
- ✅ Re-index specific pages only
- ✅ **Never rebuilds entire database** — incremental only
- ✅ Metadata: document_id, document_name, page_number, created_at, updated_at

### Massive Scale
- ✅ 5,000+ PDF pages
- ✅ 100,000+ chunks in ChromaDB
- ✅ Batch embedding (configurable batch size)
- ✅ Async ingestion
- ✅ Background workers (ThreadPoolExecutor)

### Advanced Retrieval
- ✅ Hybrid search: Dense (ChromaDB) + Sparse (BM25)
- ✅ Reciprocal Rank Fusion for hybrid merging
- ✅ FlashRank cross-encoder reranking (Top-20 → Top-5)
- ✅ Context compression (dedup, token limits, relevance sort)

### ReAct Reasoning
```
Thought: Need information about machine learning deployment.
Action: Search vector database for deployment-related chunks.
Observation: Found 5 chunks about deployment strategies.
Thought: Need supporting evidence for performance metrics.
Action: Retrieve additional performance data.
Observation: Found performance benchmarks in 3 documents.
Final Answer: [Structured report with citations]
```

### Security
- ✅ 15+ prompt injection patterns detected
- ✅ Jailbreak detection (DAN, STAN, etc.)
- ✅ Role override prevention
- ✅ System prompt extraction prevention
- ✅ Security events logged to database
- ✅ Output claim validation against source context
- ✅ Confidence scoring for every response

### PDF Reports
Sections: Title, Executive Summary, Key Findings, Detailed Analysis, Evidence, Recommendations, References

### API Failover
```
Gemini 2.5 Flash (primary)
    ↓ if fails
OpenAI GPT-4o (fallback)
    ↓ if fails
Raw retrieved chunks (never crashes)
```

---

## Configuration

All configuration via `.env` file. Key settings:

```bash
# LLM
GOOGLE_API_KEY=...           # Gemini (primary)
OPENAI_API_KEY=...           # OpenAI (fallback)
GEMINI_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.1

# Retrieval
VECTOR_SEARCH_TOP_K=20       # Initial retrieval count
RERANK_TOP_N=5               # After reranking

# Chunking
CHUNK_SIZE=1000              # Characters per chunk
CHUNK_OVERLAP=200            # Overlap between chunks

# Performance
EMBEDDING_BATCH_SIZE=100     # Embeddings per API call
MAX_CONTEXT_TOKENS=100000    # Max tokens sent to LLM
CACHE_TTL=3600               # Cache TTL in seconds
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test module
pytest tests/test_guardrails.py -v
pytest tests/test_reranker.py -v
pytest tests/test_crud.py -v
pytest tests/test_fallback.py -v
pytest tests/test_document_processing.py -v
```

Test coverage:
- `test_guardrails.py` — Input/output security validation
- `test_reranker.py` — FlashRank reranking behavior
- `test_crud.py` — Database CRUD and cache operations
- `test_fallback.py` — LLM failover chain, context compression, ReAct parsing
- `test_document_processing.py` — Document chunking, metadata, edge cases

---

## Security

### Threat Model
The system defends against:
1. **Prompt Injection** — "Ignore all previous instructions"
2. **System Prompt Extraction** — "Reveal your system prompt"
3. **Jailbreaking** — DAN mode, role override
4. **Data Exfiltration** — "Dump the entire database"
5. **Hallucination** — Output validated against source chunks

### Response to Attacks
```
→ Input detected as injection/jailbreak
→ Request blocked immediately
→ "Security violation detected." returned to user
→ Event logged to security_events table
→ IP address recorded
```

---

## Database Schema

```sql
-- Documents
CREATE TABLE documents (
    id          TEXT PRIMARY KEY,
    document_id TEXT UNIQUE NOT NULL,
    document_name TEXT NOT NULL,
    file_path   TEXT,
    file_size   INTEGER,
    total_pages INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    status      TEXT DEFAULT 'pending',
    error_message TEXT,
    metadata    JSON DEFAULT '{}',
    created_at  DATETIME,
    updated_at  DATETIME
);

-- Chunks
CREATE TABLE chunks (
    id          TEXT PRIMARY KEY,
    chunk_id    TEXT UNIQUE NOT NULL,
    document_id TEXT REFERENCES documents(document_id),
    document_name TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    content_hash TEXT,
    token_count INTEGER DEFAULT 0,
    embedding_model TEXT,
    is_indexed  BOOLEAN DEFAULT FALSE,
    created_at  DATETIME,
    updated_at  DATETIME
);

-- Reports
CREATE TABLE reports (
    id            TEXT PRIMARY KEY,
    report_id     TEXT UNIQUE NOT NULL,
    query         TEXT NOT NULL,
    title         TEXT,
    status        TEXT DEFAULT 'generating',
    pdf_path      TEXT,
    sections      JSON DEFAULT '{}',
    citations     JSON DEFAULT '[]',
    confidence_score FLOAT DEFAULT 0.0,
    llm_provider  TEXT,
    processing_time FLOAT,
    error_message TEXT,
    created_at    DATETIME,
    updated_at    DATETIME
);

-- Audit Logs
CREATE TABLE audit_logs (
    id          TEXT PRIMARY KEY,
    action      TEXT NOT NULL,
    entity_type TEXT,
    entity_id   TEXT,
    user_id     TEXT,
    ip_address  TEXT,
    details     JSON DEFAULT '{}',
    created_at  DATETIME
);

-- Security Events
CREATE TABLE security_events (
    id          TEXT PRIMARY KEY,
    event_type  TEXT NOT NULL,
    severity    TEXT DEFAULT 'WARNING',
    source_ip   TEXT,
    details     JSON DEFAULT '{}',
    raw_input   TEXT,
    resolved    BOOLEAN DEFAULT FALSE,
    created_at  DATETIME
);

-- Feedback
CREATE TABLE feedback (
    id          TEXT PRIMARY KEY,
    report_id   TEXT REFERENCES reports(report_id),
    query       TEXT,
    rating      INTEGER,
    comment     TEXT,
    helpful     BOOLEAN,
    created_at  DATETIME
);
```

---

## Streamlit UI Pages

| Page | Description |
|------|-------------|
| 🏠 Dashboard | Metrics, workflow diagram, quick actions |
| 📤 Upload Documents | Drag & drop multi-file upload |
| 📁 Manage Documents | Full CRUD with page-level operations |
| 📊 Generate Report | Query input, pipeline visualization, PDF download |
| 📋 Report History | All reports with download + delete |
| 🔍 Search | Direct knowledge base search |
| 📈 System Monitor | Stats, analytics, security events |
| ⚙️ Settings | Configuration, architecture overview |

---

## Performance Benchmarks (Approximate)

| Operation | Performance |
|-----------|-------------|
| PDF ingestion (100 pages) | ~30-60 seconds |
| Embedding batch (100 chunks) | ~5-10 seconds |
| Hybrid retrieval | < 500ms |
| FlashRank reranking | < 200ms |
| LLM report generation | 15-60 seconds |
| Full pipeline (simple query) | ~30-90 seconds |
| Cache hit retrieval | < 10ms |

---

## License

MIT License — Enterprise use permitted.

---

*Built with FastAPI, Streamlit, Google Gemini, ChromaDB, FlashRank, and ReportLab.*
