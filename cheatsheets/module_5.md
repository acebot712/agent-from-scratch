# Cheat Sheet — Module 5: Multi-agent systems

Several agent loops that pass messages. What makes it *safe*: a **delegation cap** (can't recurse forever) + a **deterministic merge** (reproducible results).

## Coordinator / worker

```
            ┌─────────────┐
   task ──▶ │ Coordinator │  decompose → delegate → synthesize
            └──────┬──────┘
        ┌──────────┼──────────┐
     research    write      review     (role = a system prompt)
        └──────────┴──────────┘
                   ▼
            synthesize_outputs(...)
```

```python
from agent import Coordinator, Worker, DelegationCap

workers = {
    "research": Worker("research", "You research facts. Reply with 2 bullet facts."),
    "write":    Worker("write",    "You write a one-sentence summary."),
    "review":   Worker("review",   "You critique the summary in one sentence."),
}
coord = Coordinator(
    workers=workers,
    cap=DelegationCap(max_depth=3),
    decompose=lambda task: [("research", task), ("write", task), ("review", task)],
)
out = coord.run("benefits of cycling")
out["results"]              # per-worker outputs
out["synthesis"]["combined"]
```

## Message passing

```python
from agent import Message, route_message
msg = Message(sender="coord", recipient="writer", content="...")
handler = route_message(msg, roles)   # raises KeyError on unknown recipient
```

## Delegation cap (stop infinite delegation)

```python
from agent import DelegationCap, DelegationError
cap = DelegationCap(max_depth=3)
deeper = cap.enter()        # returns a NEW cap at depth+1
deeper.allows()             # True while depth < max_depth
# cap.enter() past max_depth -> raises DelegationError
```

## Synthesis — mechanical merge (the graded one)

```python
from agent import synthesize_outputs
synthesize_outputs(["a", "b", "a", ""])
# -> {"parts": ["a","b"], "combined": "a\nb", "count": 2}   (strip, drop blanks, dedupe, order-preserving)
```

## Gotchas

- **Cap, or it loops forever.** A delegates to B delegates to A… the depth cap is the only guaranteed brake.
- **`enter()` returns a new cap** — don't mutate; that keeps branches independent.
- **Route strictly.** Unknown recipient → raise, don't silently drop work.
- **Mechanical merge is graded**, LLM-written synthesis is not (it's not reproducible).
- **Roles are prompts.** A "reviewer" is just a worker with a reviewer system prompt.
