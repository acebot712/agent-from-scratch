# EX1.3 — The stopping condition

**Implements:** EX1.3 (source V1.4)

## Learning objective
Implement a terminal-state check that ends the agent loop correctly.

## Problem statement
Write `should_stop(text, step, max_steps)` returning `True` when the loop should end: either `step >= max_steps` (safety cap) OR `text` contains `FINAL ANSWER:`. Otherwise `False`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Two independent reasons to stop — combine them with `or` (or two `if` returns).
2. Use `>=` for the step cap so the loop can never run past `max_steps`.

## Solution explanation
A loop without a correct terminal check either stops too early or never stops. We stop on the explicit completion marker, and always stop at the step cap as a safety net against a model that never signals done.
