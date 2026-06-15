# Cheat Sheet — Module 1: The agent loop, properly

Turn the 20 lines into a **reusable class** with a correct stopping condition and a **provider-agnostic** LLM wrapper.

## The LLM wrapper (`agent.llm`)

```python
from agent.llm import complete, embed

resp = complete(messages, tools=None, model=None)   # -> LLMResponse
resp.text          # normalised assistant text ('' if none)
resp.tool_calls    # list[ToolCall(name, args, id)]
resp.stop_reason   # 'stop' | 'end_turn' | 'tool_calls' | ...
resp.raw           # original provider JSON (usage lives here)

vecs = embed(["doc one", "doc two"])   # -> list[list[float]]  (Module 3)
```

Selected by env var — **one interface, any provider**:

```bash
LLM_PROVIDER=openai      # or: anthropic
LLM_API_KEY=sk-...
# optional: LLM_MODEL, LLM_BASE_URL, LLM_EMBED_MODEL, LLM_EMBED_PROVIDER
```

## The Agent class (`agent.loop`)

```python
from agent import Agent

agent = Agent(
    system_prompt="Solve step by step. End with FINAL ANSWER: <x>.",
    max_steps=6,
    model=None,            # override per agent if you want
)
answer = agent.run("A train goes 60km in 1.5h. Average speed?")
agent.history             # full message trace after the run
```

## Stopping condition (the part everyone gets wrong)

```python
from agent.loop import default_stop, DONE_MARKER  # "FINAL ANSWER:"

def default_stop(response, step, max_steps) -> bool:
    if step >= max_steps:                 return True   # safety exit
    if DONE_MARKER in response.text:      return True   # intentional exit
    if response.stop_reason in ("stop", "end_turn") and not response.tool_calls:
        return True                                     # natural finish
    return False
```

Custom stop: pass any `stop=callable(response, step, max_steps) -> bool` to `Agent`.

## Parsing intent (free text → structure)

```python
"FINAL ANSWER: 42"        -> {"kind": "final", "value": "42"}
"ACTION: add(2, 3)"       -> {"kind": "action", "name": "add", ...}
```

## Gotchas

- **Use `>=` for the step cap**, not `==` — never let it slip past.
- **Normalise at the boundary.** Map each provider's shape to `LLMResponse` once; the loop should never branch on provider.
- **`max_steps` returning a sentinel** ("[no final answer]") is a *signal*, not a crash — bump steps or sharpen the prompt.
