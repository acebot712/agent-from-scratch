# EX1.1 — Normalise an LLM response

**Implements:** EX1.1 (source V1.2)

## Learning objective
Normalise a raw OpenAI-style response dict into one standard shape.

## Problem statement
Different providers return different JSON. Write `normalize_llm_response(raw)` that maps an OpenAI-style raw dict to a normalised dict with keys `text` (str, '' if null), `tool_calls` (list of `{'name', 'args'}` with `args` parsed from the JSON `arguments` string), and `stop_reason` (the `finish_reason`).

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. The raw shape is `raw['choices'][0]['message']` for content/tool_calls and `raw['choices'][0]['finish_reason']` for the stop reason.
2. Tool-call `arguments` arrives as a JSON *string* — `json.loads` it into a dict.

## Solution explanation
We dig into the first choice, coerce a missing/None `content` to `''`, and parse each tool call's `arguments` JSON string into a real dict. Normalising here means the rest of the agent never has to know which provider produced the response.
