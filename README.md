# Dimensional Data Warehouse with Governed Metrics & Self-Service BI

A local analytics engineering project that builds a dimensional PostgreSQL
warehouse with dbt, orchestrates it with Dagster, exposes versioned KPIs through
Cube, and serves those governed metrics to Metabase through Cube's SQL API.

The differentiating feature is **metric reconciliation**: revenue, active-customer,
AOV, and refund KPIs are checked across the warehouse, semantic API, and BI SQL
path so dashboards cannot silently drift from the governed definition.

## Architecture

```text
Sample source data
      |
      v
PostgreSQL
      |
      v
Dagster -> dbt staging -> dimensional marts
                           |
                           v
                    governed KPI snapshot
                           |
                           v
                         Cube
                     REST + SQL API
                           |
                           v
                        Metabase
```

## Stack

- PostgreSQL 15 — warehouse
- dbt Core + dbt-postgres — transformations and tests
- Dagster — orchestration and scheduled reconciliation
- Cube — governed semantic layer and PostgreSQL-compatible SQL API
- Metabase — self-service BI
- Docker Compose — local runtime

## Dimensional models

| Model | Grain |
|---|---|
| `marts.fct_orders` | one row per order |
| `marts.dim_customers` | one row per customer |
| `marts.fct_invoices` | one row per invoice |
| `marts.dim_campaigns` | one row per campaign |
| `marts.daily_order_metrics` | one row per order date |
| `marts.metric_snapshot` | one governed KPI snapshot |

## Governed KPIs

The registry is in `metrics/metric_registry.yml` and includes a version, owner,
definition, warehouse column, Cube member, BI label, unit, and reconciliation
tolerance for every metric.

Current v1 metrics:

- `gross_revenue`
- `net_revenue`
- `active_customers`
- `average_order_value`
- `refund_rate`

With the included seed data the expected values are:

| Metric | Value |
|---|---:|
| Gross revenue | 1576.50 |
| Net revenue | 1531.50 |
| Active customers | 5 |
| Average order value | 175.17 |
| Refund rate | 11.11% |

## Quick start

```bash
cp .env.example .env
make setup
make status
```

Services:

| Service | URL |
|---|---|
| Dagster | http://localhost:3000 |
| Cube API / Playground | http://localhost:4000 |
| Metabase | http://localhost:3001 |
| Cube SQL API | localhost:15432 |
| PostgreSQL | localhost:5432 |

`make setup` starts PostgreSQL, builds/seeds/tests the dbt warehouse, then starts
Cube and Metabase.

## Reconcile the governed metrics

After Cube has finished starting:

```bash
make reconcile
```

The output looks like:

```text
metric | version | warehouse | semantic | bi_sql | status
------------------------------------------------------------------------------
gross_revenue | v1 | 1576.50 | 1576.50 | 1576.50 | PASS
...
```

The three compared paths are:

```text
PostgreSQL warehouse value
          =
Cube REST semantic metric
          =
Cube SQL metric consumed by Metabase
```

A mismatch exits non-zero and writes a report under `reports/`.

## Dagster

The asset graph contains:

```text
dimensional_warehouse
          |
          v
metric_reconciliation
```

The included schedule runs the governed analytics job every four hours.

## Metabase

Complete Metabase's first-run setup, then connect it to the **Cube SQL API**, not
directly to the warehouse. Exact settings and a KPI query are in
[`docs/metabase_setup.md`](docs/metabase_setup.md).

## Useful commands

```bash
make setup       # first-time setup + initial dbt build
make run         # start all containers
make build       # dbt build
make reconcile   # warehouse = semantic = BI-path check
make test        # dbt tests + Python tests
make status      # container status
make logs        # recent logs
make teardown    # stop services, preserve volumes
make clean       # stop and delete local volumes
```

## Repository hygiene

`.env`, dbt build artifacts, virtual environments, local databases, runtime logs,
and generated reconciliation reports are excluded from Git. `.env.example`
contains local demonstration values only and should be changed for any non-local
deployment.

## Scope

This is a local portfolio implementation. The included source data is deliberately
small, Metabase's first administrator is configured through its normal setup
wizard, and the project does not claim enterprise RBAC or large-scale performance
benchmarking.


