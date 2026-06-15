# EX7.2 — Format a structured log record

**Implements:** EX7.2 (source V7.4)

## Learning objective
Emit one flat, structured log record per agent step.

## Problem statement
Write `format_log_record(step, action, cost=0.0, cumulative=0.0)` returning a flat dict with exactly these keys: `step`, `action`, `cost_usd` (rounded to 6 places), `cumulative_cost_usd` (rounded to 6 places), and `ok` (always `True`).

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Return a literal dict — a stable, flat schema is exactly what a log aggregator wants.
2. `round(value, 6)` keeps the cost fields tidy and comparable.

## Solution explanation
Observability starts with a consistent record per step. A flat dict with a fixed key set serialises cleanly to JSON lines and makes later filtering and metrics straightforward.
