# Governed metric contract

The project intentionally keeps business KPI definitions explicit and versioned.
`metrics/metric_registry.yml` is the human-readable contract; dbt materializes the
values in `marts.metric_snapshot`; Cube exposes the same values through REST and
SQL APIs; Metabase connects to Cube's SQL API instead of redefining the formulas.

## v1 metrics

| Metric | Definition | Unit |
|---|---|---|
| gross_revenue | Completed + refunded transaction revenue before refund subtraction | USD |
| net_revenue | Completed-order revenue only | USD |
| active_customers | Distinct customers with completed or refunded transactions | count |
| average_order_value | Gross revenue / completed-or-refunded transaction count | USD |
| refund_rate | Refunded transactions / completed-or-refunded transactions × 100 | percent |

## Reconciliation

Run:

```bash
make reconcile
```

The check reads each KPI from three access paths:

1. PostgreSQL `marts.metric_snapshot` (warehouse source of truth)
2. Cube REST API (semantic layer)
3. Cube SQL API (the same governed interface used by BI tools such as Metabase)

A metric passes only when all values agree within its registry tolerance. Runtime
results are written to `reports/metric_reconciliation.csv` and `.json`.

Changing a metric requires incrementing its version in the registry and updating
the dbt model and Cube mapping in the same pull request.
