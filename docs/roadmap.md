# MetricAnchor — Product Roadmap

**Version:** 1.0 (Phase 0 — Discovery)
**Last Updated:** 2026-03-19
**Model:** Now / Next / Later

---

## Roadmap Philosophy

MetricAnchor ships in small, working increments. Each phase must produce a runnable, testable artifact — not a design or a placeholder. The roadmap prioritizes trust signals and core Q&A quality over feature breadth. We would rather do three things exceptionally well than ten things poorly.

Phases map to GitHub milestones. Each milestone closes with:
- A passing test suite
- An updated README
- A git tag (e.g., `v0.1.0`)
- A short changelog entry

---

## Phase Overview

| Phase | Milestone | Theme | Status |
|---|---|---|---|
| 0 | Discovery | Product definition and documentation | Done |
| 1 | Foundation | Repo scaffold, CI, Docker, and core architecture | Planned |
| 2 | Ingest | File upload, schema profiling, DuckDB registration | Planned |
| 3 | Semantic Layer | YAML model format, validator, CLI, UI editor (basic) | Planned |
| 4 | Q&A Engine | LLM integration, SQL generation, execution, trust output | Planned |
| 5 | UI Polish | Charts, result tables, developer view, feedback flow | Planned |
| 6 | OSS Hardening | Tests, docs, CONTRIBUTING, issue templates, v1.0 tag | Planned |
| Later | Future | Database connectors, collaboration, enterprise features | Future |

---

## Phase 0 — Discovery (Current)

**Goal:** Define the product with enough clarity that any engineer can pick up Phase 1 without ambiguity.

**Deliverables:**
- `docs/product-spec.md` — problem statement, scope, principles, demo scenarios
- `docs/personas.md` — Maya (citizen developer) and Dev (analytics engineer)
- `docs/roadmap.md` — this document

**Success criteria:**
- A reader unfamiliar with the project can understand who it's for, what it does, and what V1 ships.
- No implementation started yet — discovery is complete.

---

## Phase 1 — Foundation

**Goal:** Production-quality repo scaffold. Everything a contributor needs to get started.

**Deliverables:**
- Monorepo structure: `backend/`, `frontend/`, `cli/`, `semantic_models/`, `docs/`, `tests/`
- `docker-compose.yml` with services: backend (FastAPI), frontend (Next.js), DuckDB via backend
- `.env.example` with all required environment variables documented
- `Makefile` with targets: `up`, `down`, `test`, `lint`, `validate`
- GitHub Actions CI: lint, test, build on every PR
- `README.md` — project overview, quick start, architecture diagram (text-based)
- `CONTRIBUTING.md` — setup, dev workflow, PR checklist, code style
- `CODE_OF_CONDUCT.md`
- Issue templates: bug report, feature request, semantic model contribution
- FastAPI app skeleton with health check endpoint
- Next.js app skeleton with layout and placeholder home page
- SQLite schema for app metadata (datasets, questions, feedback)
- pytest setup with one passing smoke test

**Out of scope for this phase:** Real upload, real Q&A, real LLM.

**Success criteria:**
- `docker-compose up` starts all services on a clean machine.
- `make test` runs and passes.
- CI passes on GitHub.

---

## Phase 2 — Ingest

**Goal:** Users can upload a CSV or Parquet file, see a schema profile, and have the data registered in DuckDB.

**Deliverables:**
- Upload endpoint: `POST /api/datasets` — accepts CSV or Parquet, validates, stores file, registers in DuckDB
- Schema profiler: column names, inferred types, sample values (first 5), null %, distinct count
- Dataset list endpoint: `GET /api/datasets`
- Dataset detail endpoint: `GET /api/datasets/{id}` — returns profile
- UI: file upload drop zone, dataset list view, schema profile view
- SQLite: `datasets` table with metadata (name, path, column_count, row_count, created_at)
- CLI: `metricanchor upload <file>` — uploads a file and prints the profile
- 500MB file size limit with a clear error message
- File type validation (CSV, Parquet only)
- pytest integration tests: upload valid CSV, upload Parquet, upload invalid file type, upload oversized file

**Success criteria:**
- Upload retail_sales.csv → schema profile appears in UI in under 3 seconds.
- All integration tests pass.
- CLI upload works and prints a readable profile.

