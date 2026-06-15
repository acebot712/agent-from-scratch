# Cheat Sheet — Module 4: Planning & reasoning

One LLM call isn't enough for multi-step tasks. Make the agent **reason, act, and self-correct**.

## ReAct format (interleave reasoning + action)

```
Thought: <reasoning>
Action: <tool_name>[<input>]
Observation: <filled in by your harness>
... (repeat) ...
Answer: <final answer>
```

```python
from agent.planning import parse_react_trace, extract_answer, run_react

steps = parse_react_trace(text)   # -> [{thought, action, action_input, observation}, ...]
extract_answer(text)              # -> "..." or None

run_react(task, registry, max_steps=6)   # drives the full ReAct loop over your tools
```

An **Observation closes a step**; a new **Thought** starts the next.

## Reflection: critique + retry within a budget

```python
from agent.planning import RetryBudget, reflect_and_retry

b = RetryBudget(max_retries=2)
b.can_retry(); b.consume()  # True while budget remains, else False
b.remaining                 # countdown

rec = reflect_and_retry(
    attempt=lambda: make_output(),
    is_good=lambda r: passes(r),
    critique=lambda r: "what's wrong with r",
    max_retries=2,
)
rec["success"], rec["retries_used"], rec["critiques"]
```

## Tree-of-thoughts (a taste)

```python
from agent.planning import tree_of_thoughts
best = tree_of_thoughts(propose=lambda: [c1, c2, c3], score=lambda c: rate(c), keep=1)
# propose candidates -> score each -> keep top-N
```

## Strategy selection (rule-based router)

```python
from agent.planning import select_strategy
select_strategy(meta) -> "react" | "reflection" | "tot" | "direct"
```

| Task metadata | Strategy |
|---|---|
| `needs_tools` | `react` |
| `verifiable` and `difficulty == "hard"` | `reflection` |
| `open_ended` or `branching` | `tot` |
| (otherwise) | `direct` |

## Gotchas

- **No retry budget = infinite reflection.** Always cap it.
- **Reflection needs a checker.** `is_good` must be able to detect failure, or there's nothing to correct toward.
- **ReAct actions *are* tool calls** — Module 4 sits on top of Module 2.
- **Don't over-reason.** Route easy tasks to `direct`; ToT/reflection cost real tokens.
