# First 10 GitHub Issues

A suggested set of opening issues for when MetricAnchor goes public. These seed the issue tracker with actionable, well-scoped work that signals a healthy, active project to potential contributors.

Each issue is designed to:
- Be completable by a new contributor
- Produce a real improvement (not busy-work)
- Have unambiguous success criteria
- Demonstrate that the maintainers have thought about what they want

---

## How to use this file

When publishing the repo:
1. Create each issue from the sections below.
2. Apply the labels listed (create the labels first — see labels table at the bottom).
3. Assign `good first issue` to issues in Tier 1 and 2.
4. Pin 2–3 issues that you most want help with.

---

## Issue 1 — Add example semantic model for a new domain

**Title:** `[Good First Issue] Add an example semantic model for a new domain`
**Labels:** `good first issue`, `semantic-model`, `documentation`
**Milestone:** v1.1.0

MetricAnchor ships with three demo datasets (retail sales, support tickets, SaaS funnel). Each has a matching semantic model.

More example models help users understand the YAML format and give them a head start for their own data.

**To contribute:**
1. Pick a domain (e-commerce, HR, finance, logistics, healthcare, etc.).
2. Create `examples/<domain>/semantic_model.yml` following `examples/retail_sales/`.
3. Add a sample CSV to `sample_data/` (200–500 rows, no real PII, deterministic).
4. Validate: `make validate`
5. Add a short `examples/<domain>/README.md` with 3–5 example questions.
6. Open a PR.

**Success criteria:** `make validate` passes; example questions return sensible answers in stub mode.

