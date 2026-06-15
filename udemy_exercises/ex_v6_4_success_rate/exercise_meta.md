# EX6.1 — Success rate

**Implements:** EX6.1 (source V6.4)

## Learning objective
Compute the fraction of traces that succeeded.

## Problem statement
Write `success_rate(traces)` returning the fraction of traces whose `success` field is truthy, as a float. Return `0.0` for an empty list.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Count truthy `success` fields with a generator expression.
2. Guard the empty list before dividing to avoid `ZeroDivisionError`.

## Solution explanation
Success rate is the headline eval metric. The only edge case is the empty set, which we define as 0.0 rather than letting the division blow up.
