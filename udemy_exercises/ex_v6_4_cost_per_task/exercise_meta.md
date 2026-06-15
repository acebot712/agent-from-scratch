# EX6.3 — Cost per task

**Implements:** EX6.3 (source V6.4)

## Learning objective
Compute the average cost in dollars across all traces.

## Problem statement
Write `cost_per_task(traces)` returning the mean of the `cost_usd` field across all traces, as a float. Return `0.0` for an empty list.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Sum `cost_usd` over all traces, then divide by the count.
2. Use `t.get('cost_usd', 0.0)` so a trace missing the field counts as zero rather than raising.

## Solution explanation
Cost per task is averaged over every run, success or not — you pay for failures too. Defaulting a missing cost to zero keeps the metric robust to incomplete traces.
