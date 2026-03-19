# MetricAnchor

**Ask questions about your data in plain English. Get SQL, charts, and confidence scores back. Everything is inspectable.**

[![CI](https://github.com/your-username/metricanchor/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/metricanchor/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

MetricAnchor is an open-source AI analytics copilot. Upload a CSV, define what "revenue" or "churn rate" means in YAML, and ask questions in natural language. Every answer shows its SQL, how business terms were resolved, what assumptions were made, and a confidence score.

**No black boxes.** The SQL that ran, the semantic mappings applied, the time ranges interpreted — all of it is surfaced every time.

---

## Why MetricAnchor?

Most AI analytics tools give confident answers with no way to verify them. One wrong number in a board presentation destroys trust in the entire tool. MetricAnchor is built differently.

| | MetricAnchor | Typical AI chatbot |
|---|:---:|:---:|
| Shows generated SQL for every answer | ✅ Always | ❌ Rarely |
| Business-term semantic layer (YAML) | ✅ | ❌ |
| Assumption transparency | ✅ Every answer | ❌ None |
| Confidence indicator | ✅ High / Medium / Low / Unsure | ❌ None |
| Data stays on your machine | ✅ Local-first | ❌ Sent to cloud |
| Open source and inspectable | ✅ | ❌ |
| Works with CSV and Parquet | ✅ | ⚠️ Limited |

---

## What it looks like

> Run `make up && make seed` and open http://localhost:3000 to see these screens live.
> Screenshots will be added here — see [docs/demo-flow.md](docs/demo-flow.md) for the full walkthrough.

| Screen | What you see |
|---|---|
| **Dataset profile** | Column types, null rates, distinct counts, sample values — profiled automatically on upload |
| **Ask page** | Question textarea + dataset selector + example chips; results appear inline without page reload |
| **Answer tab** | Plain-English answer sentence + KPI card (single metric) or bar/line chart (grouped results) |
| **SQL tab** | The exact `SELECT` statement that ran, formatted with syntax highlighting |
| **Assumptions tab** | Time expressions interpreted (e.g. `"last quarter" → Q4 2025, 2025-10-01 to 2025-12-31`) |
| **Provenance tab** | Business terms resolved: `"revenue" → metric:revenue (SUM(order_total) WHERE status='completed')` |
| **Developer mode** | Full pipeline trace: parser output → semantic mapper → SQL generator → execution engine |

---

## Quick Start

**Prerequisites:** Docker and Docker Compose.

> **No API key required.** The app runs in stub mode without any LLM — SQL generation, trust output, charts, and all three demo datasets work fully offline.

```bash
# Clone the repo
git clone https://github.com/your-username/metricanchor.git
cd metricanchor

# Copy the env template (no edits required for stub mode)
cp .env.example .env

# Start API + web UI
make up

# Generate the three sample datasets and seed the API
make generate-data
make seed

# Open the app
open http://localhost:3000
```

Services:
- **Web UI:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs (OpenAPI):** http://localhost:8000/api/docs

**To enable AI-quality answers:** set `LLM_API_KEY=sk-...` in `.env` and restart (`make down && make up`). Supports OpenAI, Anthropic, and any OpenAI-compatible endpoint (Ollama, LM Studio, etc.).

### No Docker?

See [docs/local-development.md](docs/local-development.md) for instructions to run the API and frontend locally without Docker using Python venv and `npm run dev`.

---

## How It Works

### 1. Upload your data
Drop a CSV or Parquet file. MetricAnchor profiles the schema automatically — column names, types, sample values, null rates, and distinct counts.

### 2. Define your business concepts (optional but powerful)
Write a YAML semantic model to define what "revenue," "active customer," or "churn rate" means for your dataset. This is the source of truth for every AI-generated answer.

```yaml
# semantic_models/retail_sales.yml
name: retail_sales
dataset: retail_sales
metrics:
  - name: revenue
    description: Total value of completed orders
    expression: SUM(order_total)
    filters:
      - column: status
        operator: "="
        value: "completed"
  - name: aov
    description: Average order value
    expression: SUM(order_total) / COUNT(DISTINCT order_id)
```

### 3. Ask questions in plain English
```
"What was revenue by product category last quarter?"
"Which region has the most active customers?"
"Has revenue grown month over month this year?"
```

### 4. Inspect the answer
Every response includes:
- **Result table and chart**
- **Generated SQL** — the exact query that was run
- **Term mappings** — which semantic model definitions were applied
- **Assumptions** — e.g., "'last quarter' interpreted as Q4 2025"
- **Confidence level** — High, Medium, Low, or Unsure, with a plain-English explanation

**Example API response** for `"revenue by region"`:
```json
{
  "answer": "The query returned 4 rows with columns: region, revenue.",
  "sql": "SELECT \"region\" AS region,\n  SUM(order_total) FILTER (WHERE status = 'completed') AS revenue\nFROM \"retail_sales\"\nGROUP BY \"region\"\nORDER BY revenue DESC",
  "columns": ["region", "revenue"],
  "rows": [["North", 56210.40], ["East", 54890.15], ["South", 50311.75], ["West", 46810.65]],
  "chart_type": "bar",
  "semantic_mappings": [
    {"phrase": "revenue", "resolved_to": "metric:revenue", "via": "exact"},
    {"phrase": "region",  "resolved_to": "dimension:region", "via": "exact"}
  ],
  "assumptions": [],
  "confidence": "high",
  "confidence_note": "All terms mapped exactly to defined metrics and dimensions.",
  "provenance": { "steps": ["question_parser", "semantic_mapper", "sql_generator", "execution_engine", "answer_formatter"] }
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Web UI (Next.js)                  │
│   Upload │ Ask │ Chart │ SQL Inspector │ Feedback         │
└──────────────────────────┬──────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────┐
│                     API (FastAPI)                        │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Ingest     │  │  Q&A Engine  │  │  Feedback      │  │
│  │  Service    │  │              │  │  Service       │  │
│  └──────┬──────┘  └──────┬───────┘  └────────────────┘  │
│         │                │                               │
│  ┌──────▼──────┐  ┌──────▼───────┐                      │
│  │  Schema     │  │  LLM Adapter │ ← OpenAI / Anthropic  │
│  │  Profiler   │  │  (provider-  │   / Ollama / any      │
│  └─────────────┘  │   agnostic)  │   OpenAI-compatible   │
│                   └──────┬───────┘                       │
│                          │                               │
│  ┌───────────────┐ ┌─────▼────────┐                      │
│  │ Semantic      │ │  Query       │                      │
│  │ Model Layer   │ │  Engine      │                      │
│  │ (YAML+JSON    │ │  (DuckDB)    │                      │
│  │  schema)      │ └─────────────┘                       │
│  └───────────────┘                                       │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  SQLite (metadata: datasets, questions, feedback)   │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**Key design decisions:**
- **DuckDB** for local analytics — fast, zero-config, handles CSV and Parquet natively
- **SQLite** for app metadata — no separate database server required
- **YAML semantic models** — version-controllable, human-readable, JSON schema validated
- **Provider-agnostic LLM adapter** — swap OpenAI for Anthropic or a local model without changing application code
- **Every layer is a clean interface** — semantic modeling, LLM orchestration, query execution, and UI are independently testable and replaceable

See [docs/architecture.md](docs/architecture.md) for a detailed walkthrough.

---

## Demo Scenarios

MetricAnchor ships with three demo datasets and pre-built semantic models.

### Retail Sales Analytics
Upload `sample_data/retail_sales.csv`. Ask:
- "What was revenue by product category last quarter?"
- "Which region has the most active customers?"
- "What is average order value for electronics vs. apparel?"

### Support Ticket Analytics
Upload `sample_data/support_tickets.csv`. Ask:
- "How many open tickets do we have by category?"
- "What is average resolution time for enterprise vs. free tier customers?"
- "What percentage of high-priority tickets are still open?"

### SaaS Funnel Analytics
Upload `sample_data/saas_funnel.csv`. Ask:
- "What is our current MRR by plan tier?"
- "What is our trial-to-paid conversion rate by acquisition channel?"
- "Which company size segment has the highest churn rate?"

---

## Configuration

All configuration is via environment variables. Copy `.env.example` to `.env` and fill in values.

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | `openai`, `anthropic`, or `openai_compatible` | `openai` |
| `LLM_API_KEY` | API key for your LLM provider | — |
| `LLM_MODEL` | Model name to use | `gpt-4o` |
| `LLM_BASE_URL` | Base URL (for local models like Ollama) | — |
| `DATA_DIR` | Where uploaded files are stored | `./data` |
| `DATABASE_URL` | SQLite connection string | `sqlite+aiosqlite:///./data/metricanchor.db` |

### Using a Local Model (Ollama)
```bash
# Install Ollama and pull a model
ollama pull llama3.2

# In .env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3.2
```

> **Note:** Local model SQL generation quality varies significantly. OpenAI gpt-4o or Anthropic claude-3-5-sonnet are recommended for best results.

---

## CLI

```bash
# From the repo root (uses the API venv)
cd MetricAnchor

# Check API status
apps/api/.venv/bin/python3 -m cli.main status

# Upload a dataset
apps/api/.venv/bin/python3 -m cli.main ingest sample_data/retail_sales.csv

# View column profile
apps/api/.venv/bin/python3 -m cli.main profile <dataset_id>

# Scaffold + upload a semantic model
apps/api/.venv/bin/python3 -m cli.main model init <dataset_id> -o my_model.yml
# Edit my_model.yml, then:
apps/api/.venv/bin/python3 -m cli.main model create <dataset_id> my_model.yml

# Ask a question
apps/api/.venv/bin/python3 -m cli.main ask <dataset_id> "revenue by region"
apps/api/.venv/bin/python3 -m cli.main ask <dataset_id> "top 5 products" --provenance

# Run the offline eval suite
apps/api/.venv/bin/python3 -m cli.main eval run
```

Or use the `make` shortcuts: `make cli-status`, `make cli-datasets`.

See [docs/local-development.md](docs/local-development.md#cli-usage) for the full CLI reference.

---

## Roadmap

| Phase | Theme | Status |
|---|---|---|
| 0 | Product definition and documentation | ✅ Done |
| 1 | Repo scaffold, CI, Docker, and core architecture | ✅ Done |
| 2 | File upload, schema profiling, DuckDB registration | ✅ Done |
| 3 | YAML semantic layer, validator, resolver | ✅ Done |
| 4 | LLM integration, SQL generation, trust output | ✅ Done |
| 5 | UI polish, charts, developer view, feedback flow | ✅ Done |
| 6 | Test suite, CLI, structured logging, docs, v1.0 | ✅ Done |
| Next | Database connectors, time-intelligence metrics, dbt import | Planned |

See [docs/roadmap.md](docs/roadmap.md) for the full roadmap and future directions.

---

## Contributing

MetricAnchor is designed to be a learning resource and a real open-source tool. Contributions are welcome.

- Read [CONTRIBUTING.md](CONTRIBUTING.md) to set up your environment and understand the PR workflow.
- Check [open issues](https://github.com/your-username/metricanchor/issues) for good first issues.
- Review [docs/architecture.md](docs/architecture.md) before adding new features.
- All PRs must include tests. See the [test guide](CONTRIBUTING.md#testing) for details.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

You are free to use, modify, and distribute MetricAnchor in commercial and non-commercial projects. Attribution is appreciated but not required.

---

## Acknowledgements

MetricAnchor is built on excellent open-source foundations:
[FastAPI](https://fastapi.tiangolo.com/) ·
[DuckDB](https://duckdb.org/) ·
[Next.js](https://nextjs.org/) ·
[Pydantic](https://docs.pydantic.dev/) ·
[SQLAlchemy](https://www.sqlalchemy.org/)
