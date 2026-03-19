# MetricAnchor — Architecture

**Version:** 2.0 (Phase 8)
**Last Updated:** 2026-03-19

## Overview

MetricAnchor is a **trust-first analytics copilot**. Users ask natural-language questions against their data; the system returns the answer alongside the exact SQL, how every business term was resolved, what assumptions were made, and a confidence score.

The key design principle: **the LLM never writes SQL**. SQL is generated deterministically from a semantic model by code. The LLM is used only to parse intent and format the final answer.

---

## System Components

```
┌──────────────────────────────────────────────────────────┐
│                        Browser                           │
│   Next.js 14 App Router  (apps/web/src/)                │
│   Ask · Datasets · Semantic Models · History             │
└───────────────────┬──────────────────────────────────────┘
                    │ HTTP (JSON)
┌───────────────────▼──────────────────────────────────────┐
│                    FastAPI API  (apps/api/)               │
│                                                          │
│  Routers:  /datasets  /semantic_models  /questions       │
│            /health                                       │
│                                                          │
│  Services: IngestService  QuestionService                │
│            SemanticModelService                          │
│                                                          │
│  Storage:  SQLite (metadata)  ·  DuckDB (queries)        │
│            Uploads dir (raw files)                       │
└───────┬──────────────────────────┬───────────────────────┘
        │                          │
┌───────▼──────────┐  ┌────────────▼───────────────────────┐
│  packages/       │  │  packages/                         │
│  llm_adapter     │  │  semantic_model/                   │
│  (OpenAI /       │  │    validator.py  resolver.py       │
│   Anthropic /    │  │  query_engine/                     │
│   stub)          │  │    pipeline.py   engine.py         │
└──────────────────┘  └────────────────────────────────────┘
```

---

## Request Flow — Asking a Question

```
POST /api/questions
  { "question": "revenue by region last month", "dataset_id": "…" }

  1. QuestionService.ask()
     ├── load Dataset (SQLite)
     ├── load SemanticModel (SQLite)
     └── execute_pipeline(question, view_name, model_def, engine, llm)

         Step 1  question_parser
         ├── if llm.is_stub → _parse_stub()   (regex-based, zero latency)
         └── else           → _parse_with_llm()  (LLM JSON extraction)
               → ParsedIntent { question_type, candidate_terms,
                                time_expression, explicit_group_by,
                                limit, sort_direction }

         Step 2  semantic_mapper
         └── _map_intent()
               → maps candidate_terms → TermMapping (metric / dimension)
               → via: exact | alias | synonym | default
               → MappingResult { resolved_metrics, resolved_dimensions,
                                  unmapped, needs_clarification }

         Step 3  time_resolver
         └── _parse_time_expression("last month", today)
               → TimeRange { start: "2026-02-01", end: "2026-03-01" }

         Step 4  sql_generator
         └── _generate_sql()  — template-based, NEVER LLM
               SELECT <metric_exprs>
               FROM   "<view_name>"
               WHERE  <time_filter> AND <business_rules>
               GROUP BY <dimensions>
               ORDER BY <first_metric> DESC
               LIMIT <n>

         Step 5  sql_validator
         └── _validate_sql_static()  — deny-list: DROP, DELETE, INSERT …
             + DuckDB EXPLAIN (syntax check)

         Step 6  execution_engine
         └── engine.run(sql)  → (columns, rows)

         Step 7  answer_formatter
         ├── if llm.is_stub → _format_stub()
         └── else           → _format_with_llm()  (max 10 rows sent to LLM)

         Step 8  provenance_builder
         └── assemble PipelineResult with:
               sql, columns, rows, chart_type, semantic_mappings,
               assumptions, caveats, confidence, confidence_note,
               provenance (all step outputs), execution_ms

  2. Question persisted to SQLite
  3. QuestionResponse returned (mirrors PipelineResult + id, created_at)
```

---

## Data Flow — Ingesting a Dataset

```
POST /api/datasets  (multipart/form-data, file=<csv|parquet>)

  IngestService.upload()
  1. Validate extension (.csv / .parquet)
  2. Read bytes, check < 500 MB limit
  3. Write to data/uploads/<dataset_id>/<filename>
  4. DuckDB: CREATE OR REPLACE VIEW "<view_name>" AS SELECT * FROM '<path>'
  5. profile_dataset() → per-column stats (type, nulls, distinct, min/max, samples)
  6. Save Dataset row to SQLite
  7. Return DatasetResponse (id, profile, row_count, …)
```

---

## Semantic Model

A semantic model is a YAML/JSON document that maps business vocabulary to SQL expressions. It is the single source of truth for term resolution.

```yaml
name: retail_sales
dataset: retail_sales           # must match DuckDB view name
grain: one row per order line
time_column: order_date

metrics:
  - name: revenue
    expression: SUM(revenue)
    aliases: [sales, total_revenue, gross_revenue]
    format: currency

dimensions:
  - name: region
    column: region
    aliases: [geo]
    values: [North, South, East, West]

synonyms:
  - phrase: top selling
    maps_to: metric:revenue

business_rules:
  - name: exclude_returns
    filter: "is_return = 'false'"
    applies_to: [metric:revenue]

caveats:
  - Revenue is gross; returns are not deducted.
```

The `SemanticResolver` builds an inverted index (phrase → metric/dimension) at construction time. Resolution is O(1) per term lookup.

---

## Packages

| Package | Purpose |
|---------|---------|
| `packages/semantic_model/` | Model validation (JSON schema + semantic rules), term resolver |
| `packages/query_engine/` | DuckDB wrapper, data profiler, analytics pipeline |
| `packages/llm_adapter/` | Async HTTP client for OpenAI / Anthropic / compatible APIs |
| `packages/shared/` | Shared utilities |

All packages are pure Python, importable without installation by adding the repo root to `sys.path`.

---

## Confidence Scoring

| Level | Condition |
|-------|-----------|
| `high` | All terms matched exactly (not via alias/default), no unmapped terms |
| `medium` | Some terms matched via alias/synonym, a default metric was used, or there are unmapped terms |
| `low` | No metrics resolved (but clarification not triggered) |
| `clarification_needed` | No metrics identified — returns a clarifying question |

---

## Chart Type Routing

| Condition | Chart |
|-----------|-------|
| No dimensions | `metric` (KPI card) |
| > 25 rows or > 1 dimension | `table` |
| 1 date dimension or question_type=trend | `line` |
| question_type=ranking | `bar` |
| 1 dim + 1 metric | `bar` |
| 1 dim + multiple metrics | `grouped_bar` |

---

## Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| API | FastAPI + Pydantic v2 | Async, typed, auto OpenAPI docs |
| Analytics DB | DuckDB | Columnar, zero-config, fast aggregations on CSV |
| Metadata DB | SQLite + SQLAlchemy async | Lightweight persistence, no external server |
| LLM | OpenAI / Anthropic (configurable) | Provider-agnostic via httpx adapter |
| Frontend | Next.js 14 App Router + Tailwind | React server components, dark theme |
| Testing | pytest + pytest-asyncio | Async-native, parametrize for evals |
| CLI | Typer + Rich | Ergonomic, coloured output |
