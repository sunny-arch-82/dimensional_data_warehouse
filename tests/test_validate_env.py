# Feature: governed analytics platform, startup environment variable validation
"""Property-based tests for scripts/validate_env.py.

Validates required runtime configuration
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Import the module under test without executing __main__
# ---------------------------------------------------------------------------
_SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "validate_env.py"
_spec = importlib.util.spec_from_file_location("validate_env", _SCRIPT_PATH)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

REQUIRED_VARS: list[str] = list(_mod.REQUIRED_VARS)
validate = _mod.validate
main = _mod.main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_with_env(present: set[str]) -> tuple[int, str]:
    """Run validate_env.main() with only *present* vars set, capturing stdout."""
    import io
    from contextlib import redirect_stdout

    env_backup = {name: os.environ.pop(name, None) for name in REQUIRED_VARS}
    for name in present:
        os.environ[name] = "dummy_value"

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exit_code = main()
    finally:
        # Restore original environment
        for name, original in env_backup.items():
            if original is not None:
                os.environ[name] = original
            else:
                os.environ.pop(name, None)

    return exit_code, buf.getvalue()


# ---------------------------------------------------------------------------
# Property 15 — Startup environment variable validation
# ---------------------------------------------------------------------------

@given(missing=st.sets(st.sampled_from(REQUIRED_VARS), min_size=1))
@settings(max_examples=100)
def test_missing_vars_exit_1_and_names_in_output(missing: set[str]):
    """For any non-empty subset of missing required vars, exit code must be 1
    and every missing variable name must appear in stdout.

    **Validates required runtime configuration**
    """
    present = set(REQUIRED_VARS) - missing
    exit_code, output = _run_with_env(present)

    assert exit_code == 1, (
        f"Expected exit code 1 when vars {missing} are missing, got {exit_code}"
    )
    for name in missing:
        assert name in output, (
            f"Expected '{name}' to appear in output when it is missing, "
            f"but output was:\n{output}"
        )


def test_all_vars_present_exit_0():
    """When all required variables are present, exit code must be 0.

    **Validates required runtime configuration**
    """
    exit_code, output = _run_with_env(set(REQUIRED_VARS))
    assert exit_code == 0, (
        f"Expected exit code 0 when all vars are present, got {exit_code}.\n"
        f"Output: {output}"
    )
