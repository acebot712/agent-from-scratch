# EX3.3 — Trim history to a token budget

**Implements:** EX3.3 (source V3.2)

## Learning objective
Trim a message history to fit a token budget, keeping the most recent turns.

## Problem statement
Using the provided `count_tokens` proxy (word count), write `context_budget_trim(messages, budget)`. Keep a leading `system` message if present, then keep the most recent messages whose combined token count fits within `budget`. Return the kept messages in original order. Return `[]` if `budget <= 0`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Pop the system message aside first, then iterate the rest in reverse so you add the newest messages until the budget runs out.
2. Accumulate kept messages while a running `remaining` counter stays >= each message's cost; reverse them back at the end to restore order.

## Solution explanation
The context window is a budget. We protect the system instruction, then greedily keep the freshest turns that fit — older context is the first to go, which is usually what you want.
