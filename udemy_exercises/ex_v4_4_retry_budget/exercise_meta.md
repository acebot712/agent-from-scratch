# EX4.2 — A retry budget

**Implements:** EX4.2 (source V4.4)

## Learning objective
Implement the bounded retry counter at the core of a reflection loop.

## Problem statement
Implement a `RetryBudget` class constructed with `max_retries`. Provide `can_retry() -> bool` (True while fewer than `max_retries` have been used), `consume() -> bool` (use one retry; return True if one was available, else False), and a `remaining` property.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Track a `used` counter; `can_retry` compares it to `max_retries`.
2. `consume` should refuse (return False) once the budget is exhausted, without incrementing past the cap.

## Solution explanation
Reflection means critique-and-retry, but only within a budget — otherwise a model that can't fix its output loops forever. This counter is the deterministic core the rest of the reflection loop is built on.
