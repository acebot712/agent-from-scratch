# EX6.4 — Classify a failure

**Implements:** EX6.4 (source V6.5)

## Learning objective
Classify a failed run into a failure category from its trace, rule-based.

## Problem statement
Write `classify_failure(trace)`. If the run succeeded (`success` truthy) return `None`. Otherwise classify in this order: `'max_steps_hit'` if `stop_reason == 'max_steps'` or `steps >= max_steps`; `'tool_error'` if `tool_errors > 0` or `stop_reason == 'error'`; `'no_final_answer'` if `final_answer` is missing/empty; else `'wrong_answer'`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Return `None` for successes first, so the rest of the function only deals with failures.
2. Order matters: check the step cap, then tool errors, then a missing answer, then fall through to 'wrong_answer'.

## Solution explanation
A rule-based taxonomy turns a pile of failing traces into actionable buckets (ran out of steps vs tool broke vs never answered) — deterministic and autogradeable, unlike an LLM judge.
