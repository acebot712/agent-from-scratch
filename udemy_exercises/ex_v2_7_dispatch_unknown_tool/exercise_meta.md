# EX2.3 — Dispatch with graceful failure

**Implements:** EX2.3 (source V2.5 + V2.7)

## Learning objective
Dispatch a parsed call and handle unknown tools and bad args gracefully.

## Problem statement
Write `dispatch(registry, name, args)` where `registry` is a dict of `name -> callable`. Return `{'ok': True, 'output': <result>}` on success. For an unknown tool return `{'ok': False, 'error': <message containing 'unknown'>}`. If the call raises `TypeError` (wrong/missing args) return `{'ok': False, 'error': <message containing 'bad arguments'>}`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Check membership before calling; an unknown name should never reach the function.
2. Wrap the `fn(**args)` call in try/except TypeError to catch wrong/missing keyword arguments.

## Solution explanation
Models hallucinate tool names and emit wrong arguments. Dispatch converts both failure modes into a structured error dict the loop can feed back to the model, instead of crashing the agent.
