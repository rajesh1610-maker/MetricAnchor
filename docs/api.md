# MetricAnchor API Reference

**Base URL:** `http://localhost:8000`
**Interactive docs:** `http://localhost:8000/api/docs` (Swagger UI)
**OpenAPI schema:** `http://localhost:8000/api/openapi.json`

All request/response bodies are JSON. Successful creates return HTTP 201.
Errors return a `{ "detail": "..." }` body.

---

## Health

### `GET /api/health`

Returns API status and runtime configuration.

**Response 200**
```json
{
  "status": "ok",
  "service": "metricanchor-api",
  "version": "0.3.0",
  "timestamp": "2026-03-19T12:00:00+00:00",
  "uptime_seconds": 3600,
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "llm_live": true,
  "python_version": "3.11.14"
}
```

`llm_live: false` means the API key is missing or is the test stub. The pipeline will use rule-based parsing and templated answers — fully functional, just without LLM quality.

---

## Datasets

### `POST /api/datasets`

Upload a CSV or Parquet file. Returns a full column profile.

**Request:** `multipart/form-data`
- `file` — `.csv` or `.parquet`, max 500 MB

**Response 201**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "retail_sales",
  "original_filename": "retail_sales.csv",
  "file_format": "csv",
  "row_count": 774,
  "column_count": 8,
  "profile": {
    "row_count": 774,
    "column_count": 8,
    "columns": [
      {
        "name": "order_date",
        "data_type": "DATE",
        "null_count": 0,
        "null_pct": 0.0,
        "distinct_count": 365,
        "is_numeric": false,
        "is_date": true,
        "is_bool": false,
        "min_value": "2025-01-01",
        "max_value": "2026-02-28",
        "sample_values": ["2025-03-14", "2025-07-22"]
      }
    ]
  },
  "created_at": "2026-03-19T10:00:00+00:00"
}
```

**Errors**
- `413` — file exceeds 500 MB
- `415` — unsupported file type

---

### `GET /api/datasets`

List all uploaded datasets.

**Response 200**
```json
{
  "datasets": [ ... ],
  "total": 3
}
```

---

### `GET /api/datasets/{dataset_id}`

Get a single dataset with its full column profile.

**Errors:** `404` if not found.

---

### `GET /api/datasets/{dataset_id}/rows`

Preview sample rows.

**Query params**
- `limit` — rows to return (1–500, default 100)
- `offset` — pagination offset (default 0)

**Response 200**
```json
{
  "columns": ["order_date", "region", "product", "revenue"],
  "rows": [["2025-03-14", "North", "Electronics", 124.99]],
  "total_returned": 100
}
```

---

### `DELETE /api/datasets/{dataset_id}`

Delete a dataset. Returns `204 No Content`.

---

## Semantic Models

### `POST /api/semantic_models`

Create a semantic model for a dataset.

**Request body**
```json
{
  "dataset_id": "3fa85f64-...",
  "name": "retail_sales",
  "definition": {
    "name": "retail_sales",
    "dataset": "retail_sales",
    "description": "Retail order analytics",
    "grain": "one row per order line",
    "time_column": "order_date",
    "metrics": [
      {
        "name": "revenue",
        "description": "Total gross revenue",
        "expression": "SUM(revenue)",
        "aliases": ["sales", "total_revenue"],
        "format": "currency"
      }
    ],
    "dimensions": [
      {
        "name": "region",
        "column": "region",
        "description": "Sales region",
        "aliases": ["geo"]
      }
    ]
  }
}
```

**Response 201** — created model with `id`.

**Errors**
- `422` — definition fails JSON schema or semantic validation (errors listed in `detail`)

---

### `GET /api/semantic_models`

List semantic models.

**Query params**
- `dataset_id` — filter by dataset (optional)

---

### `GET /api/semantic_models/{model_id}`

Get a single semantic model.

---

### `PUT /api/semantic_models/{model_id}`

Update a semantic model definition.

**Request body**
```json
{
  "name": "retail_sales_v2",
  "definition": { ... }
}
```

---

### `DELETE /api/semantic_models/{model_id}`

Delete a semantic model. Returns `204 No Content`.

---

### `POST /api/semantic_models/validate`

Validate a model definition **without saving it**.

**Request body** — the raw model definition dict (not wrapped in `dataset_id`/`name`).

**Response 200**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Metric 'revenue' has no aliases. Add common synonyms for better natural-language matching."
  ]
}
```