---

## Phase 3 — Semantic Layer

**Goal:** Users can define business metrics and dimensions in YAML. The system validates and stores them.

**Deliverables:**
- YAML semantic model format defined and documented
- JSON schema for semantic models (with field descriptions)
- Example semantic models for all three demo datasets (retail, support, SaaS)
- Validation engine: `metricanchor validate <model.yml>` — checks structure, references valid columns
- Semantic model endpoints: `GET/POST/PUT /api/semantic_models`
- UI: basic metric editor (name, description, SQL expression, filters)
- SQLite: `semantic_models` table
- Business term resolver: maps user-defined terms to SQL fragments
- pytest tests: valid model, missing required field, invalid column reference

**YAML format preview:**
```yaml
name: retail_sales
dataset: retail_sales
metrics:
  - name: revenue
    description: Total completed order value
    expression: SUM(order_total)
    filters:
      - column: status
        operator: "="
        value: "completed"
dimensions:
  - name: product_category
    column: product_category
  - name: region
    column: region
```

**Success criteria:**
- `metricanchor validate retail_sales.yml` passes for a valid model, fails clearly for an invalid one.
- UI editor can create and save a metric definition.
- Resolver correctly maps "revenue" to `SUM(order_total) WHERE status = 'completed'`.

---

## Phase 4 — Q&A Engine

**Goal:** Users can ask questions in plain English and get SQL-backed answers with full trust output.

**Deliverables:**
- LLM adapter layer: provider-agnostic, supports OpenAI, Anthropic, and OpenAI-compatible local models
- Prompt builder: constructs grounded prompt from schema profile + semantic model + user question
- SQL generator: calls LLM, parses SQL from response
- SQL executor: runs generated SQL against DuckDB, returns result set
- Trust builder: extracts assumptions, maps business terms used, assigns confidence level
- Q&A endpoint: `POST /api/questions` — returns `{sql, results, trust_info, confidence}`
- Question history endpoint: `GET /api/questions`
- Feedback endpoint: `POST /api/questions/{id}/feedback`
- Fallback: if LLM is not configured, return a clear "LLM not configured" message — do not silently fail
- pytest tests: known-good Q&A pairs for all three demo datasets (minimum 5 per dataset)
- Trust output schema:
  ```json
  {
    "sql": "SELECT ...",
    "assumptions": ["'last month' interpreted as February 2026"],
    "term_mappings": [{"term": "revenue", "definition": "SUM(order_total) WHERE status='completed'"}],
    "confidence": "high",
    "confidence_notes": "All columns referenced exist. Semantic model definition applied."
  }
  ```

**Success criteria:**
- 80% of the 15 demo questions (5 per dataset) return correct SQL on first attempt.
- Every response includes trust output — no answer is returned without SQL.
- Confidence level is "unsure" when the LLM references a column that doesn't exist.

---

## Phase 5 — UI Polish

**Goal:** The UI is complete, usable, and serious-looking. Both personas can complete their full journey.

**Deliverables:**
- Question interface: text input, submit, streaming-style result reveal
- Result display: auto-selected bar or line chart (recharts), result table with column sorting
- Trust panel: expandable section showing SQL, term mappings, assumptions, confidence badge
- Developer view toggle: shows full LLM prompt and raw response (for Persona 2 / Dev)
- Feedback flow: "Report a problem" button → modal → records flag in SQLite
- Dataset manager: upload, view profile, delete
- Semantic model editor: view, edit metrics and dimensions in UI
- Question history: list of past questions with status (answered, flagged)
- Error states: clear messages for upload failure, LLM not configured, SQL execution error
- Accessibility: keyboard navigable, ARIA labels, color contrast AA compliant
- Playwright smoke tests: upload → define metric → ask question → see trust output

**Success criteria:**
- A new user can complete the full citizen developer journey (upload → define → ask → inspect) without reading documentation.
- Developer view shows the full LLM prompt.
- Playwright smoke test passes on CI.

---

## Phase 6 — OSS Hardening

**Goal:** The repo is genuinely GitHub-ready. A new contributor can onboard, contribute, and merge a PR cleanly.

