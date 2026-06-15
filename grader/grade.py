"""Local autograder for the course assignments.

Usage:
    python grader/grade.py N            # grade assignment N (1..8)
    python grader/grade.py N --solution # grade the reference solution (should be 100%)

It loads ``assignments/assignment_N.ipynb``, exec's its code cells to import the
functions you wrote, then runs assertion-based checks. LLM-dependent assignments
are graded on **structure** — we inject scripted fakes, so grading needs no API
key and is deterministic (a fixed fake model, fixed fixtures, fixed worker
stubs). Each check prints PASS/FAIL; a final score is printed at the end.

Assignment 8 (capstone) is rubric-based and prints a checklist instead of a score.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
FIX_TRACES = os.path.join(ROOT, "fixtures", "traces")
FIX_EMB = os.path.join(ROOT, "fixtures", "embeddings")


# --- notebook loading ----------------------------------------------------------

def load_notebook(n: int, solution: bool) -> dict:
    """Exec the assignment notebook's code cells and return its namespace.

    RUN_LIVE is force-cleared so any live-guarded demo cells are skipped — grading
    never hits the network.
    """
    name = f"assignment_{n}_solution.ipynb" if solution else f"assignment_{n}.ipynb"
    path = os.path.join(ROOT, "assignments", name)
    if not os.path.exists(path):
        raise SystemExit(f"not found: {path}")
    nb = json.load(open(path, encoding="utf-8"))
    os.environ.pop("RUN_LIVE", None)
    ns: dict = {"__name__": "assignment"}
    # cwd-relative paths in notebooks assume the assignments/ dir
    old = os.getcwd()
    os.chdir(os.path.join(ROOT, "assignments"))
    try:
        for cell in nb["cells"]:
            if cell["cell_type"] != "code":
                continue
            src = "".join(cell["source"])
            try:
                exec(compile(src, f"<{name}:cell>", "exec"), ns)  # noqa: S102
            except Exception:
                # A demo/smoke cell that calls an unfinished function will raise.
                # Definitions run before demos, so keep going — the checks below
                # test the functions directly. (Syntax errors still surface here.)
                continue
    finally:
        os.chdir(old)
    return ns


# --- check harness -------------------------------------------------------------

class Checker:
    def __init__(self):
        self.results: list[tuple[str, bool, str]] = []

    def check(self, name: str, fn):
        try:
            fn()
            self.results.append((name, True, ""))
        except AssertionError as e:
            self.results.append((name, False, str(e) or "assertion failed"))
        except Exception as e:  # missing function, TODO left as ..., etc.
            self.results.append((name, False, f"{type(e).__name__}: {e}"))

    def require(self, ns: dict, *names: str):
        for fn_name in names:
            self.check(f"defines {fn_name}()", lambda fn_name=fn_name: _assert(
                callable(ns.get(fn_name)), f"{fn_name} is not defined"))


def _assert(cond, msg):
    assert cond, msg


# --- per-assignment checks -----------------------------------------------------

def grade_1(ns, c: Checker):
    c.require(ns, "solve")
    solve = ns.get("solve")

    def stops_on_marker():
        calls = {"n": 0}
        def fake(messages):
            calls["n"] += 1
            return "FINAL ANSWER: 42" if calls["n"] >= 3 else "still thinking"
        out = solve("q", fake, max_steps=6)
        assert out.strip() == "42", f"expected '42', got {out!r}"
        assert calls["n"] == 3, f"should stop at the marker (3 calls), made {calls['n']}"
    c.check("stops on FINAL ANSWER and parses it", stops_on_marker)

    def respects_cap():
        calls = {"n": 0}
        def fake(messages):
            calls["n"] += 1
            return "never done"
        solve("q", fake, max_steps=4)
        assert calls["n"] <= 4, f"exceeded max_steps: {calls['n']} calls"
    c.check("never exceeds max_steps", respects_cap)


def grade_2(ns, c: Checker):
    c.require(ns, "build_registry", "handle")
    reg = ns["build_registry"]()

    c.check("registers exactly 3 tools",
            lambda: _assert(len(reg.names()) == 3, f"got {reg.names()}"))
    c.check("has add/upper/length",
            lambda: _assert({"add", "upper", "length"} <= set(reg.names()), reg.names()))

    def add_dispatch():
        res = ns["handle"]('TOOL: add\nARGS: {"a": 2, "b": 3}', reg)
        assert res.ok and res.output == 5, f"add gave {res.output!r} ok={res.ok}"
    c.check("dispatches add correctly", add_dispatch)

    def unknown_graceful():
        res = ns["handle"]('TOOL: ghost\nARGS: {}', reg)
        assert res.ok is False, "unknown tool should not be ok"
    c.check("handles unknown tool gracefully", unknown_graceful)


def grade_3(ns, c: Checker):
    import numpy as np
    c.require(ns, "retrieve", "build_context")
    vecs = np.load(os.path.join(FIX_EMB, "doc_vectors.npy"))
    docs = json.load(open(os.path.join(FIX_EMB, "docs.json")))

    def topk_geo():
        idx = list(ns["retrieve"](vecs[0], vecs, k=2))
        assert set(idx) == {0, 1}, f"expected docs 0,1 (France cluster), got {idx}"
        assert idx[0] == 0, f"best match should be doc 0, got {idx[0]}"
    c.check("retrieves the right top-2", topk_geo)

    def context_has_docs():
        ctx = ns["build_context"](vecs[2], vecs, docs, k=2)  # biology cluster
        assert "Photosynthesis" in ctx and "Chlorophyll" in ctx, ctx
    c.check("build_context injects the top-k docs", context_has_docs)


def grade_4(ns, c: Checker):
    c.require(ns, "reflect")
    reflect = ns["reflect"]

    def improves_within_budget():
        box = {"n": 0}
        def attempt():
            box["n"] += 1
            return box["n"]
        rec = reflect(attempt, lambda r: r >= 3, lambda r: "small", max_retries=5)
        assert rec["success"] is True, rec
        assert rec["retries_used"] == 2, f"expected 2 retries, got {rec['retries_used']}"
    c.check("retries until good", improves_within_budget)

    def respects_budget():
        rec = reflect(lambda: 0, lambda r: r == 1, lambda r: "no", max_retries=2)
        assert rec["success"] is False, rec
        assert rec["retries_used"] == 2, f"should stop at budget 2, got {rec['retries_used']}"
    c.check("never exceeds the retry budget", respects_budget)


def grade_5(ns, c: Checker):
    from agent.multiagent import DelegationError
    c.require(ns, "plan", "make_cap", "run_crew")

    c.check("plan has research/write/review in order",
            lambda: _assert([r for r, _ in ns["plan"]("t")] == ["research", "write", "review"],
                            ns["plan"]("t")))

    def cap_enforced():
        cap = ns["make_cap"]()
        d = cap
        for _ in range(3):
            d = d.enter()
        try:
            d.enter()
        except DelegationError:
            return
        raise AssertionError("delegation cap not enforced past depth 3")
    c.check("delegation cap halts runaway delegation", cap_enforced)

    def crew_synthesizes():
        class Fake:
            def __init__(self, tag): self.tag = tag
            def handle(self, task): return f"{self.tag}:{task}"
        workers = {r: Fake(r) for r in ("research", "write", "review")}
        out = ns["run_crew"]("x", workers)
        assert out["count"] == 3, f"expected 3 merged outputs, got {out['count']}"
    c.check("run_crew merges all three workers", crew_synthesizes)


def grade_6(ns, c: Checker):
    from agent.evals import load_traces
    c.require(ns, "evaluate")
    traces = load_traces(os.path.join(FIX_TRACES, "runA.json"))
    rep = ns["evaluate"](traces)

    c.check("success_rate correct",
            lambda: _assert(abs(rep["success_rate"] - 0.6) < 1e-9, rep))
    c.check("avg_steps correct",
            lambda: _assert(abs(rep["avg_steps"] - 4.0) < 1e-9, rep))
    c.check("failures categorised",
            lambda: _assert(rep["failures"] == {"max_steps_hit": 1, "tool_error": 1}, rep["failures"]))


def grade_7(ns, c: Checker):
    c.require(ns, "cap", "log_record")
    cap = ns["cap"]

    c.check("step cap fires first",
            lambda: _assert("max_steps" in (cap(5, 0.1, 5, 1.0) or ""), cap(5, 0.1, 5, 1.0)))
    c.check("cost cap fires",
            lambda: _assert("max_cost" in (cap(2, 1.0, 5, 1.0) or ""), cap(2, 1.0, 5, 1.0)))
    c.check("within caps -> None",
            lambda: _assert(cap(2, 0.1, 5, 1.0) is None, cap(2, 0.1, 5, 1.0)))

    def log_shape():
        rec = ns["log_record"](1, "llm_call", 0.01, 0.05)
        need = {"step", "action", "cost_usd", "cumulative_cost_usd", "ok"}
        assert need <= set(rec), f"missing keys: {need - set(rec)}"
    c.check("log_record has the right shape", log_shape)


def grade_8(ns, c: Checker):
    # Capstone is rubric-based; no PASS/FAIL.
    print("Assignment 8 is the capstone — rubric-based self-assessment, no autograde.\n")
    print("Rubric (aim for 4/6):")
    for item in [
        "1. Uses the loop (Agent/ToolAgent)",
        "2. At least one real Tool registered and called",
        "3. Uses some memory (working/episodic/semantic)",
        "4. Uses planning (ReAct or reflection) where it helps",
        "5. Has a step/cost cap and a guardrail",
        "6. Evaluated over >=3 tasks with a reported success rate",
    ]:
        print("  [ ]", item)
    # light structural nudge if they left a build() function:
    if callable(ns.get("build")):
        print("\n(Found a build() function — good. Run it with RUN_LIVE=1 to demo.)")


GRADERS = {1: grade_1, 2: grade_2, 3: grade_3, 4: grade_4,
           5: grade_5, 6: grade_6, 7: grade_7, 8: grade_8}


def main(argv: list[str]) -> int:
    if not argv or not argv[0].isdigit():
        raise SystemExit("usage: python grader/grade.py N [--solution]   (N = 1..8)")
    n = int(argv[0])
    solution = "--solution" in argv
    if n not in GRADERS:
        raise SystemExit(f"no such assignment: {n}")

    print(f"== Grading assignment {n}{' (solution)' if solution else ''} ==\n")
    ns = load_notebook(n, solution)

    if n == 8:
        grade_8(ns, Checker())
        return 0

    c = Checker()
    GRADERS[n](ns, c)
    passed = sum(1 for _, ok, _ in c.results if ok)
    total = len(c.results)
    for name, ok, detail in c.results:
        mark = "PASS" if ok else "FAIL"
        line = f"  [{mark}] {name}"
        if not ok and detail:
            line += f"  — {detail}"
        print(line)
    print(f"\nScore: {passed}/{total}  ({round(100 * passed / total) if total else 0}%)")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