---

### `GET /api/semantic_models/{model_id}/export`

Export a model as YAML text.

**Response** — `text/yaml`, raw YAML string.

---

## Questions

### `POST /api/questions`

Ask a natural-language analytics question. This is the core pipeline endpoint.

**Request body**
```json
{
  "question": "revenue by region last month",
  "dataset_id": "3fa85f64-...",
  "model_id": null
}
```

- `model_id` is optional. If omitted, the most recently updated model for the dataset is used.

**Response 201**
```json
{
  "id": "7abc1234-...",
  "dataset_id": "3fa85f64-...",
  "question": "revenue by region last month",
  "answer": "North led with $52,400 in revenue last month, followed by South at $48,200.",
  "sql": "SELECT\n  \"region\" AS region,\n  SUM(revenue) AS revenue\nFROM \"retail_sales\"\nWHERE \"order_date\" >= '2026-02-01'\n  AND \"order_date\" < '2026-03-01'\nGROUP BY \"region\"\nORDER BY revenue DESC",
  "columns": ["region", "revenue"],
  "rows": [["North", 52400.0], ["South", 48200.0], ["East", 43100.0], ["West", 38900.0]],
  "row_count": 4,
  "chart_type": "bar",
  "semantic_mappings": [
    { "phrase": "revenue", "resolved_to": "metric:revenue", "resolved_name": "revenue", "type": "metric", "via": "exact" },
    { "phrase": "region", "resolved_to": "dimension:region", "resolved_name": "region", "type": "dimension", "via": "exact" }
  ],
  "assumptions": [
    "Interpreted 'last month' as 2026-02-01 to 2026-02-28."
  ],
  "caveats": ["Revenue is gross; returns are not deducted."],
  "confidence": "high",
  "confidence_note": "All terms mapped exactly to defined metrics and dimensions.",
  "clarifying_question": null,
  "provenance": {
    "steps": [
      { "step": "question_parser", "output": { "question_type": "breakdown", ... } },
      { "step": "semantic_mapper", "output": { ... } },
      { "step": "time_resolver", "output": { "start": "2026-02-01", "end": "2026-03-01", ... } },
      { "step": "sql_generator", "output": { "sql": "SELECT ..." } },
      { "step": "execution_engine", "output": { "row_count": 4, "execution_ms": 12 } }
    ],
    "model_name": "retail_sales",
    "view_name": "retail_sales"
  },
  "execution_ms": 14,
  "error": null,
  "created_at": "2026-03-19T12:00:00+00:00"
}
```

**Confidence levels**

| Value | Meaning |
|-------|---------|
| `high` | All terms exactly matched |
| `medium` | Some alias/synonym matching or default metric used |
| `low` | No metrics resolved or significant assumptions |
| `clarification_needed` | Could not identify any metric — check `clarifying_question` |

**Chart types:** `metric` · `bar` · `grouped_bar` · `line` · `table` · `none`

**Errors**
- `422` — question is empty or dataset_id is invalid

---

### `GET /api/questions`

List past questions.

**Query params**
- `dataset_id` — filter by dataset (optional)
- `limit` — 1–200, default 50
- `offset` — default 0

---

### `GET /api/questions/{question_id}`

Get a question with its full answer and provenance.

---

### `POST /api/questions/{question_id}/feedback`

Submit feedback on an answer.

**Request body**
```json
{
  "feedback_type": "wrong",
  "note": "Revenue should exclude cancelled orders"
}
```

`feedback_type` must be one of: `correct` · `partial` · `wrong`

**Response 201**
```json
{
  "id": "...",
  "question_id": "...",
  "feedback_type": "wrong",
  "note": "Revenue should exclude cancelled orders",
  "created_at": "2026-03-19T12:01:00+00:00"
}
```

---

## Error Format

All errors use FastAPI's standard format:

```json
{ "detail": "Dataset '3fa85f64-...' not found." }
```

Validation errors return a list:
```json
{
  "detail": [
    { "loc": ["body", "question"], "msg": "question must not be empty", "type": "value_error" }
  ]
}
```

---

## Environment Variables

See `docs/local-development.md` for the full list and how to configure them.
