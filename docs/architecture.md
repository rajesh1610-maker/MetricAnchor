# MetricAnchor — Architecture

**Version:** 1.0 (Phase 1)
**Last Updated:** 2026-03-19

---

## Overview

MetricAnchor is a local-first AI analytics copilot. Its architecture separates four concerns into distinct layers with clean interfaces:

1. **Ingest** — file upload, schema profiling, DuckDB registration
2. **Semantic modeling** — YAML definitions of business concepts, validated against a JSON schema
3. **Q&A engine** — LLM-generated SQL, grounded against the schema and semantic model, executed in DuckDB
4. **Trust output** — every answer includes SQL, term mappings, assumptions, and a confidence level

No layer has a hard dependency on another layer's internals. Each is independently testable.

---

## System Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                      Browser (Next.js)                          │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Upload   │  │ Ask      │  │ Trust Panel │  │ Semantic   │  │
│  │ Dataset  │  │ Question │  │ SQL · Terms │  │ Model      │  │
│  │          │  │          │  │ Assumptions │  │ Editor     │  │
│  └────┬─────┘  └────┬─────┘  └─────────────┘  └────────────┘  │
└───────┼─────────────┼────────────────────────────────────────────┘
        │ HTTP/JSON   │ HTTP/JSON
        ▼             ▼
┌────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                         │
│                                                                  │
│  POST /api/datasets          GET /api/datasets/{id}             │
│  POST /api/questions         GET /api/questions                 │
│  POST /api/semantic_models   GET /api/semantic_models/{id}      │
│  POST /api/questions/{id}/feedback                              │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      Services                             │  │
│  │                                                           │  │
│  │  IngestService      QuestionService    FeedbackService    │  │
│  │  SchemaProfiler     SemanticResolver   ConfidenceScorer   │  │
│  └──────┬────────────────────┬────────────────────────────┘  │
│         │                    │                                   │
│  ┌──────▼──────┐    ┌────────▼──────────────────────────────┐  │
│  │  packages/  │    │  packages/                            │  │
│  │  query_     │    │  llm_adapter/                         │  │
│  │  engine/    │    │                                       │  │
│  │  (DuckDB)   │    │  LLMAdapter (abstract)                │  │
│  └─────────────┘    │  ├── OpenAIAdapter                   │  │
│                     │  ├── AnthropicAdapter                │  │
│  ┌──────────────┐   │  └── OpenAICompatibleAdapter         │  │
│  │  packages/   │   │       (Ollama, LM Studio, etc.)      │  │
│  │  semantic_   │   └───────────────────────────────────────┘  │
│  │  model/      │                                               │
│  │  Validator   │                                               │
│  │  Resolver    │                                               │
│  └──────────────┘                                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  SQLite  (datasets · semantic_models · questions · feedback)│ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘

External (optional, configured via .env):
  OpenAI API  /  Anthropic API  /  Local Ollama
```

---

## Directory Structure

```
metricanchor/
├── apps/
│   ├── api/                  FastAPI application
│   │   ├── main.py           App entry point, middleware, router mounting
│   │   ├── routers/          One file per resource (datasets, questions, etc.)
│   │   ├── services/         Business logic (ingest, Q&A, feedback)
│   │   ├── models/           SQLAlchemy ORM models
│   │   ├── schemas/          Pydantic request/response schemas
│   │   ├── db.py             SQLite session factory
│   │   ├── config.py         Settings from environment variables
│   │   └── tests/            pytest unit + integration tests
│   │
│   └── web/                  Next.js 14 (App Router) frontend
│       └── src/app/          Pages and layouts
│
├── packages/
│   ├── semantic_model/       YAML format + JSON schema + validator + resolver
│   ├── query_engine/         DuckDB connector, query runner, result formatter
│   ├── llm_adapter/          Provider-agnostic LLM interface + adapters
│   └── shared/               Common types, exceptions, logging helpers
│
├── examples/                 Sample semantic model YAMLs with READMEs
├── sample_data/              Demo CSVs (retail, support, SaaS)
├── tests/                    End-to-end integration tests (full stack)
└── docs/                     Architecture, roadmap, connector guide
```

---

## Data Flow: Answering a Question

```
User types: "What was revenue by category last quarter?"
                    │
                    ▼
        QuestionService.ask(question, dataset_id)
                    │
         ┌──────────┴──────────┐
         │                     │
  Load schema profile    Load semantic model
  from SQLite            YAML from SQLite
         │                     │
         └──────────┬──────────┘
                    │
         PromptBuilder.build(schema, model, question)
                    │   → Structured prompt with:
                    │     - Table schema (columns, types)
                    │     - Semantic definitions (revenue = ...)
                    │     - Question
                    │
                    ▼
           LLMAdapter.complete(prompt)
                    │   → Raw LLM response
                    │
                    ▼
           SQLParser.extract(response)
                    │   → Validated SQL string
                    │
                    ▼
           QueryEngine.run(sql, dataset)
                    │   → Result rows (DuckDB)
                    │
                    ▼
           TrustBuilder.build(response, sql, model)
                    │   → {sql, assumptions, term_mappings, confidence}
                    │
                    ▼
       API returns QuestionResponse to the browser
