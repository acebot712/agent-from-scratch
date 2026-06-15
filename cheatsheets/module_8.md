# Cheat Sheet — Module 8: Capstone (the whole framework, one page)

You built a complete agent framework. Here's the entire public API and how it maps onto the big names.

## One import

```python
from agent import (
    # loop + hardening (M1, M7)
    Agent, default_stop, enforce_caps, format_log_record, guardrail_check, estimate_cost,
    # llm wrapper
    complete, embed, LLMResponse,
    # tools (M2)
    Tool, ToolRegistry, ToolAgent, parse_tool_call, dispatch,
    # memory (M3)
    WorkingMemory, EpisodicMemory, SemanticMemory,
    cosine_similarity, top_k_retrieval, context_budget_trim, count_tokens,
    # planning (M4)
    run_react, parse_react_trace, reflect_and_retry, RetryBudget, tree_of_thoughts, select_strategy,
    # multi-agent (M5)
    Coordinator, Worker, Message, route_message, DelegationCap, synthesize_outputs,
    # evals (M6)
    run_eval, summarize, success_rate, step_efficiency, cost_per_task,
    classify_failure, regression_diff, load_traces, replay_runner,
)
```

## A flagship agent in a few lines

```python
from agent import Tool, ToolRegistry, ToolAgent
reg = ToolRegistry()
reg.register(Tool("calc", "evaluate arithmetic; arg: expression",
                  run=lambda expression: str(eval(expression, {"__builtins__": {}}, {})),
                  parameters={"type":"object","properties":{"expression":{"type":"string"}}}))
agent = ToolAgent(reg, max_steps=6, block=["shell"])   # tools + cap + guardrail
agent.run("What is 12 * 9?")
```

See `examples/flagship_agent.py` for tools + memory + planning + hardening together.

## Framework-equivalence map (V8.4)

| ours | LangChain | CrewAI / AutoGen |
|---|---|---|
| `Agent` / run loop | `AgentExecutor` | `Agent` / `ConversableAgent` |
| `Tool` / `ToolRegistry` | `Tool` / `@tool` | `tool` / function |
| `SemanticMemory` | `VectorStoreRetriever` | Knowledge / RAG |
| `WorkingMemory` + trim | memory + context window | context management |
| `Coordinator` / `Worker` | LCEL chains | `Crew` / `GroupChat` |
| `run_react` / planning | ReAct agent | planner |
| `run_eval` / metrics | LangSmith evals | (custom) |
| `enforce_caps` / `guardrail_check` | callbacks / limits | `max_round` / guardrails |

## Module → file map

| file | module |
|---|---|
| `loop.py` | M1 loop + M7 hardening |
| `tools.py` | M2 |
| `memory.py` | M3 |
| `planning.py` | M4 |
| `multiagent.py` | M5 |
| `evals.py` | M6 |
| `__init__.py` | M8 public API |

## Capstone rubric (aim 4/6)

1. Uses the loop (`Agent`/`ToolAgent`) · 2. ≥1 real tool called · 3. Some memory ·
4. Planning where it helps · 5. A cap + a guardrail · 6. Evaluated over ≥3 tasks.

## The takeaway

Every agent framework on the market is some arrangement of these same pieces — a loop, tools, memory, planning, coordination, evals, and caps. You now understand all of them because you built them.
