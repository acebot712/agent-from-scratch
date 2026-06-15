# EX5.2 — Cap delegation depth

**Implements:** EX5.2 (source V5.4)

## Learning objective
Enforce a delegation-depth cap to prevent runaway agent loops.

## Problem statement
Implement `DelegationError(RuntimeError)` and a `DelegationCap` class constructed with `max_depth` (and optional `depth=0`). `enter()` returns a NEW `DelegationCap` one level deeper, but raises `DelegationError` if the current depth is already at `max_depth`. `allows()` returns whether another level is permitted.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. `enter` should return a fresh `DelegationCap` with `depth + 1`, not mutate `self` — that makes each delegation branch independent.
2. Raise `DelegationError` when `depth >= max_depth` before descending.

## Solution explanation
Multi-agent systems can recurse forever (A delegates to B delegates to A...). A depth cap that raises on the (max+1)th `enter` is the simplest reliable brake.
