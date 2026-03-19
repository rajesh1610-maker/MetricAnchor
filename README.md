# MetricAnchor

**Grounded answers for business data.**

[![CI](https://github.com/your-username/metricanchor/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/metricanchor/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

MetricAnchor is an open-source AI analytics copilot that helps you upload tabular data, define business concepts in plain English, and ask questions in natural language — with every answer showing its SQL, assumptions, business-term mappings, and confidence level.

**Trust is the feature.** No black boxes. Every answer is inspectable.

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

## Screenshots

> _Screenshots will be added after Phase 5 (UI Polish). For now, see the demo scenarios below._

---

## Quick Start

**Prerequisites:** Docker and Docker Compose.

```bash
# Clone the repo
git clone https://github.com/your-username/metricanchor.git
cd metricanchor

# Copy environment config
cp .env.example .env
# Edit .env and add your LLM API key (OpenAI, Anthropic, or local Ollama)

# Start all services
make up

# Load the sample datasets
make seed

# Open the app
open http://localhost:3000
```

The app will be running at:
- **Web UI:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs (OpenAPI):** http://localhost:8000/api/docs

### No Docker? Local Dev Setup

See [CONTRIBUTING.md](CONTRIBUTING.md#local-development-without-docker) for instructions to run the backend and frontend locally without Docker.

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
| `DATABASE_URL` | SQLite connection string | `sqlite:///./metricanchor.db` |

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
# Install the CLI
pip install -e "packages/semantic_model[cli]"

# Upload a dataset
metricanchor upload sample_data/retail_sales.csv

# Validate a semantic model
metricanchor validate examples/retail_sales/semantic_model.yml

# Ask a question from the terminal
metricanchor ask "What was revenue last quarter?" --dataset retail_sales
```

---

## Roadmap

| Phase | Theme | Status |
|---|---|---|
| 0 | Product definition and documentation | ✅ Done |
| 1 | Repo scaffold, CI, Docker, and core architecture | ✅ Done |
| 2 | File upload, schema profiling, DuckDB registration | Planned |
| 3 | YAML semantic layer, validator, CLI | Planned |
| 4 | LLM integration, SQL generation, trust output | Planned |
| 5 | UI polish, charts, developer view, feedback flow | Planned |
| 6 | OSS hardening, full test suite, v1.0 release | Planned |

See [docs/roadmap.md](docs/roadmap.md) for the full roadmap.

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
