# Architecture

```text
CSV seed sources
      |
      v
PostgreSQL raw schemas
      |
      v
     dbt
  staging views
      |
      v
Dimensional marts
  fct_orders      dim_customers
  fct_invoices    dim_campaigns
      |
      +----> marts.metric_snapshot
                    |
                    v
               Cube semantic layer
               REST + SQL APIs
                    |
                    v
                 Metabase
```

Dagster orchestrates the dbt warehouse build and the metric reconciliation check.
The reconciliation asset fails if a governed KPI differs between the warehouse,
Cube REST API, and Cube SQL API used by BI.
