# EX5.1 — Route a message

**Implements:** EX5.1 (source V5.3)

## Learning objective
Route a structured message to the agent named as its recipient.

## Problem statement
Write `route_message(message, roles)` where `message` is a dict with a `recipient` key and `roles` maps role name -> handler. Return the handler for the recipient. Raise `KeyError` if no such role exists.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Read `message['recipient']`, then look it up in `roles`.
2. Check membership first so a missing recipient raises a clear `KeyError` rather than returning `None`.

## Solution explanation
Message passing is how agents coordinate. Routing is deliberately strict — an unroutable message is a bug, so we surface it loudly instead of silently dropping the message.
