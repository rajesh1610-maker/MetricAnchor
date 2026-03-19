# Semantic Model Reference

A **semantic model** is a YAML file that describes what your data means in plain business language. MetricAnchor uses it to translate natural-language questions into correct, consistent SQL — and to show users exactly which definitions were applied to every answer.

---

## File structure

```yaml
name: retail_sales          # unique identifier (snake_case)
dataset: retail_sales       # must match the uploaded dataset name
description: "..."          # plain-English summary shown in the UI
grain: "one row = one order"
time_column: order_date     # primary date field for time-based queries

metrics: [...]
dimensions: [...]
entities: [...]
synonyms: [...]
business_rules: [...]
caveats: [...]
exclusions: [...]
```

---

## metrics

Metrics are the numbers your business cares about — revenue, signups, tickets resolved. Each metric maps a business term to a SQL aggregate expression.

```yaml
metrics:
  - name: revenue
    description: "Total completed order value"
    expression: "SUM(order_total)"
    format: currency          # number | currency | percent | duration
    unit: USD                 # optional
    default_aggregation: sum  # sum | count | avg | min | max
    aliases:
      - sales
      - total revenue
    filters:
      - column: status
        operator: "="
        value: "completed"
```

**Required fields:** `name`, `expression`

**filters** are injected as `WHERE` clauses whenever this metric is queried. Use them to enforce business definitions at the metric level (e.g., "revenue only counts completed orders").

---

## dimensions

Dimensions are the attributes you group or filter by — category, region, date, plan tier.

```yaml
dimensions:
  - name: product_category
    column: product_category      # actual column name in the table
    description: "Product grouping"
    is_date: false                # true → the AI treats this as a time dimension
    aliases:
      - category
      - product type
    values:                       # optional: known values for validation and prompt hints
      - Electronics
      - Apparel
      - Home
```

**Required fields:** `name`, `column`

---

## entities

Entities are the primary keys or foreign keys that identify objects in your data.

```yaml
entities:
  - name: account
    column: account_id
    description: "Unique user account"
    aliases:
      - user
      - customer
```

---

## synonyms

Synonyms map business phrases to specific metrics, dimensions, or entities so the AI resolves ambiguous language consistently.

```yaml
synonyms:
  - phrase: "sales"
    maps_to: "metric:revenue"
  - phrase: "cohort"
    maps_to: "dimension:signup_date"
  - phrase: "customer"
    maps_to: "entity:account"
```

**maps_to format:** `metric:<name>` | `dimension:<name>` | `entity:<name>`

The resolver uses exact and fuzzy matching against these phrases when parsing a user question.

---

## business_rules

Business rules are always-on filters that the AI applies automatically, unless the user explicitly asks for something different.

```yaml
business_rules:
  - name: active_accounts_only
    description: "Exclude churned accounts from all revenue metrics"
    filter: "churned = false"
    applies_to:
      - metric:mrr
      - metric:paid_accounts
```

If `applies_to` is omitted, the rule applies to all queries on this dataset.

---

## caveats

Caveats are plain-English warnings surfaced alongside every AI answer that uses this model. Use them to prevent misinterpretation.

```yaml
caveats:
  - "Refunds are not deducted from revenue."
  - "Data refreshes daily at 6am UTC. Same-day data may be incomplete."
```

---

## exclusions

Exclusions describe data that is intentionally absent from the dataset.

```yaml
exclusions:
  - description: "Test accounts are excluded"
    filter: "account_id NOT LIKE 'test-%'"
```

---

## Validation rules

MetricAnchor validates every model before saving:

| Rule | Error |
|------|-------|
| At least one metric | `metrics` array must have ≥ 1 item |
| Unique names | No two metrics, dimensions, or entities may share a name |
| Safe metric names | Names must be `[a-z][a-z0-9_]*` — no spaces or special chars |
| Synonym targets exist | `maps_to` must point to a defined metric, dimension, or entity |

Warnings (non-blocking):

- Metrics without `description`
- Metrics without `aliases`
- Dimensions without `description`

---

## Using the wizard vs. YAML editor

| | Wizard | YAML editor |
|---|---|---|
| Best for | First-time users, business stakeholders | Analytics engineers, power users |
| How | 5-step guided form | Direct text editing with inline validation |
| Output | Same YAML stored in the database | Same YAML stored in the database |
| Access | `/semantic-models/new` (default) | Toggle to "YAML editor" on the same page |

---

## Examples

Three fully worked examples are included in the `examples/` directory:

- `examples/retail_sales/semantic_model.yml` — e-commerce orders with revenue, AOV, units sold
- `examples/support_tickets/semantic_model.yml` — help desk with resolution time, CSAT, backlog
- `examples/saas_funnel/semantic_model.yml` — product funnel with MRR, trial conversion, churn

To load an example via the API:

```bash
curl -X POST http://localhost:8000/api/semantic_models \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "dataset_id": "your-dataset-id",
  "name": "retail_sales",
  "definition": $(python3 -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(open('examples/retail_sales/semantic_model.yml'))))")
}
EOF
```

---

## REST API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/semantic_models` | List all models (filter by `?dataset_id=`) |
| `POST` | `/api/semantic_models` | Create a model |
| `GET` | `/api/semantic_models/{id}` | Get model by ID |
| `PUT` | `/api/semantic_models/{id}` | Update model definition |
| `DELETE` | `/api/semantic_models/{id}` | Delete model |
| `POST` | `/api/semantic_models/validate` | Validate a definition without saving |
| `GET` | `/api/semantic_models/{id}/export` | Export as YAML text |
