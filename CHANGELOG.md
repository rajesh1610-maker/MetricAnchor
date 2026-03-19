# Changelog

All notable changes to MetricAnchor are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- Nothing yet — see [docs/roadmap.md](docs/roadmap.md) for what's next.

---

## [1.0.0] - 2026-03-19

### Added
- **Complete test suite** — unit tests, integration tests, and offline eval suite with 13 deterministic question-level assertions; no LLM or running server required for CI
- **Playwright end-to-end smoke tests** — 7 UI flows covering homepage, dataset management, ask page, and dev-mode toggle (`tests/e2e/`)
- **Offline eval runner** — `evals/runner.py` with human-readable report; `evals/last_run.json` written after every run; filterable by dataset
- **CLI** (`cli/`) — Typer/Rich terminal interface with commands: `ingest`, `profile`, `datasets`, `ask`, `status`; subgroups `model init/create/list/validate` and `eval run`
- **Structured logging** — `LOG_FORMAT=human` (coloured terminal) or `LOG_FORMAT=json` (structured, for production); noisy libraries silenced; request-ID middleware with per-request timing
- **Enriched health endpoint** — `GET /api/health` returns `uptime_seconds`, `llm_provider`, `llm_model`, `llm_live`, `python_version` as typed Pydantic response
- **`apps/api/.env.example`** — full environment variable reference with defaults and comments
- **`docs/architecture.md`** — complete system diagram, 8-step request flow, data ingestion flow, package responsibilities, confidence scoring table, chart routing table
- **`docs/api.md`** — all endpoint groups documented with request/response examples and error codes
- **`docs/local-development.md`** — Docker quickstart, no-Docker venv setup, full env-var reference table, test command reference, CLI usage guide, project structure tree
- **`docs/evals.md`** — eval runner usage, `EvalCase` format, `ValueCheck` operators, all 13 current eval cases with ground-truth values, CI integration guide

### Changed
- `Makefile` rewritten with `PYTHON`, `PYTEST`, `CLI` variables pointing into the API venv; new targets: `test-api`, `test-coverage`, `status`, `cli-datasets`, `cli-status`; `test` target outputs section headers
- `README.md` roadmap updated to reflect current completion status
- `CONTRIBUTING.md` test requirements table updated to match new test structure (`tests/unit/`, `tests/integration/`, `evals/`)

---

## [0.3.0] - 2026-03-19

### Added
- **Complete question pipeline** (`packages/query_engine/pipeline.py`) — stub and LLM modes; `_parse_stub()`, `_generate_sql()`, `_validate_sql_static()`, `_compute_confidence()`, `_suggest_chart()`, `_parse_time_expression()`
- **Provider-agnostic LLM adapter** (`packages/llm_adapter/`) — OpenAI, Anthropic, and `openai_compatible` (Ollama) providers; async streaming interface; stub client for tests/CI
- **Trust output** — every answer includes: generated SQL, term mappings, assumptions list (e.g., `"'last quarter' interpreted as Q4 2025"`), confidence level (`high/medium/low/clarification_needed`), chart type suggestion
- **Time-range parsing** — `_parse_time_expression()` handles: today, yesterday, this/last week/month/quarter/year, MTD, QTD, YTD, last N days, custom ISO ranges
- **SQL static validator** — deny-list using `\b` word-boundary regex; blocks `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `TRUNCATE`, `CREATE`, `REPLACE`, `ATTACH`, `DETACH`, `PRAGMA`, `COPY`, `EXPORT`, `IMPORT`, `LOAD`, `INSTALL`
- **Question history** — `GET /api/questions` with pagination; `GET /api/questions/{id}`
- **Feedback endpoint** — `POST /api/questions/{id}/feedback`
- **Full Next.js UI** — question interface with result table, auto-selected chart (bar/line/metric KPI), trust panel (SQL inspector, term mappings, assumptions, confidence badge), developer-mode toggle showing raw LLM prompt/response
- **Recharts integration** — bar chart, line chart, and single-metric KPI card; responsive layout

---

## [0.2.0] - 2026-03-19

### Added
- **YAML semantic model format** — `name`, `dataset`, `description`, `metrics` (name, expression, description, aliases, filters), `dimensions` (name, column, description, aliases, is_date), `synonyms`, `time_column`
- **JSON schema validation** (`packages/semantic_model/schema.json`) — validates all fields and types
- **Semantic model validator** (`packages/semantic_model/validator.py`) — structural validation plus semantic rules: duplicate names, invalid synonym targets, metric name safety; returns `ValidationResult` with errors and warnings
- **Semantic resolver** (`packages/semantic_model/resolver.py`) — inverted index at init; `resolve(question)` → `ResolvedContext`; `metric_sql(name)` returns expression with FILTER applied
- **Semantic model endpoints** — `POST /api/semantic_models`, `GET /api/semantic_models`, `GET /api/semantic_models/{id}`, `PUT /api/semantic_models/{id}`, `DELETE /api/semantic_models/{id}`
- **Example semantic models** — `examples/retail_sales/`, `examples/support_tickets/`, `examples/saas_funnel/` with full metric and dimension definitions
- **UI: semantic model editor** — view and edit model from the web interface

---

## [0.1.0] - 2026-03-19

### Added
- **File upload** — `POST /api/datasets` accepts CSV and Parquet; validates type and size; stores file; registers view in DuckDB
- **Schema profiler** — column names, inferred types, null rates, distinct counts, sample values (first 5 rows)
- **DuckDB registration** — in-process analytics engine; views registered per dataset; survives restart via re-registration from stored files
- **Dataset endpoints** — `GET /api/datasets`, `GET /api/datasets/{id}`, `DELETE /api/datasets/{id}`
- **SQLite metadata store** — `Dataset`, `SemanticModel`, `Question`, `Feedback` ORM models via SQLAlchemy async; `aiosqlite` driver
- **Sample data generator** — `sample_data/generate.py`; deterministic seed=42; produces `retail_sales.csv` (774 rows), `support_tickets.csv` (256 rows), `saas_funnel.csv` (320 rows)
- **Seed script** — `scripts/seed_demo.py` — uploads all three CSVs and creates semantic models via API; `--reset` flag to re-seed from scratch
- **UI: dataset manager** — file upload drop zone, dataset list, schema profile view with column type badges

---

## [0.0.1] - 2026-03-19

### Added
- Monorepo scaffold: `apps/api/`, `apps/web/`, `packages/`, `cli/`, `tests/`, `evals/`, `docs/`
- `docker-compose.yml` — `api` (FastAPI/uvicorn) and `web` (Next.js) services with health checks and shared data volume
- `Makefile` — `up`, `down`, `build`, `logs`, `health`, `test`, `lint`, `validate`, `generate-data`, `seed`, `seed-reset`, `clean`
- GitHub Actions CI — lint, test, build on every push and PR to `main`
- FastAPI app skeleton — `main.py`, `config.py` (pydantic-settings), `models.py` (SQLAlchemy ORM), router stubs
- Next.js 14 app skeleton — App Router, shared layout, placeholder home page
- Community files — `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`
- GitHub issue templates — bug report, feature request, question (YAML structured forms)
- GitHub PR template
- `docs/product-spec.md`, `docs/personas.md`, `docs/roadmap.md`, `docs/semantic-model.md`, `docs/business-metrics-guide.md`
