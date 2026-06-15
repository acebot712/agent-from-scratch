# EX3.4 — Serialise episodic memory

**Implements:** EX3.4 (source V3.6)

## Learning objective
Serialise and reload a list of episodes so memory survives across sessions.

## Problem statement
Write `serialize_episodes(episodes)` returning a JSON string, and `deserialize_episodes(blob)` returning the list back. An episode is a dict like `{'role': ..., 'content': ..., 'meta': {...}}`. The round-trip must preserve the data, and `deserialize_episodes` must accept an empty/whitespace string and return `[]`.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. `json.dumps` / `json.loads` handle the whole list at once — no need to walk fields.
2. Guard the empty case in `deserialize_episodes` before calling `json.loads`, since `json.loads('')` raises.

## Solution explanation
Persistence is what lets an agent remember across runs. JSON is enough for a list of plain dicts; the only sharp edge is an empty file, which we map to an empty list instead of letting it raise.
