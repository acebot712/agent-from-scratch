# Cheat Sheet — Module 0: What an agent actually is

**The one definition:** *An agent is an LLM in a loop that chooses its own next action.* Tools, memory, planning, multi-agent, and evals are all additions to this core.

## The loop (5 parts)

```
observe → decide → act → feed back → stop
  │         │        │       │          │
  input   LLM call  run a   append      terminal-state
          (decide   tool /  result to   check (marker
          next)     answer  history     OR step cap)
```

Drop any part and it breaks: no *feed back* → no progress; no *stop* → infinite loop.

## The 20-line reference agent

```python
from agent.llm import complete   # provider-agnostic LLM call

DONE = "FINAL ANSWER:"

def run(task, max_steps=5):
    messages = [
        {"role": "system", "content": f"Reason step by step. End with '{DONE} <answer>'."},
        {"role": "user", "content": task},
    ]
    for _ in range(max_steps):
        reply = complete(messages).text          # decide
        messages.append({"role": "assistant", "content": reply})
        if DONE in reply:                        # stop
            return reply.split(DONE, 1)[1].strip()
        messages.append({"role": "user", "content": "Continue."})  # feed back
    return "[no final answer — hit max_steps]"
```

```bash
LLM_PROVIDER=openai LLM_API_KEY=sk-... python examples/hello_agent.py
```

## Gotchas

- **No stop = runaway.** Always pair an intentional exit (the marker) with a safety exit (`max_steps`).
- **Frameworks aren't magic.** LangChain/CrewAI wrap *this* loop. Once you can write it, you can read any of them.
- **The model can't *do* anything** — it only emits text. Acting is your code running on that text (see Module 2).
- **History grows every turn.** Fine for short tasks; Module 3 handles the budget.
