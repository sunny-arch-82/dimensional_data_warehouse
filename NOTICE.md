# Attribution and modifications

This project is based on the **Self-Serve Analytics Platform** project described in
Abhishek Singh's `project_OmniFlow` portfolio and is distributed under the MIT
License. The upstream license notice is preserved in `LICENSE`.

This portfolio version extends the supplied project scaffold with a runnable
PostgreSQL dimensional warehouse, dbt staging and mart models, a governed KPI
registry with metric versions, a Cube semantic model, Dagster orchestration,
and automated metric reconciliation across the warehouse, Cube REST semantic
API, and the Cube SQL API used by BI tools such as Metabase.

The sample seed data supplied with the original project is retained for local
demonstration and testing.
