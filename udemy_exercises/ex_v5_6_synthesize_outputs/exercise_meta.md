# EX5.3 — Synthesise worker outputs

**Implements:** EX5.3 (source V5.6)

## Learning objective
Mechanically merge multiple worker outputs into one structured result.

## Problem statement
Write `synthesize_outputs(outputs, dedupe=True)`. Strip each output, drop blanks, and (when `dedupe`) remove duplicates while preserving first-seen order. Return `{'parts': [...], 'combined': '<newline-joined parts>', 'count': <len(parts)>}`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Track a `seen` set for dedupe, but still append to a list so order is preserved.
2. Strip each output before the blank check so whitespace-only strings are dropped.

## Solution explanation
This is the mechanical (graded) synthesis: deterministic combine/dedupe/order. It contrasts with an LLM writing a fused summary — useful, but not reproducible enough to autograde.
