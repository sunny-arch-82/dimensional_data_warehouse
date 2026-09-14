"""Dagster orchestration for the governed analytics warehouse."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dagster import AssetExecutionContext, Definitions, ScheduleDefinition, asset, define_asset_job

ROOT = Path("/opt/dagster/app")
DBT_PROJECT = ROOT / "dbt_project"


def run(command: list[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    result.check_returncode()
    return result.stdout


@asset(group_name="warehouse", description="Seed source data and build tested dimensional dbt models.")
def dimensional_warehouse(context: AssetExecutionContext):
    run(["dbt", "seed", "--profiles-dir", ".", "--full-refresh"], DBT_PROJECT)
    output = run(["dbt", "build", "--profiles-dir", "."], DBT_PROJECT)
    context.add_output_metadata({"dbt_project": "governed_analytics", "status": "built"})
    return output


@asset(
    deps=[dimensional_warehouse],
    group_name="governance",
    description="Verify governed KPI values across PostgreSQL, Cube REST, and the Cube SQL BI path.",
)
def metric_reconciliation(context: AssetExecutionContext):
    output = run(["python", "scripts/reconcile_metrics.py"])
    context.add_output_metadata({"report": "reports/metric_reconciliation.csv"})
    return output


governed_analytics_job = define_asset_job(
    "governed_analytics_job",
    selection=[dimensional_warehouse, metric_reconciliation],
)

four_hour_schedule = ScheduleDefinition(
    job=governed_analytics_job,
    cron_schedule="0 */4 * * *",
)

defs = Definitions(
    assets=[dimensional_warehouse, metric_reconciliation],
    jobs=[governed_analytics_job],
    schedules=[four_hour_schedule],
)
