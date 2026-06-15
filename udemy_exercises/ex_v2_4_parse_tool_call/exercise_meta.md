# EX2.1 — Parse a tool call

**Implements:** EX2.1 (source V2.4)

## Learning objective
Parse a hand-rolled tool request into a structured {name, args} object.

## Problem statement
Write `parse_tool_call(text)`. A tool request looks like two lines:

    TOOL: <name>
    ARGS: {"json": "object"}

Return `{'name': name, 'args': <parsed dict>}`. If there is no `ARGS:` line, use `{}`. If the args JSON is malformed, use `{}`. Return `None` when there is no `TOOL:` line at all.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Search for the `TOOL:` name first; return `None` immediately if it's absent.
2. Wrap `json.loads` in try/except so malformed args fall back to `{}` instead of raising.

## Solution explanation
This is native function calling, done by hand. We extract the tool name with one regex and the JSON args with another, parsing defensively so a model that emits broken JSON gives us an empty-args call rather than a crash.
