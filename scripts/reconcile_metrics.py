#!/usr/bin/env python3
"""Reconcile governed KPIs across warehouse, Cube REST, and Cube SQL (BI path)."""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import jwt
import psycopg2
import psycopg2.extras
import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "metrics" / "metric_registry.yml"
REPORT_DIR = ROOT / "reports"


def _decimal(value) -> Decimal:
    if value is None:
        raise ValueError("Metric value is null")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid metric value: {value!r}") from exc


def load_registry() -> dict:
    with REGISTRY.open() as fh:
        return yaml.safe_load(fh)


def warehouse_values(registry: dict) -> dict[str, Decimal]:
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM marts.metric_snapshot ORDER BY metric_as_of_date DESC LIMIT 1")
            row = cur.fetchone()
            if not row:
                raise RuntimeError("marts.metric_snapshot is empty")
            return {
                name: _decimal(row[cfg["warehouse_column"]])
                for name, cfg in registry["metrics"].items()
            }
    finally:
        conn.close()


def _cube_token() -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "metric-reconciler",
        "role": "admin",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
    }
    return jwt.encode(payload, os.environ["CUBE_API_SECRET"], algorithm="HS256")


def cube_rest_values(registry: dict, retries: int = 20) -> dict[str, Decimal]:
    measures = [cfg["cube_member"] for cfg in registry["metrics"].values()]
    query = {"measures": measures}
    headers = {"Authorization": f"Bearer {_cube_token()}"}
    url = os.environ["CUBE_API_URL"].rstrip("/") + "/cubejs-api/v1/load"

    last_error: Exception | None = None
    for _ in range(retries):
        try:
            response = requests.get(url, params={"query": json.dumps(query)}, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json().get("data") or []
            if not data:
                raise RuntimeError("Cube REST returned no data")
            row = data[0]
            return {
                name: _decimal(row[cfg["cube_member"]])
                for name, cfg in registry["metrics"].items()
            }
        except Exception as exc:  # service may still be warming up
            last_error = exc
            time.sleep(3)
    raise RuntimeError(f"Cube REST did not become ready: {last_error}")


def cube_sql_values(registry: dict, retries: int = 20) -> dict[str, Decimal]:
    aliases = list(registry["metrics"].keys())
    select_list = ", ".join(
        f"MEASURE(metrics.{name}) AS {name}" for name in aliases
    )
    sql = f"SELECT {select_list} FROM metrics"

    last_error: Exception | None = None
    for _ in range(retries):
        try:
            conn = psycopg2.connect(
                host=os.environ["CUBE_SQL_HOST"],
                port=int(os.environ["CUBE_SQL_PORT"]),
                dbname=os.environ.get("CUBE_SQL_DATABASE", "cube"),
                user=os.environ["CUBE_SQL_USER"],
                password=os.environ["CUBE_SQL_PASSWORD"],
                connect_timeout=5,
            )
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(sql)
                    row = cur.fetchone()
                    if not row:
                        raise RuntimeError("Cube SQL API returned no data")
                    return {name: _decimal(row[name]) for name in aliases}
            finally:
                conn.close()
        except Exception as exc:
            last_error = exc
            time.sleep(3)
    raise RuntimeError(f"Cube SQL API did not become ready: {last_error}")


def reconcile() -> list[dict]:
    registry = load_registry()
    warehouse = warehouse_values(registry)
    semantic = cube_rest_values(registry)
    bi_path = cube_sql_values(registry)

    rows: list[dict] = []
    for name, cfg in registry["metrics"].items():
        tolerance = Decimal(str(cfg.get("tolerance", os.environ.get("METRIC_RECONCILIATION_TOLERANCE", "0.01"))))
        w = warehouse[name]
        s = semantic[name]
        b = bi_path[name]
        warehouse_vs_semantic = abs(w - s) <= tolerance
        semantic_vs_bi = abs(s - b) <= tolerance
        rows.append({
            "metric": name,
            "version": cfg["version"],
            "warehouse_value": str(w),
            "semantic_value": str(s),
            "bi_sql_value": str(b),
            "warehouse_vs_semantic": warehouse_vs_semantic,
            "semantic_vs_bi": semantic_vs_bi,
            "status": "PASS" if warehouse_vs_semantic and semantic_vs_bi else "FAIL",
        })
    return rows


def write_report(rows: list[dict]) -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    json_path = REPORT_DIR / "metric_reconciliation.json"
    csv_path = REPORT_DIR / "metric_reconciliation.csv"
    json_path.write_text(json.dumps(rows, indent=2) + "\n")
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = reconcile()
    write_report(rows)
    print("metric | version | warehouse | semantic | bi_sql | status")
    print("-" * 78)
    for row in rows:
        print(
            f"{row['metric']} | {row['version']} | {row['warehouse_value']} | "
            f"{row['semantic_value']} | {row['bi_sql_value']} | {row['status']}"
        )
    return 0 if all(row["status"] == "PASS" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
