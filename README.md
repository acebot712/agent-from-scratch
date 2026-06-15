# Build an AI Agent From Scratch

> Stop using frameworks you don't understand. Build the whole thing yourself in pure Python.

This repo is the companion codebase for the course. You build a complete,
readable (~1,200 line) agent framework yourself — tool use, memory, planning,
multi-agent, and evals — and end up able to recognise every concept in any agent framework on the market.

**Status:** `module-0` seed. See [COURSE_SPEC.md](COURSE_SPEC.md) for the full,
authoritative module/asset breakdown.

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env          # then fill in LLM_API_KEY and LLM_PROVIDER
python examples/hello_agent.py
```

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
