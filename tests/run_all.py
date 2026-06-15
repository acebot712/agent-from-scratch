"""Tiny zero-dependency test runner.

Runs every ``test_*`` function in every ``test_*.py`` module in this directory.
Use this when pytest isn't installed:  ``python tests/run_all.py``
(pytest also works:  ``pytest tests/`` — same test functions.)

Tests whose names contain ``live`` are skipped unless RUN_LIVE=1, since those
hit a real LLM and need LLM_API_KEY.
"""
import importlib
import os
import sys
import traceback

HERE = os.path.dirname(__file__)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))


def main() -> int:
    run_live = os.environ.get("RUN_LIVE") == "1"
    files = sorted(f for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py"))
    passed = failed = skipped = 0
    for f in files:
        mod = importlib.import_module(f[:-3])
        for name in dir(mod):
            if not name.startswith("test_"):
                continue
            if "live" in name and not run_live:
                skipped += 1
                continue
            try:
                getattr(mod, name)()
                passed += 1
                print(f"PASS {f}::{name}")
            except Exception:  # noqa: BLE001
                failed += 1
                print(f"FAIL {f}::{name}")
                traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped (set RUN_LIVE=1 to run live tests)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
