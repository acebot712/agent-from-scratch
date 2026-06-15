# Cheat Sheet — Module 2: Tool use from scratch

**Key idea:** the model can't run code. "Tool use" = the model *requests* a call in text; **your** code runs it and feeds back the result. Native function calling is the same loop with a provider-managed format.

## Tool signature (`agent.tools`)

```python
from agent import Tool, ToolRegistry

weather = Tool(
    name="get_weather",
    description="current weather for a city; arg: city",
    run=lambda city: f"{city}: 18C cloudy",
    parameters={"type": "object", "properties": {"city": {"type": "string"}}},
)
```

## Registry + dispatch

```python
reg = ToolRegistry()
reg.register(weather)
reg.names()         # ['get_weather']  (sorted)
reg.describe()      # human catalogue for hand-rolled prompting
reg.schemas()       # provider tool schemas for native function calling

from agent import parse_tool_call, dispatch
call = parse_tool_call('TOOL: get_weather\nARGS: {"city": "Paris"}')
#   -> {"name": "get_weather", "args": {"city": "Paris"}}  (None if no TOOL line)
res = dispatch(reg, call)            # never raises
res.ok        # True / False
res.output    # on success
res.error     # on failure
res.as_observation()   # "get_weather -> Paris: 18C cloudy"
```

## Tool-using agent (loop + tools wired)

```python
from agent import ToolAgent
agent = ToolAgent(reg, max_steps=6, block=["shell"])   # block = guardrail (M7)
agent.run("What's the weather in Paris?")
```

Prompt format the model is asked to emit:

```
TOOL: <name>
ARGS: {"arg": "value"}
# ...or when done:
FINAL ANSWER: <answer>
```

## Failure handling (V2.7) — dispatch returns, never throws

| Situation | `res.ok` | `res.error` contains |
|---|---|---|
| unknown / hallucinated tool | `False` | `unknown tool '<name>'` |
| missing/wrong args (TypeError) | `False` | `bad arguments` |
| tool raises at runtime | `False` | `<ExcType>: ...` |
| malformed args JSON | `False` | `malformed arguments` |

## Gotchas

- **Parse defensively.** Malformed JSON → empty/flagged args, not a crash.
- **Feed errors back.** An error observation lets the model self-correct; a raised exception kills the run.
- **Register once.** Duplicate `register` raises `ValueError` — catch name collisions early.
