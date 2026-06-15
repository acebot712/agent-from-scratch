"""Generate the graded assignment notebooks (scaffold + solution).

Run:  python assignments/_build_assignments.py
Produces, per module N in 1..8:
    assignments/assignment_N.ipynb           (scaffold with TODOs; faded support)
    assignments/assignment_N_solution.ipynb  (reference solution)

Design contract with grader/grade.py:
  * Each assignment defines specific top-level FUNCTIONS (named below) that the
    grader imports by exec-ing the notebook's code cells.
  * Graded functions are deterministic or take injected dependencies (a fake
    `llm`, fake workers, fixture vectors) so grading never needs a live key and
    is stable — exactly the spec's "grade on structure, not exact text" rule.
  * Any cell that hits a real LLM is guarded by `if os.environ.get('RUN_LIVE')`,
    so exec-ing the notebook for grading does no network I/O.

Faded support: assignment_1 is heavily scaffolded; later assignments give only
signatures.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BOOT = (
    "import os, sys\n"
    "sys.path.insert(0, os.path.abspath(os.path.join('..', 'src')))"
)


def md(s):
    return ("md", s)


def code(s):
    return ("code", s)


def turn(clean, solution):
    return ("turn", clean, solution)


ASSIGN = {}


def assignment(n, title, objective, cells):
    ASSIGN[n] = dict(title=title, objective=objective, cells=cells)


# === Assignment 1 — the agent loop (LLM; graded on loop structure) ===========
assignment(
    1, "Build a multi-step agent loop",
    "Build a loop that solves a multi-step word problem: call the model, feed "
    "results back, and stop correctly (Module 1).",
    [
        md("# Assignment 1 — the agent loop\n"
           "Implements: **assignment_1 (Module 1)**\n\n"
           "**Goal:** write `solve(task, llm, max_steps=6)`.\n\n"
           "- `llm` is a callable: `llm(messages) -> str` (so we can grade you with a "
           "fake model — no API key needed for grading).\n"
           "- Loop: append the model reply, stop when it contains `FINAL ANSWER:` and "
           "return what follows; otherwise nudge it to continue.\n"
           "- Never exceed `max_steps` calls to `llm`.\n\n"
           "Grading is structural: did you stop on the marker, respect the cap, and "
           "return the parsed answer?"),
        code(BOOT),
        turn(
            "DONE = 'FINAL ANSWER:'\n\n"
            "def solve(task, llm, max_steps=6):\n"
            "    messages = [\n"
            "        {'role': 'system', 'content': 'Solve step by step. End with FINAL ANSWER: <x>.'},\n"
            "        {'role': 'user', 'content': task},\n"
            "    ]\n"
            "    for _ in range(max_steps):\n"
            "        reply = llm(messages)                 # 👉 TODO: call the model\n"
            "        # 👉 TODO: append the assistant reply to messages\n"
            "        # 👉 TODO: if DONE in reply, return the text AFTER the marker, stripped\n"
            "        # 👉 TODO: else append a user 'Continue.' message\n"
            "        ...\n"
            "    return '[no final answer]'\n",
            "DONE = 'FINAL ANSWER:'\n\n"
            "def solve(task, llm, max_steps=6):\n"
            "    messages = [\n"
            "        {'role': 'system', 'content': 'Solve step by step. End with FINAL ANSWER: <x>.'},\n"
            "        {'role': 'user', 'content': task},\n"
            "    ]\n"
            "    for _ in range(max_steps):\n"
            "        reply = llm(messages)\n"
            "        messages.append({'role': 'assistant', 'content': reply})\n"
            "        if DONE in reply:\n"
            "            return reply.split(DONE, 1)[1].strip()\n"
            "        messages.append({'role': 'user', 'content': 'Continue.'})\n"
            "    return '[no final answer]'\n"),
        code("# Smoke-check with a tiny scripted fake model (this is the idea the grader uses):\n"
             "def fake_llm(messages):\n"
             "    n = sum(1 for m in messages if m['role'] == 'assistant')\n"
             "    return 'FINAL ANSWER: 42' if n >= 2 else 'thinking...'\n"
             "print(solve('demo', fake_llm))  # expect '42'"),
        code("# Optional live run (needs a key):\n"
             "if os.environ.get('RUN_LIVE') == '1':\n"
             "    from agent.llm import complete\n"
             "    print(solve('A pen costs $2, a book $5. How much for 3 pens and 2 books?',\n"
             "                lambda msgs: complete(msgs).text))"),
    ])

# === Assignment 2 — tools + registry + dispatch (graded deterministically) ===
assignment(
    2, "Three tools, a registry, and dispatch",
    "Build 3 tools + a registry + dispatch; the agent must select the right tool "
    "and fail gracefully on unknown tools (Module 2).",
    [
        md("# Assignment 2 — tools, registry, dispatch\n"
           "Implements: **assignment_2 (Module 2)**\n\n"
           "Define:\n"
           "- `build_registry()` → a `ToolRegistry` with **three** tools named "
           "`add`, `upper`, `length`.\n"
           "- `handle(text, registry)` → parse a tool request from `text`, dispatch it, "
           "and return the `ToolResult`.\n\n"
           "Graded on correct tool selection and graceful unknown-tool handling — no "
           "LLM needed."),
        code(BOOT),
        code("from agent.tools import Tool, ToolRegistry, parse_tool_call, dispatch"),
        turn(
            "def build_registry():\n"
            "    reg = ToolRegistry()\n"
            "    # 👉 TODO: register three tools: add(a,b)->a+b, upper(s)->s.upper(), length(s)->len(s)\n"
            "    ...\n"
            "    return reg\n",
            "def build_registry():\n"
            "    reg = ToolRegistry()\n"
            "    reg.register(Tool('add', 'add a and b', lambda a, b: a + b,\n"
            "        {'type':'object','properties':{'a':{'type':'number'},'b':{'type':'number'}}}))\n"
            "    reg.register(Tool('upper', 'uppercase s', lambda s: s.upper(),\n"
            "        {'type':'object','properties':{'s':{'type':'string'}}}))\n"
            "    reg.register(Tool('length', 'length of s', lambda s: len(s),\n"
            "        {'type':'object','properties':{'s':{'type':'string'}}}))\n"
            "    return reg\n"),
        turn(
            "def handle(text, registry):\n"
            "    # 👉 TODO: parse the tool call from text, then dispatch against the registry\n"
            "    ...\n",
            "def handle(text, registry):\n"
            "    call = parse_tool_call(text)\n"
            "    return dispatch(registry, call)\n"),
        code("reg = build_registry()\n"
             "print(handle('TOOL: add\\nARGS: {\"a\": 2, \"b\": 3}', reg).output)   # 5\n"
             "print(handle('TOOL: ghost\\nARGS: {}', reg).ok)                       # False"),
    ])

# === Assignment 3 — semantic retrieval (deterministic via fixed embeddings) ==
assignment(
    3, "Semantic retrieval into context",
    "Implement semantic retrieval over a small doc set and inject the top-k into a "
    "context string (Module 3). Graded on a fixed embedding fixture.",
    [
        md("# Assignment 3 — retrieval into context\n"
           "Implements: **assignment_3 (Module 3)**\n\n"
           "Define:\n"
           "- `retrieve(query_vec, doc_vecs, k=3)` → list of doc indices, best first.\n"
           "- `build_context(query_vec, doc_vecs, docs, k=3)` → a string containing the "
           "top-k docs (one per line).\n\n"
           "Use cosine similarity. Graded with a **fixed embedding fixture** so scoring "
           "is deterministic."),
        code(BOOT),
        code("import numpy as np"),
        turn(
            "def cosine(a, b):\n"
            "    # 👉 TODO: cosine similarity, zero-vector safe\n"
            "    ...\n\n"
            "def retrieve(query_vec, doc_vecs, k=3):\n"
            "    # 👉 TODO: score every doc, return the indices of the top-k\n"
            "    ...\n",
            "def cosine(a, b):\n"
            "    a, b = np.asarray(a, float), np.asarray(b, float)\n"
            "    d = np.linalg.norm(a) * np.linalg.norm(b)\n"
            "    return 0.0 if d == 0 else float(np.dot(a, b) / d)\n\n"
            "def retrieve(query_vec, doc_vecs, k=3):\n"
            "    scored = sorted(range(len(doc_vecs)),\n"
            "                    key=lambda i: cosine(query_vec, doc_vecs[i]), reverse=True)\n"
            "    return scored[:k]\n"),
        turn(
            "def build_context(query_vec, doc_vecs, docs, k=3):\n"
            "    # 👉 TODO: retrieve top-k indices and join the matching docs with newlines\n"
            "    ...\n",
            "def build_context(query_vec, doc_vecs, docs, k=3):\n"
            "    idx = retrieve(query_vec, doc_vecs, k)\n"
            "    return '\\n'.join(docs[i] for i in idx)\n"),
        code("import json\n"
             "FIX = os.path.abspath(os.path.join('..', 'fixtures', 'embeddings'))\n"
             "vecs = np.load(os.path.join(FIX, 'doc_vectors.npy'))\n"
             "docs = json.load(open(os.path.join(FIX, 'docs.json')))\n"
             "print(build_context(vecs[0], vecs, docs, k=2))  # expect the two France lines"),
    ])

# === Assignment 4 — reflection/retry (retry budget deterministic) ===========
assignment(
    4, "A reflection loop with a retry budget",
    "Implement a self-critique-and-retry loop that fixes a failing output within N "
    "retries and never exceeds the budget (Module 4).",
    [
        md("# Assignment 4 — reflection & retry\n"
           "Implements: **assignment_4 (Module 4)**\n\n"
           "Define `reflect(attempt, is_good, critique, max_retries=2)`:\n"
           "- call `attempt()`; if `is_good(result)` is False, call `critique(result)` and "
           "retry — up to `max_retries` extra times.\n"
           "- return a dict: `{'result', 'success', 'retries_used', 'critiques'}`.\n\n"
           "Graded by injecting scripted `attempt`/`is_good` — measures that you improve "
           "and respect the budget."),
        code(BOOT),
        turn(
            "def reflect(attempt, is_good, critique, max_retries=2):\n"
            "    # 👉 TODO: run attempt(); while not good and budget remains, critique + retry\n"
            "    # 👉 track retries_used and collect critiques; never exceed max_retries retries\n"
            "    ...\n",
            "def reflect(attempt, is_good, critique, max_retries=2):\n"
            "    critiques, used = [], 0\n"
            "    result = attempt()\n"
            "    while not is_good(result) and used < max_retries:\n"
            "        critiques.append(critique(result))\n"
            "        used += 1\n"
            "        result = attempt()\n"
            "    return {'result': result, 'success': is_good(result),\n"
            "            'retries_used': used, 'critiques': critiques}\n"),
        code("# scripted check: succeeds on the 3rd attempt\n"
             "box = {'n': 0}\n"
             "def attempt():\n    box['n'] += 1; return box['n']\n"
             "rec = reflect(attempt, lambda r: r >= 3, lambda r: f'too small {r}', max_retries=5)\n"
             "print(rec['success'], rec['retries_used'])  # True 2"),
    ])

# === Assignment 5 — multi-agent crew (routing/cap deterministic) =============
assignment(
    5, "A research → write → review crew",
    "Build a 3-agent crew with deterministic routing and a delegation cap, then "
    "synthesize the outputs (Module 5).",
    [
        md("# Assignment 5 — coordinator crew\n"
           "Implements: **assignment_5 (Module 5)**\n\n"
           "Define:\n"
           "- `plan(task)` → list of `(role, subtask)` with exactly the roles "
           "`research`, `write`, `review` (in that order).\n"
           "- `make_cap()` → a `DelegationCap` that allows at most depth 3.\n"
           "- `run_crew(task, workers)` → run each planned subtask through "
           "`workers[role].handle(subtask)`, then return "
           "`synthesize_outputs([...])`. `workers` is injected (fakes in grading).\n\n"
           "Graded on routing, cap enforcement, and the merged result — no live key."),
        code(BOOT),
        code("from agent.multiagent import DelegationCap, synthesize_outputs"),
        turn(
            "def plan(task):\n"
            "    # 👉 TODO: return [('research', task), ('write', task), ('review', task)]\n"
            "    ...\n\n"
            "def make_cap():\n"
            "    # 👉 TODO: return a DelegationCap with max_depth=3\n"
            "    ...\n",
            "def plan(task):\n"
            "    return [('research', task), ('write', task), ('review', task)]\n\n"
            "def make_cap():\n"
            "    return DelegationCap(max_depth=3)\n"),
        turn(
            "def run_crew(task, workers):\n"
            "    # 👉 TODO: for each (role, subtask) in plan(task), call workers[role].handle(subtask)\n"
            "    # 👉 collect outputs, return synthesize_outputs(outputs)\n"
            "    ...\n",
            "def run_crew(task, workers):\n"
            "    outputs = [workers[role].handle(sub) for role, sub in plan(task)]\n"
            "    return synthesize_outputs(outputs)\n"),
        code("# fake workers (no LLM): each just echoes its role\n"
             "class Fake:\n"
             "    def __init__(self, tag): self.tag = tag\n"
             "    def handle(self, task): return f'{self.tag}: {task}'\n"
             "workers = {r: Fake(r) for r in ('research', 'write', 'review')}\n"
             "print(run_crew('otters', workers)['count'])  # 3"),
    ])

# === Assignment 6 — eval suite (deterministic) ==============================
assignment(
    6, "An eval suite over recorded traces",
    "Write an eval suite that scores agents over a fixed shipped trace set (Module "
    "6). Graded on correct metric computation.",
    [
        md("# Assignment 6 — eval suite\n"
           "Implements: **assignment_6 (Module 6)** · fully deterministic\n\n"
           "Define `evaluate(traces)` returning a dict with keys "
           "`success_rate`, `avg_steps`, `cost_per_task`, `failures` "
           "(a category→count dict). You may use `agent.evals` helpers."),
        code(BOOT),
        code("from agent.evals import (success_rate, step_efficiency, cost_per_task,\n"
             "                         failure_breakdown, load_traces)"),
        turn(
            "def evaluate(traces):\n"
            "    # 👉 TODO: return the four metrics in a dict (see keys above)\n"
            "    ...\n",
            "def evaluate(traces):\n"
            "    return {\n"
            "        'success_rate': success_rate(traces),\n"
            "        'avg_steps': step_efficiency(traces),\n"
            "        'cost_per_task': cost_per_task(traces),\n"
            "        'failures': failure_breakdown(traces),\n"
            "    }\n"),
        code("FIX = os.path.abspath(os.path.join('..', 'fixtures', 'traces'))\n"
             "print(evaluate(load_traces(os.path.join(FIX, 'runA.json'))))"),
    ])

# === Assignment 7 — hardening (deterministic) ===============================
assignment(
    7, "Harden the framework: caps + logging",
    "Add cost/step caps and structured logging (Module 7). Graded on cap "
    "enforcement and log-record shape.",
    [
        md("# Assignment 7 — caps & logging\n"
           "Implements: **assignment_7 (Module 7)** · fully deterministic\n\n"
           "Define:\n"
           "- `cap(steps, cost, max_steps, max_cost)` → a halt-reason string, or "
           "`None` if within both caps. (Check steps first.)\n"
           "- `log_record(step, action, cost, cumulative)` → a flat dict with keys "
           "`step, action, cost_usd, cumulative_cost_usd, ok`.\n\n"
           "Minimal scaffold — you write the bodies."),
        code(BOOT),
        turn(
            "def cap(steps, cost, max_steps, max_cost):\n"
            "    # 👉 TODO: return a reason string if a cap is hit (steps first), else None\n"
            "    ...\n\n"
            "def log_record(step, action, cost, cumulative):\n"
            "    # 👉 TODO: return the flat dict described above (ok=True)\n"
            "    ...\n",
            "def cap(steps, cost, max_steps, max_cost):\n"
            "    if steps >= max_steps:\n"
            "        return f'max_steps ({max_steps}) reached'\n"
            "    if cost >= max_cost:\n"
            "        return f'max_cost (${max_cost}) reached'\n"
            "    return None\n\n"
            "def log_record(step, action, cost, cumulative):\n"
            "    return {'step': step, 'action': action, 'cost_usd': round(cost, 6),\n"
            "            'cumulative_cost_usd': round(cumulative, 6), 'ok': True}\n"),
        code("print(cap(5, 0.1, 5, 1.0))     # max_steps (5) reached\n"
             "print(cap(2, 1.0, 5, 1.0))     # max_cost ($1.0) reached\n"
             "print(cap(2, 0.1, 5, 1.0))     # None\n"
             "print(log_record(1, 'llm_call', 0.01, 0.01))"),
    ])

# === Assignment 8 — capstone (rubric, no autograder) ========================
assignment(
    8, "Capstone — your flagship agent",
    "Build an original agent on the framework (Module 8). Rubric-based "
    "self-assessment; no automated grade.",
    [
        md("# Capstone — build your flagship agent\n"
           "Implements: **capstone (Module 8)**\n\n"
           "There is no autograder here (the work is open-ended). Instead, build an "
           "agent on the framework and self-assess against the rubric. "
           "`python grader/grade.py 8` prints the rubric checklist.\n\n"
           "## Rubric\n"
           "1. **Uses the loop** — your agent runs on `Agent`/`ToolAgent` (M1/M2).\n"
           "2. **Tools** — at least one real `Tool` registered and called (M2).\n"
           "3. **Memory** — uses working, episodic, or semantic memory (M3).\n"
           "4. **Planning** — uses ReAct or reflection where it helps (M4).\n"
           "5. **Hardening** — a step/cost cap and at least one guardrail (M7).\n"
           "6. **Evaluated** — you ran it over ≥3 tasks and reported success rate (M6).\n\n"
           "Aim for 4/6+. Optional: share for peer review."),
        code(BOOT),
        code("# 👉 Build your capstone here. A starting skeleton:\n"
             "from agent import Tool, ToolRegistry, ToolAgent\n\n"
             "def build():\n"
             "    reg = ToolRegistry()\n"
             "    # register your tools ...\n"
             "    return ToolAgent(reg, max_steps=6, block=['shell'])\n\n"
             "# if os.environ.get('RUN_LIVE') == '1':\n"
             "#     print(build().run('your task here'))"),
        md("### Self-assessment\nTick the rubric items you hit, and note one thing "
           "you'd improve with more time."),
    ])


# ---------------------------------------------------------------------------
def make_cell(cell_type, source):
    cell = {"cell_type": cell_type, "metadata": {}, "source": source.splitlines(keepends=True)}
    if cell_type == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    return cell


def build(n, spec, solution):
    cells = []
    for c in spec["cells"]:
        if c[0] == "md":
            cells.append(make_cell("markdown", c[1]))
        elif c[0] == "code":
            cells.append(make_cell("code", c[1]))
        elif c[0] == "turn":
            cells.append(make_cell("code", c[2] if solution else c[1]))
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
            "assignment": f"assignment_{n}",
            "variant": "solution" if solution else "scaffold",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    name = f"assignment_{n}_solution.ipynb" if solution else f"assignment_{n}.ipynb"
    path = os.path.join(HERE, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(nb, fh, indent=1)
    return path


def main():
    written = []
    for n, spec in ASSIGN.items():
        written.append(build(n, spec, solution=False))
        written.append(build(n, spec, solution=True))
    for p in written:
        print("wrote", os.path.basename(p))
    print(f"\n{len(written)} files ({len(ASSIGN)} assignments x 2 variants)")


if __name__ == "__main__":
    main()
