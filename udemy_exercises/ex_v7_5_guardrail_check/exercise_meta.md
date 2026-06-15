# EX7.3 — A tool-access guardrail

**Implements:** EX7.3 (source V7.5)

## Learning objective
Apply an allow/block rule to a tool call before it executes.

## Problem statement
Write `guardrail_check(tool_name, allow=None, block=None)` returning `(allowed, reason)`. Precedence: if `block` is given and `tool_name` is in it, deny (reason mentions `denylist`). Else if `allow` is given and `tool_name` is NOT in it, deny (reason mentions `allowlist`). Otherwise allow with reason `'allowed'`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Check the denylist first so a blocked tool is denied even if it's also allowlisted.
2. An allowlist denies anything not on it; if no `allow` is given, don't enforce it.

## Solution explanation
Guardrails gate tool access before execution. Denylist-beats-allowlist precedence means an explicitly dangerous tool stays blocked regardless of other rules — the safe default.
