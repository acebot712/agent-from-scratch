# EX7.1 — Enforce cost and step caps

**Implements:** EX7.1 (source V7.2)

## Learning objective
Enforce a max-step and max-cost cap that halts the loop.

## Problem statement
Write `enforce_caps(steps, cost, max_steps=None, max_cost=None)` returning a halt-reason string if a cap is exceeded, else `None`. Check steps first: if `max_steps` is set and `steps >= max_steps`, return a message containing `max_steps`; then if `max_cost` is set and `cost >= max_cost`, return a message containing `max_cost`. An unset cap (None) is never enforced.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Guard each cap with an `is not None` check so an unset cap is ignored.
2. Use `>=` so the loop halts exactly at the cap, and check steps before cost.

## Solution explanation
Caps are the difference between a bug and a bill. A pure function that returns the halt reason (or None) is trivial to call once per loop iteration and trivial to test.
