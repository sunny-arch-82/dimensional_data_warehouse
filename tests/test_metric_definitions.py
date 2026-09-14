from __future__ import annotations

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_orders():
    path = ROOT / "dbt_project" / "seeds" / "marketing" / "orders.csv"
    with path.open() as fh:
        return list(csv.DictReader(fh))


def test_metric_registry_has_versions_and_unique_cube_members():
    registry = yaml.safe_load((ROOT / "metrics" / "metric_registry.yml").read_text())
    metrics = registry["metrics"]
    assert metrics
    assert len({m["cube_member"] for m in metrics.values()}) == len(metrics)
    for name, metric in metrics.items():
        assert metric["version"].startswith("v"), name
        assert metric["status"] == "active", name
        assert metric["warehouse_column"] == name
        assert metric["bi_label"]
        assert metric["description"]


def test_seed_fixture_matches_governed_kpi_contract():
    orders = load_orders()
    transacted = [r for r in orders if r["status"] in {"completed", "refunded"}]
    completed = [r for r in orders if r["status"] == "completed"]
    refunded = [r for r in orders if r["status"] == "refunded"]

    gross = money(sum(Decimal(r["revenue_usd"]) for r in transacted))
    net = money(sum(Decimal(r["revenue_usd"]) for r in completed))
    active = len({r["customer_id"] for r in transacted})
    aov = money(gross / Decimal(len(transacted)))
    refund_rate = money(Decimal(100) * Decimal(len(refunded)) / Decimal(len(transacted)))

    assert gross == Decimal("1576.50")
    assert net == Decimal("1531.50")
    assert active == 5
    assert aov == Decimal("175.17")
    assert refund_rate == Decimal("11.11")
