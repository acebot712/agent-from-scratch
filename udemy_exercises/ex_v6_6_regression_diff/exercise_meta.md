# EX6.5 — Detect regressions between runs

**Implements:** EX6.5 (source V6.6)

## Learning objective
Diff two eval runs to find tasks that regressed and tasks that got fixed.

## Problem statement
Write `regression_diff(before, after)`. Match traces by `task_id`. Return `{'regressions': [...], 'fixes': [...]}` where regressions are task ids that were successful in `before` but not in `after`, and fixes are the reverse. Both lists sorted; only consider task ids present in both runs.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Build a `task_id -> success` dict for each run; the intersection of their keys is the comparable set.
2. A regression is `before True and after False`; a fix is the mirror image.

## Solution explanation
When you tweak a prompt, aggregate success rate can hide that you fixed two tasks and broke two others. Diffing per task surfaces exactly which ids moved, which is what catches silent regressions.
