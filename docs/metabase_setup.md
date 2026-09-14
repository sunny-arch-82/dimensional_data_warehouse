# Metabase connection to the governed semantic layer

Open `http://localhost:3001` and complete Metabase's first-run administrator setup.
When asked to add a database, select **PostgreSQL** and use the Cube SQL API:

- Host: `cube`
- Port: `15432`
- Database: `cube`
- Username: value of `CUBE_SQL_USER` (default `analytics_bi`)
- Password: value of `CUBE_SQL_PASSWORD`
- SSL: off for this local-only stack

Cube's SQL API is PostgreSQL-protocol compatible, so Metabase can consume the
semantic model without directly implementing KPI formulas.

## KPI card SQL

Create a native SQL question in Metabase:

```sql
SELECT
  MEASURE(metrics.gross_revenue) AS gross_revenue,
  MEASURE(metrics.net_revenue) AS net_revenue,
  MEASURE(metrics.active_customers) AS active_customers,
  MEASURE(metrics.average_order_value) AS average_order_value,
  MEASURE(metrics.refund_rate) AS refund_rate
FROM metrics;
```

Use the result for KPI cards. For exploration, the `orders` and `customers` Cube
models are available through the same connection.
