# Example: Retail Sales Analytics

This example demonstrates MetricAnchor with a retail order dataset.

## Dataset

`sample_data/retail_sales.csv`

| Column | Type | Description |
|---|---|---|
| order_id | string | Unique order identifier |
| order_date | date | Date the order was placed |
| customer_id | string | Unique customer identifier |
| product_category | string | Product category (Electronics, Apparel, Home, Beauty, Sports) |
| product_name | string | Product name |
| quantity | integer | Units ordered |
| unit_price | float | Price per unit |
| order_total | float | Total order value |
| status | string | completed, cancelled, returned, pending |
| region | string | North, South, East, West |

## Sample Questions

1. "What was revenue by product category last quarter?"
2. "Which region has the highest average order value?"
3. "How many completed orders did we have each month this year?"
4. "What is the refund rate by category?"
5. "Show me the top 5 customers by total revenue."

## Semantic Model

See `semantic_model.yml` for the full definition. Key concepts:
- **revenue** = SUM(order_total) where status = 'completed'
- **aov** = revenue / order count (excludes cancelled/returned)
- **units_sold** = SUM(quantity) for completed orders

## Validate

```bash
metricanchor validate examples/retail_sales/semantic_model.yml
```
