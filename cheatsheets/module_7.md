# Cheat Sheet — Module 7: Production realities

Harden the agent against **runaway cost** and **silent failure**.

## Cost + step caps (V7.2)

```python
from agent.loop import enforce_caps

reason = enforce_caps(steps, cost_usd, max_steps=5, max_cost_usd=0.30)
# returns a halt-reason string, or None if within both caps
# checks STEPS first, then COST; an unset (None) cap is never enforced
if reason:
    halt(reason)
```

Built into the `Agent`:

```python
from agent import Agent
agent = Agent(max_steps=6, max_cost_usd=0.50, logger=print)
agent.run(task)
agent.cost_usd      # accumulated estimate
agent.stop_reason   # "stop_condition" | "max_steps" | "max_cost ($0.5) reached" | ...
agent.log           # list of structured records (below)
```

## Structured logging (V7.4)

```python
from agent.loop import format_log_record
format_log_record(step=1, action="llm_call", detail="…",
                  cost_usd=0.01, cumulative_cost_usd=0.01, tokens=120)
# -> flat dict, stable schema:
{ "step": 1, "action": "llm_call", "detail": "…",
  "cost_usd": 0.01, "cumulative_cost_usd": 0.01, "tokens": 120, "ok": True }
```

One flat dict per step → JSON-lines → your log aggregator.

## Guardrails (V7.5)

```python
from agent.loop import guardrail_check
allowed, reason = guardrail_check("shell", args,
                                  allow=["search","calc"], block=["shell"],
                                  patterns=["*rm -rf*"])
```

Precedence: **block (denylist) wins → allow (allowlist) → patterns**. Wire into a `ToolAgent`:

```python
ToolAgent(registry, allow=["search"], block=["shell"])   # checked before dispatch
```

## Cost estimation

```python
from agent.loop import estimate_cost
estimate_cost(response, prices={"prompt": 0.0005, "completion": 0.0015})  # from response.raw usage
```

## Latency notes

- Latency ≈ tokens × per-token time + network round-trips. More steps = more round-trips.
- **Streaming** improves *perceived* latency (first token sooner); it doesn't reduce total cost.
- Fewer, fuller turns usually beat many tiny ones.

## Gotchas

- **Denylist beats allowlist** — an explicitly dangerous tool stays blocked. Safe default.
- **Caps are pure & cheap** — call `enforce_caps` every iteration.
- **Log shape must be stable** — downstream tooling depends on the fixed key set.
- **Guardrail-as-rules ≠ LLM classifier.** This module grades the rule-based version.
