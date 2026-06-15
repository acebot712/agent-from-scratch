# EX1.2 — Parse the model's intent

**Implements:** EX1.2 (source V1.3)

## Learning objective
Extract a structured action or final answer from a free-text response.

## Problem statement
Write `parse_intent(text)` returning a dict: if `text` contains `FINAL ANSWER:` return `{'kind': 'final', 'value': <text after the marker, stripped>}`; else if it matches `ACTION: name(args)` return `{'kind': 'action', 'name': name, 'args_text': args}`; otherwise `{'kind': 'unknown'}`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Check for the `FINAL ANSWER:` marker first; `str.split(marker, 1)[1]` gives you everything after it.
2. For actions use a regex like `ACTION:\s*(\w+)\((.*)\)` and read groups 1 and 2.

## Solution explanation
Intent parsing turns free text into a decision the loop can act on. We check the terminal marker first (so a response that both reasons and concludes is treated as final), then fall back to an `ACTION:` regex, then to `unknown`.
