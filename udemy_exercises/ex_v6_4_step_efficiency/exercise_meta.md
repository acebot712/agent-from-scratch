# EX6.2 — Step efficiency

**Implements:** EX6.2 (source V6.4)

## Learning objective
Compute the average number of steps taken by successful traces.

## Problem statement
Write `step_efficiency(traces)` returning the mean `steps` over the **successful** traces only (lower is better). Return `0.0` if there are no successful traces.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Filter to successful traces first; a failed run's step count would skew the measure.
2. Average `steps` over that filtered list, guarding the empty case.

## Solution explanation
Counting steps only on successes answers 'when it works, how efficiently?' — averaging in failures (which often hit the step cap) would muddy that signal.
