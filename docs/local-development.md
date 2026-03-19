# Local Development Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | ≥ 4.x | https://docker.com/products/docker-desktop |
| Python | 3.11+ | `brew install python@3.11` |
| Node.js | 18+ | `brew install node` |
| make | any | included on macOS |

---

## Quick Start (Docker — recommended)

```bash
# 1. Clone and start all services
git clone <repo>
cd MetricAnchor
make up

# 2. Generate sample data and seed the API
make generate-data   # creates sample_data/*.csv (deterministic, seed=42)
make seed            # uploads CSVs + creates semantic models

# 3. Open the UI
open http://localhost:3000
```

Services:
- **Web UI:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

To tail logs: `make logs` or `make logs-api`

---

## Local Development (no Docker)

### 1. API

```bash
cd apps/api
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create a .env file (copy and edit)
cp .env.example .env

# Start the API
uvicorn main:app --reload --port 8000
```

**Required `.env` variables:**

```bash
# LLM — set one of these to enable AI-quality answers
LLM_PROVIDER=openai           # openai | anthropic | openai_compatible
LLM_API_KEY=sk-...            # omit for stub mode (fully functional, no LLM)
LLM_MODEL=gpt-4o              # or claude-opus-4-6, etc.
LLM_BASE_URL=                 # only for openai_compatible (e.g. Ollama)
LLM_MAX_TOKENS=2048

# Storage
DATA_DIR=./data               # where uploads and DuckDB go
DATABASE_URL=sqlite+aiosqlite:///./data/metricanchor.db

# API
CORS_ORIGINS=http://localhost:3000
API_DEBUG=true

# Logging
LOG_LEVEL=INFO                # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=human              # human | json
```

**Stub mode** (no API key): The pipeline uses regex-based intent parsing and templated answers. SQL generation, execution, and all trust features work identically. Set `LLM_API_KEY=` or omit it entirely.

### 2. Web UI

```bash
cd apps/web
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

Open http://localhost:3000.

---

## Environment Variables — Full Reference

### API (`apps/api/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | `openai` · `anthropic` · `openai_compatible` |
| `LLM_API_KEY` | *(empty)* | API key. Empty or `test-key` = stub mode |
| `LLM_MODEL` | `gpt-4o` | Model identifier |
| `LLM_BASE_URL` | *(empty)* | Base URL for `openai_compatible` providers |
| `LLM_MAX_TOKENS` | `2048` | Max tokens per completion |
| `DATA_DIR` | `./data` | Directory for uploads and DuckDB |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/metricanchor.db` | SQLite connection string |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `API_DEBUG` | `true` | Enable SQLAlchemy echo and debug logging |
| `LOG_LEVEL` | `INFO` | Root log level |
| `LOG_FORMAT` | `human` | `human` (coloured) or `json` (structured, for prod) |
| `MAX_UPLOAD_BYTES` | `524288000` | 500 MB upload limit |

### Web UI (`apps/web/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | API base URL |

---

## Running Tests

```bash
# All unit + integration + eval tests (no API key, no running server needed)
make test

# Unit tests only (fastest, ~0.2s)
apps/api/.venv/bin/python3 -m pytest tests/unit/ -v

# Integration tests (requires sample_data/*.csv)
make generate-data
apps/api/.venv/bin/python3 -m pytest tests/integration/ -v

# Eval suite (question-level assertions against deterministic CSVs)
apps/api/.venv/bin/python3 -m pytest evals/test_evals.py -v

# API-level tests (requires running API)
make test-api

# Live question evaluations (requires make up && make seed)
pytest tests/test_demo_questions.py -v

# E2E Playwright tests (requires make up)
cd apps/web && npx playwright test
```

---

## CLI Usage

The CLI connects to the running API and provides a power-user interface.

```bash
# Check the alias works (or use python -m cli.main directly)
cd /path/to/MetricAnchor

# Check API status
apps/api/.venv/bin/python3 -m cli.main status

# Upload a dataset
apps/api/.venv/bin/python3 -m cli.main ingest sample_data/retail_sales.csv

# View column profile
apps/api/.venv/bin/python3 -m cli.main profile <dataset_id>

# Scaffold a semantic model
apps/api/.venv/bin/python3 -m cli.main model init <dataset_id> -o my_model.yml
# Edit my_model.yml, then upload:
apps/api/.venv/bin/python3 -m cli.main model create <dataset_id> my_model.yml

# Ask a question
apps/api/.venv/bin/python3 -m cli.main ask <dataset_id> "revenue by region"
apps/api/.venv/bin/python3 -m cli.main ask <dataset_id> "top 5 products" --provenance

# Run the offline eval suite
apps/api/.venv/bin/python3 -m cli.main eval run
```

Set `METRICANCHOR_API_URL` to point at a non-local server:
```bash
export METRICANCHOR_API_URL=https://my-staging-server.example.com
```

---

## Generating Sample Data

```bash
# Creates sample_data/retail_sales.csv, support_tickets.csv, saas_funnel.csv
# Deterministic — same output every time (seed=42)
make generate-data
# or:
python3 sample_data/generate.py
```

Seed the running API:
```bash
make seed           # upload CSVs + create semantic models
make seed-reset     # delete existing models first, then re-seed
```

---

## Linting

```bash
make lint           # ruff (Python) + ESLint (TypeScript)
make lint-fix       # auto-fix where possible
```

---

## Validating Semantic Models

```bash
# Validate all example models
make validate

# Validate a single file
python3 -m packages.semantic_model.validator examples/retail_sales/semantic_model.yml

# Via CLI (requires running API)
apps/api/.venv/bin/python3 -m cli.main model validate examples/retail_sales/semantic_model.yml
```

---

## Project Structure

```
MetricAnchor/
├── apps/
│   ├── api/              FastAPI backend
│   │   ├── config.py     Settings (env vars via pydantic-settings)
│   │   ├── main.py       App factory + lifespan + logging + middleware
│   │   ├── models.py     SQLAlchemy ORM (Dataset, SemanticModel, Question, Feedback)
│   │   ├── routers/      Route handlers (datasets, questions, semantic_models, health)
│   │   ├── schemas/      Pydantic request/response models
│   │   ├── services/     Business logic (IngestService, QuestionService, …)
│   │   └── tests/        API-level tests (httpx.ASGITransport)
│   └── web/              Next.js 14 frontend
│       └── src/app/      App Router pages
├── packages/
│   ├── llm_adapter/      Provider-agnostic async LLM client
│   ├── query_engine/     DuckDB wrapper + profiler + analytics pipeline
│   └── semantic_model/   Validator + resolver
├── cli/                  Typer CLI (metricanchor)
├── tests/
│   ├── unit/             Pure unit tests (no I/O, no DuckDB)
│   ├── integration/      Pipeline tests with real DuckDB + sample CSVs
│   └── e2e/              Playwright UI smoke tests
├── evals/                Offline question evaluation suite
├── examples/             Demo semantic models + example questions
├── sample_data/          Deterministic CSV generator + generated files
├── scripts/              seed_demo.py
├── docs/                 This directory
└── Makefile              All developer commands
```
