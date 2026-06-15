# Build an AI Agent From Scratch

> **Stop using frameworks you don't understand. Build the whole thing yourself in pure Python.**

This is the companion repository for the course. Across 9 modules you build your own
~1,200 line agent framework — tool use, memory, planning, multi-agent, evals, and
production hardening — and end up able to recognise every concept in any agent framework on
the market (LangChain, CrewAI, AutoGen).

**Dependencies:** `numpy` + a provider-agnostic LLM client (pure standard-library HTTP).
No LangChain, no vector DB, no heavyweight deps. Target: **Python 3.10**.

---

## Quickstart

```bash
git clone <this-repo> agent-from-scratch && cd agent-from-scratch

python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                                   # then edit it (see below)
python examples/hello_agent.py                         # the 20-line Module 0 agent
```

### Get an API key & configure `.env`

The framework is provider-agnostic. Pick one provider and fill in `.env`:

```bash
LLM_API_KEY=sk-...           # your key
LLM_PROVIDER=openai          # "openai" (any OpenAI-compatible endpoint) or "anthropic"
# optional overrides:
# LLM_MODEL=gpt-4o-mini
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_EMBED_MODEL=text-embedding-3-small
# LLM_EMBED_PROVIDER=openai   # Anthropic has no embeddings endpoint; route embed() here
```

- **OpenAI:** create a key at <https://platform.openai.com/api-keys>. Works with any
  OpenAI-compatible base URL (Together, Groq, local servers) via `LLM_BASE_URL`.
- **Anthropic:** create a key at <https://console.anthropic.com/>. Set
  `LLM_PROVIDER=anthropic`. For memory retrieval (`embed()`), also set
  `LLM_EMBED_PROVIDER=openai` with an OpenAI-compatible key, since Anthropic has no
  embeddings endpoint.

> Most coursework runs **offline** (deterministic exercises, eval fixtures, the math
> labs). You only need a key for the live LLM cells — they're clearly marked.

---

## Jump to any module with git tags

The code is **monotonic**: each module builds on the previous one. Every module's
finished state is a git tag, so you can jump to any point in the course:

```bash
git tag                 # module-0 … module-8
git checkout module-3   # repo exactly as it is at the end of Module 3
git checkout main       # back to the latest, complete framework
```

The instructor records each module from its tag, so on-screen code matches what you
check out. Recommended: take the modules in order.

| Tag | Module |
|---|---|
| `module-0` | What an agent actually is (the 20-line build) |
| `module-1` | The agent loop, properly (`Agent`, the LLM wrapper, stopping) |
| `module-2` | Tool use from scratch |
| `module-3` | Memory architectures |
| `module-4` | Planning & reasoning (ReAct, reflection, ToT) |
| `module-5` | Multi-agent systems |
| `module-6` | Evaluating agents (runs on shipped fixtures) |
| `module-7` | Production realities (caps, logging, guardrails) |
| `module-8` | Capstone — the consolidated framework |

---

## How to use each asset

### The framework — `src/agent/`
One import gives you everything built so far:

```python
from agent import Agent, Tool, ToolRegistry, ToolAgent, SemanticMemory, \
    run_react, Coordinator, run_eval, enforce_caps, guardrail_check
```

Examples: `examples/hello_agent.py` (Module 0) and `examples/flagship_agent.py`
(the capstone — tools + memory + planning + caps + guardrail).

### Lab notebooks — `notebooks/`
Guided, mostly-complete notebooks you run cell by cell, with 2–3 **👉 Your turn** cells.

```bash
jupyter notebook notebooks/lab_v3_4_clean.ipynb      # you fill in the TODOs
#                notebooks/lab_v3_4_answers.ipynb     # the solved version
```

Named by video id (`lab_v<module>_<n>_{clean,answers}.ipynb`). Math/eval labs run
offline; LLM labs need your `.env` key.

### Graded assignments — `assignments/` + `grader/`
Scaffolded notebooks with a **local autograder** — no submission server, no key needed
to grade:

```bash
# work in assignments/assignment_3.ipynb, then:
python grader/grade.py 3              # PASS/FAIL per check + a score
python grader/grade.py 3 --solution  # see a full-marks run
```

LLM-dependent assignments are graded **structurally** (did the loop stop, did it retry,
did delegation cap) via injected fakes — stable and offline. See `grader/README.md`.

### Udemy coding exercises — `udemy_exercises/`
24 self-contained autograded exercises (`ex_v<m>_<n>_<slug>/`), each with
`starter.py`, `solution.py`, `evaluation.py`, and `exercise_meta.md`. Standard library
+ numpy only. Run any locally:

```bash
cd udemy_exercises/ex_v3_4_cosine_similarity && python -m unittest evaluation
```

### Quizzes & cheat sheets — `quizzes/`, `cheatsheets/`
`quizzes/module_N.md` — 5–8 questions per module (with answers + explanations).
`cheatsheets/module_N.md` — one-page dense reference per module.

---

## Running the tests

```bash
pytest tests/                 # offline smoke tests (one file per module)
python tests/run_all.py       # same tests, no pytest required

# optional live end-to-end (hits a real provider):
RUN_LIVE=1 LLM_PROVIDER=openai LLM_API_KEY=sk-... pytest tests/test_live.py
```

---

## Repository layout

```
src/agent/        the framework you build (llm, loop, tools, memory, planning,
                  multiagent, evals, __init__)
examples/         runnable demos (hello_agent, flagship_agent)
notebooks/        guided lab notebooks (clean + answers)
assignments/      scaffolded assignment notebooks (+ solutions)
grader/           local autograder: python grader/grade.py N
udemy_exercises/  24 deterministic autograded exercises
fixtures/         shipped trace + embedding data (offline, deterministic)
quizzes/          per-module quiz banks
cheatsheets/      per-module one-page references
tests/            per-module smoke tests
COURSE_SPEC.md    the authoritative course spec
MANIFEST.md       every asset and its path, at a glance
```

See [COURSE_SPEC.md](COURSE_SPEC.md) for the full breakdown and [MANIFEST.md](MANIFEST.md)
for a coverage index.
