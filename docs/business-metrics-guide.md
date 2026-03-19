# Business Metrics Guide

This guide helps business stakeholders — not just engineers — define metrics clearly so MetricAnchor can answer questions correctly and consistently.

---

## Why definitions matter

When someone asks "what was revenue last month?", the answer depends on several unstated decisions:

- Does "revenue" include refunds? Cancelled orders? Shipping fees?
- Is "last month" calendar month, fiscal month, or rolling 30 days?
- Should test accounts be included?

Without explicit definitions, different people get different numbers for the same question. MetricAnchor makes these decisions visible and consistent by grounding every answer in your semantic model.

---

## Step 1: Name your metrics precisely

A good metric name is:
- **Unambiguous** — "completed_order_revenue" is better than "revenue" when there are multiple revenue types
- **Stable** — avoid names that will change as the business evolves ("q4_revenue")
- **Machine-safe** — lowercase, underscores, no spaces: `avg_resolution_hours` not `Avg Resolution Hours`

Use `aliases` to map the human-friendly names:

```yaml
- name: completed_order_revenue
  aliases:
    - revenue
    - sales
    - net revenue
```

---

## Step 2: Write the SQL expression

The `expression` is a SQL aggregate that will be computed over your dataset. Common patterns:

| Business concept | SQL expression |
|-----------------|----------------|
| Sum of a column | `SUM(order_total)` |
| Count of rows | `COUNT(*)` |
| Count distinct | `COUNT(DISTINCT customer_id)` |
| Average | `AVG(satisfaction_score)` |
| Rate / percentage | `100.0 * COUNT(CASE WHEN converted THEN 1 END) / NULLIF(COUNT(*), 0)` |
| Safe division | `SUM(revenue) / NULLIF(SUM(orders), 0)` |

Use `NULLIF(..., 0)` for any division to avoid divide-by-zero errors.

---

## Step 3: Encode your business rules as filters

Every metric can carry filters that restrict what data it counts. This is where you lock in the business definition.

```yaml
- name: revenue
  expression: "SUM(order_total)"
  filters:
    - column: status
      operator: "="
      value: "completed"
```

**Common filter patterns:**

| Rule | Filter |
|------|--------|
| Only completed orders | `status = 'completed'` |
| Active users only | `is_active = true` |
| Paid accounts only | `plan != 'free'` |
| Exclude test data | `is_test = false` |
| Last 90 days | Use time dimension, not a filter here |

For rules that apply across multiple metrics, use `business_rules` instead of repeating filters:

```yaml
business_rules:
  - name: exclude_internal
    filter: "is_internal = false"
    applies_to:
      - metric:signups
      - metric:revenue
```

---

## Step 4: Define your dimensions

Dimensions are the "group by" and "filter by" columns. Good dimensions:
- Have a clear business meaning
- Have known values (list them in `values:` if finite)
- Are stable — avoid columns that change constantly

```yaml
dimensions:
  - name: plan_tier
    column: plan_tier
    description: "Subscription plan (starter, growth, enterprise)"
    values:
      - starter
      - growth
      - enterprise
    aliases:
      - plan
      - tier
```

---

## Step 5: Add synonyms for natural language

Synonyms let the AI understand business language that doesn't match column names exactly.

**Before synonyms:** User asks "what's the CSAT?" → AI doesn't know what CSAT is.

**After synonyms:**
```yaml
synonyms:
  - phrase: "CSAT"
    maps_to: "metric:csat_score"
  - phrase: "satisfaction"
    maps_to: "metric:csat_score"
```

Good synonyms to add:
- Abbreviations (MRR, AOV, LTV, CAC, NPS, CSAT)
- Informal names ("churn" → `metric:churn_rate`)
- Plural forms if they differ ("tickets" → `metric:ticket_count`)
- Business-unit-specific vocabulary

---

## Step 6: Write caveats for tricky definitions

Caveats are surfaced to users alongside every answer. Use them when:
- The metric has a non-obvious definition ("revenue excludes refunds")
- The data has known gaps ("same-day data is incomplete")
- There's a business context users need ("fiscal year starts in October")

```yaml
caveats:
  - "Revenue reflects gross order value at time of purchase. Refunds are not deducted."
  - "MRR is contracted value, not cash received."
  - "Data updates once daily at 6am UTC."
```

---

## Common mistakes and how to fix them

### Metric returns too-high numbers
**Cause:** Missing filter — you're summing all rows, not just the relevant ones.
**Fix:** Add a filter to the metric definition.

```yaml
# Wrong: sums ALL orders
expression: "SUM(order_total)"

# Right: sums only completed orders
expression: "SUM(order_total)"
filters:
  - column: status
    operator: "="
    value: "completed"
```

### Duplicate counts for the same entity
**Cause:** Joining multiple tables creates fan-out; `COUNT(*)` inflates.
**Fix:** Use `COUNT(DISTINCT entity_id)` instead of `COUNT(*)`.

```yaml
expression: "COUNT(DISTINCT customer_id)"
```

### Division by zero errors
**Cause:** The denominator can be zero for some time periods.
**Fix:** Wrap the denominator in `NULLIF(..., 0)`.

```yaml
expression: "SUM(revenue) / NULLIF(COUNT(DISTINCT orders), 0)"
```

### The same metric has two names in the business
**Cause:** Different teams use different terms.
**Fix:** Pick one canonical name, add the rest as aliases.

```yaml
- name: monthly_recurring_revenue
  aliases:
    - MRR
    - monthly revenue
    - recurring revenue
```

---

## Checklist before publishing a semantic model

- [ ] Every metric has a `description` explaining what it measures and what it excludes
- [ ] Every metric that should be filtered has the right `filters`
- [ ] Ambiguous terms (abbreviations, brand terms) have `synonyms`
- [ ] Known data caveats are in the `caveats` list
- [ ] Dimension `values` are listed for low-cardinality columns
- [ ] The model has been validated using `/api/semantic_models/validate`
- [ ] A teammate who wasn't involved in building it has reviewed the definitions

---

## Template

Use this as a starting point when building a new model from scratch:

```yaml
name: your_model_name
dataset: your_dataset
description: "What this data represents and who uses it."
grain: "one row = one ___"
time_column: your_date_column

metrics:
  - name: primary_metric
    description: "What exactly this counts/sums, and what it excludes."
    expression: "SUM(your_column)"
    format: number   # number | currency | percent | duration
    aliases:
      - common name
      - abbreviation

dimensions:
  - name: primary_dimension
    column: column_name
    description: "What this groups by."
    aliases:
      - common name

synonyms:
  - phrase: "informal name"
    maps_to: "metric:primary_metric"

caveats:
  - "Known limitation or non-obvious definition."
```