```

---

## Key Design Decisions

### DuckDB for query execution

DuckDB is an in-process analytical database. It reads CSV and Parquet files natively, runs fast aggregations, and requires zero infrastructure. In V1, there is no separate database server — DuckDB runs embedded in the API process. This means:
- `make up` starts two containers (API and web), not three or four.
- There is no schema migration step for the analytics layer.
- DuckDB files are stored in the data volume alongside uploaded CSV/Parquet files.

Trade-off: DuckDB is single-writer. For V1 (single-user, local), this is fine. Multi-user deployments would need a different query engine.

### SQLite for metadata

Datasets, semantic models, questions, and feedback are stored in SQLite via SQLAlchemy. This keeps the metadata layer simple and eliminates another service dependency. SQLite performs well for the low-concurrency workload of a local analytics tool.

### YAML semantic models

Semantic models are stored in both the database (for the API to query quickly) and optionally in YAML files on disk (for version control). The YAML format is the source of truth for contributors. The JSON schema at `packages/semantic_model/schema.json` validates every model before it is accepted.

### Provider-agnostic LLM adapter

The `LLMAdapter` abstract class defines a single interface: `complete(prompt: str) -> str`. All provider-specific details (API keys, request format, retry logic, error handling) live inside the concrete adapter. The application code never imports an OpenAI or Anthropic SDK directly — only the adapter does.

This makes it straightforward to:
- Swap providers by changing one environment variable
- Add a new adapter without touching the Q&A engine
- Mock the adapter in tests without a live API key

### Trust output is mandatory

The `TrustBuilder` always runs. The API schema for `QuestionResponse` requires `sql`, `assumptions`, `term_mappings`, and `confidence` — they are not optional fields. If the LLM fails to produce parseable SQL, the response returns `confidence: "unsure"` with an explanation, not a fabricated answer.

---

## Package Interfaces

### `packages/query_engine`

```python
class QueryEngine:
    def register_dataset(self, name: str, file_path: str) -> DatasetProfile: ...
    def run(self, sql: str, dataset_name: str) -> QueryResult: ...
    def profile(self, dataset_name: str) -> DatasetProfile: ...
```

### `packages/llm_adapter`

```python
class LLMAdapter(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str: ...

class LLMAdapterFactory:
    @staticmethod
    def from_settings(settings: Settings) -> LLMAdapter: ...
```

### `packages/semantic_model`

```python
class SemanticModelValidator:
    def validate(self, model_dict: dict) -> ValidationResult: ...

class SemanticResolver:
    def resolve_terms(self, question: str, model: SemanticModel) -> list[TermMapping]: ...
    def to_sql_fragments(self, model: SemanticModel) -> list[str]: ...
```

---

## Environment Configuration

All runtime configuration flows through environment variables, loaded via `pydantic-settings` in `apps/api/config.py`. No hardcoded values in application code.

See `.env.example` for the full reference.

---

## Testing Strategy

| Layer | Tool | Location |
|---|---|---|
| API unit tests | pytest | `apps/api/tests/` |
| Package unit tests | pytest | `packages/*/tests/` |
| API integration tests | pytest + httpx | `apps/api/tests/integration/` |
| Full-stack integration | pytest | `tests/` |
| Browser smoke tests | Playwright | `apps/web/tests/e2e/` |

All tests run in CI on every pull request. See `.github/workflows/ci.yml`.
