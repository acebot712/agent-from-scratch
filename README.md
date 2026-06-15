# Build an AI Agent From Scratch

> Stop using frameworks you don't understand. Build the whole thing yourself in pure Python.

This repo is the companion codebase for the course. You build a complete,
readable (~1,200 line) agent framework yourself — tool use, memory, planning,
multi-agent, and evals — and end up able to recognise every concept in any agent framework on the market.

**Status:** framework complete through `module-8` (tags `module-0` … `module-8`).
See [COURSE_SPEC.md](COURSE_SPEC.md) for the full, authoritative module/asset
breakdown.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in LLM_API_KEY and LLM_PROVIDER
python examples/hello_agent.py        # the 20-line Module 0 build
python examples/flagship_agent.py     # the capstone, tools+memory+planning+caps
```

## Running the tests

```bash
pytest tests/                 # offline smoke tests, one file per module
python tests/run_all.py       # same tests, no pytest needed

# optional live end-to-end (hits a real provider):
RUN_LIVE=1 LLM_PROVIDER=openai LLM_API_KEY=sk-... pytest tests/test_live.py
```

## The framework (one import)

```python
from agent import Agent, Tool, ToolRegistry, ToolAgent, SemanticMemory, \
    run_react, Coordinator, run_eval, enforce_caps, guardrail_check
```

| module file | what it adds |
|---|---|
| `loop.py` | `Agent` + run loop; caps, logging, guardrails (M1, M7) |
| `tools.py` | tool interface, registry, dispatch, `ToolAgent` (M2) |
| `memory.py` | working/episodic/semantic memory + cosine retrieval (M3) |
| `planning.py` | ReAct, reflection/retry, tree-of-thoughts (M4) |
| `multiagent.py` | coordinator/worker, routing, delegation cap, synthesis (M5) |
| `evals.py` | metrics, failure taxonomy, regression diff, harness (M6) |

## Layout

```
src/agent/    the framework you build (llm.py, loop.py, ... grows per module)
examples/     runnable demos (hello_agent.py = the 20-line Module 0 build)
notebooks/    guided lab notebooks
assignments/  scaffolded assignment notebooks (graded locally)
grader/       local autograder for assignments
udemy_exercises/  deterministic autograded coding exercises
quizzes/      per-module quiz banks
cheatsheets/  per-module cheat sheets
tests/        per-module smoke tests
```

## How to follow along

The code is monotonic — each module imports prior modules. Tags `module-0` …
`module-8` mark the repo state after each module. Jump to any point with
`git checkout module-N`.
