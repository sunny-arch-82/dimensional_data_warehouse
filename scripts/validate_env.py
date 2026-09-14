#!/usr/bin/env python3
"""Validate runtime configuration used by Dagster, dbt, Cube, and reconciliation."""

import os
import sys

REQUIRED_VARS = [
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "DAGSTER_HOME",
    "DBT_PROFILES_DIR",
    "CUBE_API_SECRET",
    "CUBE_API_URL",
    "CUBE_SQL_HOST",
    "CUBE_SQL_PORT",
    "CUBE_SQL_DATABASE",
    "CUBE_SQL_USER",
    "CUBE_SQL_PASSWORD",
]


def validate() -> list[str]:
    return [name for name in REQUIRED_VARS if not os.environ.get(name)]


def main(argv: list[str] | None = None) -> int:
    missing = validate()
    if missing:
        for name in missing:
            print(f"ERROR: Missing required environment variable '{name}'")
        return 1

    if argv:
        import subprocess
        return subprocess.run(argv, check=False).returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
