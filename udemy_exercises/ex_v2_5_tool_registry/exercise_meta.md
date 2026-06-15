# EX2.2 — A tool registry

**Implements:** EX2.2 (source V2.5)

## Learning objective
Register tools by name and call the right one by name.

## Problem statement
Implement a `ToolRegistry` class with: `register(name, fn)` (raise `ValueError` on a duplicate name), `has(name) -> bool`, `names() -> sorted list`, and `call(name, **kwargs)` which runs the registered function (raise `KeyError` for an unknown name).

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Back the registry with a plain dict: name -> function.
2. `call` should look the name up, raise `KeyError` if missing, else invoke `fn(**kwargs)`.

## Solution explanation
The registry is the lookup table that turns a parsed tool name into an actual callable. Guarding duplicate registration and unknown calls keeps dispatch predictable as the toolset grows.
