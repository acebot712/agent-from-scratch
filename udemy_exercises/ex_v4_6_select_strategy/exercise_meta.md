# EX4.3 — Select a reasoning strategy

**Implements:** EX4.3 (source V4.6)

## Learning objective
Pick a reasoning strategy from task metadata with rule-based logic.

## Problem statement
Write `select_strategy(meta)` (a dict) returning one of `'react'`, `'reflection'`, `'tot'`, `'direct'`. Rules, in order: if `meta['needs_tools']` -> `'react'`; elif `meta['verifiable']` and `meta['difficulty'] == 'hard'` -> `'reflection'`; elif `meta['open_ended']` or `meta['branching']` -> `'tot'`; else `'direct'`. Missing keys are falsy.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Use `meta.get(key)` so missing keys read as falsy instead of raising `KeyError`.
2. Order matters — check the rules top to bottom and return on the first match.

## Solution explanation
Not every task needs the heaviest reasoning. A cheap rule-based router sends tool tasks to ReAct, hard verifiable tasks to reflection, branching tasks to tree-of-thoughts, and everything else to a single direct call.