**Deliverables:**
- Complete README: overview, quick start, architecture, configuration reference, FAQ
- CONTRIBUTING.md: local setup, coding standards, test requirements, PR checklist
- Architecture doc: `docs/architecture.md` — component diagram, data flow, key design decisions
- Connector guide: `docs/connectors.md` — how to write and register a connector
- Semantic model reference: `docs/semantic-models.md` — full YAML field reference with examples
- OpenAPI docs: auto-generated via FastAPI, served at `/api/docs`
- Test coverage: 80% line coverage on backend, documented exceptions
- Changelog: `CHANGELOG.md` following Keep a Changelog format
- GitHub release: v1.0.0 tag with release notes
- Demo data: three CSV sample datasets committed to `demo_data/`

**Success criteria:**
- A new contributor can follow CONTRIBUTING.md and run the test suite without help.
- The repo has no TODOs in user-facing code.
- v1.0.0 is tagged and released on GitHub.

---

## Later — Future Roadmap

These items are explicitly out of scope for V1 but represent the natural evolution of MetricAnchor. They are listed here to signal product direction and invite OSS community discussion.

### Database Connectors (High Value)
- PostgreSQL connector
- SQLite connector (direct DB, not just metadata)
- Snowflake read-only connector
- BigQuery read-only connector

Each connector implements the `BaseConnector` interface and is independently installable.

### Collaboration Features
- Shared workspaces (multiple users, shared semantic models)
- Question commenting and annotation
- Metric definition review workflow (propose → discuss → merge, GitHub-style)

### Semantic Layer Depth
- Calculated metrics (metric A / metric B)
- Time-intelligence functions (YoY, rolling 30-day, period-over-period)
- Semantic model inheritance and composition
- dbt integration: import metrics from dbt YAML files

### Enhanced Trust and Explainability
- Query plan visualization (show join strategy, filter order)
- Data lineage: which source columns contributed to this answer
- LLM prompt versioning: see how prompt changes affect answer quality
- Automated regression tests for Q&A quality

### Advanced Q&A
- Multi-turn conversation: follow-up questions that reference prior context
- Ambiguity resolution: when the question is unclear, ask a clarifying question before generating SQL
- Multi-dataset joins: answer questions that span multiple uploaded files

### Enterprise Features (V2+)
- SSO (SAML, OIDC)
- RBAC: dataset-level and metric-level permissions
- Audit log: who asked what, when
- Multi-tenancy: isolated workspaces per team
- Managed cloud deployment playbook (AWS, GCP)

### Developer Ecosystem
- Plugin marketplace for connectors and LLM adapters
- SDK for building custom trust validators
- Webhook support for feedback events

---

## Success Metrics — V1

| Metric | Target |
|---|---|
| Time to first answer (new user, clean install) | Under 10 minutes |
| Q&A accuracy on demo datasets | 80% correct SQL on first attempt |
| Test coverage (backend) | 80%+ line coverage |
| Playwright smoke test pass rate | 100% on CI |
| CONTRIBUTING.md onboarding time | Under 20 minutes for a developer |
| Docker cold start time | Under 60 seconds |
| Trust output completeness | 100% of answers include SQL, assumptions, confidence |

---

## Out-of-Scope List (Explicit)

The following are explicitly excluded from V1 to maintain focus and shipping velocity. Each item is a deliberate decision, not an oversight.

| Item | Reason Out of Scope |
|---|---|
| Multi-tenancy | Requires auth, RBAC, and isolation infrastructure not worth building before V1 validation |
| SSO / RBAC | Same as above; adds weeks of infra for a feature set local users don't need |
| Production database connectors | File uploads cover the primary use case; connectors are an extension point for V2 |
| Streaming LLM responses | Adds UI and API complexity; correctness and trust quality matter more than speed for V1 |
| Complex visualizations (maps, funnels, scatter) | Bar and line charts cover 80% of analytics use cases; add the rest in V2 based on user feedback |
| Mobile / native app | Web-first; no meaningful analytics work happens on mobile in V1 target personas |
| Fine-tuning or custom model training | Out of scope for an open-source analytics tool; users choose their LLM provider |
| Scheduled data refreshes | File uploads are one-time; pipelines are a V2 concept |
| Billing or monetization | OSS V1 is free; business model is a future decision |
| Cloud deployment playbooks | `docker-compose` is sufficient for V1; cloud guides come after validation |