See [docs/good-first-issues.md](good-first-issues.md#gfi-01-add-an-example-semantic-model-for-a-new-domain) for full details.

---

## Issue 2 — Add `--json` flag to the `profile` CLI command

**Title:** `[Good First Issue] CLI: add --json flag to 'profile' command`
**Labels:** `good first issue`, `cli`, `enhancement`
**Milestone:** v1.1.0

The `metricanchor profile <dataset_id>` command outputs a Rich table — great for humans, hard to pipe into other tools.

**Proposed change:** Add `--json / --no-json` option. When set, print the profile as JSON (`json.dumps(...)`) instead of the Rich table.

**Files:** `cli/main.py`

**Tests required:** Unit test checking output format.

**Success criteria:** `metricanchor profile <id> --json | jq .columns` works correctly.

---

## Issue 3 — Add `row_count` to dataset list API response

**Title:** `API: include row_count in GET /api/datasets response`
**Labels:** `enhancement`, `api`
**Milestone:** v1.1.0

`GET /api/datasets` returns dataset metadata but omits `row_count`. Users need to click into a dataset to see its size — a round-trip that could be avoided.

**Proposed change:** Add `row_count: int | None` to the `DatasetListItem` response schema and populate it from the stored `Dataset` record.

**Files:** `apps/api/schemas/datasets.py`, `apps/api/routers/datasets.py`

**Tests required:** Update or add a test checking the list response includes `row_count`.

---

## Issue 4 — Surface request ID in API error responses

**Title:** `API: include request_id in error response bodies`
**Labels:** `enhancement`, `api`, `observability`
**Milestone:** v1.1.0

The API injects `X-Request-ID` headers but not in the JSON body of error responses. This makes it harder to correlate client-side errors with server logs.

**Proposed change:** For non-2xx JSON responses, inject `"request_id"` into the response body. Leave non-JSON responses untouched.

**Files:** `apps/api/main.py`

**Tests required:** Test that a 422 response body contains `request_id`.

---

## Issue 5 — Add column-reference validation to semantic model creation

**Title:** `Semantic model: warn when metric/dimension references unknown column`
**Labels:** `enhancement`, `semantic-model`, `api`
**Milestone:** v1.1.0

The validator checks YAML structure but has no visibility into the actual dataset columns. When creating a model via `POST /api/semantic_models`, the API has both the model and the dataset profile — it should warn if a column reference doesn't match.

**Proposed change:** After model creation, compare extracted column references (from `expression` fields and dimension `column` fields) against the dataset profile. Return mismatches as non-fatal `warnings` in the response.

**Files:** `apps/api/routers/semantic_models.py` (or a new service layer)

**Tests required:** Test that a model referencing an unknown column returns a warning but is still created.

---

## Issue 6 — Add `--provenance` output to `ask` CLI command

**Title:** `[Good First Issue] CLI: implement --provenance flag for 'ask' command`
**Labels:** `good first issue`, `cli`, `enhancement`
**Milestone:** v1.1.0

The `metricanchor ask` command has a `--provenance` flag that is accepted but doesn't do anything yet. It should print the `term_mappings` and `assumptions` from the API response.

**Files:** `cli/main.py`

**Success criteria:** `metricanchor ask <id> "revenue by region" --provenance` prints term mappings and assumptions below the result table using Rich panels.

---

## Issue 7 — Write setup instructions for Windows (WSL2)

**Title:** `Docs: add Windows WSL2 setup instructions`
**Labels:** `documentation`, `help wanted`
**Milestone:** v1.1.0

The local development guide covers macOS and Linux. Contributors on Windows need WSL2. We'd like to document:
- Which WSL2 distribution to use
- Any Docker Desktop for Windows config required
- Any path or line-ending issues to watch out for

This is a research and documentation issue — no code changes required.

**Files:** `docs/local-development.md`

---

## Issue 8 — Add a PostgreSQL connector (read-only)

**Title:** `Connector: read-only PostgreSQL support`
**Labels:** `enhancement`, `connector`, `help wanted`
**Milestone:** v2.0.0

MetricAnchor currently supports CSV and Parquet file uploads. A PostgreSQL connector would let users point the system at a database table instead.

**Scope:** Read-only. Register a query result as a DuckDB view using DuckDB's `postgres_scan` extension.

**Requirements:**
- Implement `BaseConnector` interface
- Connection string via environment variable or UI config
- Integration test against a Dockerized Postgres instance
- Documentation in `docs/connectors.md`

This is a larger effort — ideal for a contributor who wants a substantial project.

---

## Issue 9 — Add time-intelligence metrics to the semantic model format

**Title:** `Semantic model: add period-over-period and rolling window metric types`
**Labels:** `enhancement`, `semantic-model`
**Milestone:** v2.0.0

Advanced analytics questions like "revenue vs. last quarter" or "30-day rolling average" require time-intelligence functions not currently expressible in the semantic model YAML.

**Proposed additions:**
- `time_compare: true` on a metric — generates a period-over-period SQL pattern
- `rolling_window: 30` on a metric — generates a rolling `N`-day aggregate

This is a design-heavy issue. Please comment with a proposed YAML format before writing code.

---

## Issue 10 — Add dbt metric import

**Title:** `Integration: import metrics from dbt YAML files`
**Labels:** `enhancement`, `integration`
**Milestone:** v2.0.0

Teams using dbt already have metric and dimension definitions in dbt's semantic layer YAML format. A one-way import tool (`metricanchor model import --from-dbt metrics.yml`) would let these teams adopt MetricAnchor without duplicating their definitions.

**Scope for a first pass:**
- Parse dbt metric YAML (name, description, expression, dimensions)
- Map to MetricAnchor semantic model format
- Output as a `semantic_model.yml` file

This is a research issue first — please comment with the dbt YAML schema version you'd target.

---

## Suggested Labels

Create these labels when setting up the repo:

| Label | Color | Description |
|---|---|---|
| `bug` | `#d73a4a` | Something isn't working |
| `enhancement` | `#a2eeef` | New feature or improvement |
| `documentation` | `#0075ca` | Improvements or additions to docs |
| `good first issue` | `#7057ff` | Well-scoped for first-time contributors |
| `help wanted` | `#008672` | Extra attention is needed |
| `question` | `#d876e3` | Further information is requested |
| `triage` | `#e4e669` | Needs review before action |
| `wontfix` | `#ffffff` | This will not be worked on |
| `duplicate` | `#cfd3d7` | This issue or PR already exists |
| `semantic-model` | `#bfd4f2` | Related to the YAML semantic model format |
| `api` | `#f9d0c4` | Related to the FastAPI backend |
| `cli` | `#c2e0c6` | Related to the Typer CLI |
| `connector` | `#fef2c0` | Data source connector (PostgreSQL, etc.) |
| `integration` | `#e99695` | Third-party integration |
| `observability` | `#c5def5` | Logging, metrics, tracing |
| `performance` | `#e4b9b9` | Speed or memory improvement |
| `breaking-change` | `#b60205` | Changes the public API or model format |
