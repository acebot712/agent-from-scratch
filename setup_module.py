#!/usr/bin/env python3
"""Start-anywhere bootstrap for "Build an AI Agent From Scratch".

    python setup_module.py <N>          # set up to build module N (1..8)
    python setup_module.py <N> --reset  # discard your my_agent/ and rebuild
    python setup_module.py <N> --dest D  # write to D instead of ./my_agent

It creates a learner working copy `my_agent/` in which **modules 0..N-1 are
complete** and **module N's build targets are stubbed** (signature + docstring +
`raise NotImplementedError`), so you implement only module N. Lab and assignment
notebooks import from `my_agent/` (falling back to `src/` if it's absent).

How it stays honest with zero duplicated code: the git tag `module-N` already IS
the repo's complete state through module N (that's the linear-build path). So we
just materialise that tag's framework, then blank out the handful of symbols the
learner is meant to write. The list of those symbols — `BUILD_TARGETS` below — is
the only per-module config, and it doubles as documentation of what each module
asks you to build. `tests/test_setup_module.py` guards that every name here still
exists in its tag.
"""
from __future__ import annotations

import argparse
import ast
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))

# --- The only per-module config: what YOU implement in each module. ------------
# {N: {repo_path: [qualified symbol names]}}. Everything else in tag module-N is
# given complete (data shapes, the llm.py black box, the count_tokens proxy, ...).
BUILD_TARGETS: dict[int, dict[str, list[str]]] = {
    1: {"src/agent/loop.py": ["default_stop", "Agent.run", "Agent._final_answer"]},
    2: {"src/agent/tools.py": [
        "parse_tool_call", "dispatch", "tool", "Tool.to_schema", "ToolResult.as_observation",
        "ToolRegistry.register", "ToolRegistry.get", "ToolRegistry.names",
        "ToolRegistry.describe", "ToolRegistry.schemas"]},
    3: {"src/agent/memory.py": [  # count_tokens is the GIVEN proxy — left complete
        "context_budget_trim", "cosine_similarity", "top_k_retrieval",
        "WorkingMemory.add", "WorkingMemory.tokens", "WorkingMemory.window",
        "WorkingMemory.compress_overflow", "SemanticMemory.add", "SemanticMemory.retrieve",
        "EpisodicMemory.record", "EpisodicMemory.to_json", "EpisodicMemory.from_json",
        "EpisodicMemory.save", "EpisodicMemory.load"]},
    4: {"src/agent/planning.py": [
        "parse_react_trace", "extract_answer", "run_react", "_coerce_args", "_coerce_scalar",
        "RetryBudget.can_retry", "RetryBudget.consume", "RetryBudget.remaining",
        "reflect_and_retry", "tree_of_thoughts", "select_strategy"]},
    5: {"src/agent/multiagent.py": [
        "route_message", "DelegationCap.enter", "DelegationCap.allows",
        "Worker.handle", "synthesize_outputs", "Coordinator.run"]},
    6: {"src/agent/evals.py": [
        "exact_match", "contains", "success_rate", "step_efficiency", "cost_per_task",
        "summarize", "classify_failure", "failure_breakdown", "regression_diff",
        "load_traces", "run_eval", "replay_runner"]},
    7: {"src/agent/loop.py": ["enforce_caps", "format_log_record", "guardrail_check"]},
    8: {"examples/flagship_agent.py": ["build", "calculator", "kb_lookup"]},
}

# Which shipped fixtures each module needs staged into my_agent/fixtures/.
FIXTURES: dict[int, list[str]] = {3: ["embeddings"], 4: ["reflection"],
                                  5: ["multiagent", "embeddings"], 6: ["traces"]}

# The smoke test that exercises each module's build targets (module 1 is covered by
# test_module_0). Staged into my_agent/tests/ — rewired to import my_agent, so it
# actually checks the student's source (not the src/ reference).
TEST_FILE: dict[int, str] = {1: "test_module_0.py", **{n: f"test_module_{n}.py" for n in range(2, 9)}}

# Where to open next, per module.
NOTEBOOK_HINT = {
    1: "notebooks/lab_v1_3_clean.ipynb + assignments/assignment_1.ipynb",
    2: "notebooks/lab_v2_4_clean.ipynb + assignments/assignment_2.ipynb",
    3: "notebooks/lab_v3_4_clean.ipynb + assignments/assignment_3.ipynb",
    4: "notebooks/lab_v4_3_clean.ipynb + assignments/assignment_4.ipynb",
    5: "notebooks/lab_v5_6_clean.ipynb + assignments/assignment_5.ipynb",
    6: "notebooks/lab_v6_3_clean.ipynb + assignments/assignment_6.ipynb",
    7: "notebooks/lab_v7_2_clean.ipynb + assignments/assignment_7.ipynb",
    8: "assignments/capstone (assignment_8.ipynb) + examples/flagship_agent.py",
}


# --- git helpers (the tag is the source of truth) ------------------------------

def git(*args: str) -> str:
    out = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def tag_files(tag: str, *paths: str) -> list[str]:
    return [l for l in git("ls-tree", "-r", "--name-only", tag, *paths).splitlines() if l]


def tag_show(tag: str, path: str) -> str:
    return git("show", f"{tag}:{path}")


# --- the stubber: replace a function's body with `raise NotImplementedError` ----

def stub_source(src: str, symbols: list[str], module_n: int) -> str:
    """Blank the bodies of `symbols` in `src`, keeping signatures + docstrings.

    Pure text surgery guided by the AST, so every other line — comments,
    imports, dataclass fields, the parts from earlier modules — is preserved
    exactly. `symbols` are qualified names: "func" or "Class.method".
    """
    tree = ast.parse(src)
    wanted = set(symbols)
    edits = []  # (body_start_line, end_line, indent, qualname)

    def walk(node, prefix):
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = prefix + child.name
                if qn in wanted or child.name in wanted:
                    body = child.body
                    has_doc = (body and isinstance(body[0], ast.Expr)
                               and isinstance(body[0].value, ast.Constant)
                               and isinstance(body[0].value.value, str))
                    body_start = (body[0].end_lineno + 1) if has_doc else body[0].lineno
                    indent = " " * body[0].col_offset
                    edits.append((body_start, child.end_lineno, indent, qn))
            elif isinstance(child, ast.ClassDef):
                walk(child, prefix + child.name + ".")

    walk(tree, "")
    found = {qn for *_, qn in edits} | {qn.split(".")[-1] for *_, qn in edits}
    missing = [s for s in wanted if s not in found]
    if missing:
        raise ValueError(f"symbols not found to stub: {missing}")

    lines = src.split("\n")
    for body_start, end, indent, qn in sorted(edits, reverse=True):
        stub = f'{indent}raise NotImplementedError("Module {module_n}: implement {qn}")'
        lines[body_start - 1:end] = [stub]
    out = "\n".join(lines)
    ast.parse(out)  # never emit a file that won't import
    return out


# --- materialise my_agent/ -----------------------------------------------------

def dest_path(repo_rel: str) -> str:
    # src/agent/X -> agent/X ; examples/Y -> examples/Y
    if repo_rel.startswith("src/agent/"):
        return os.path.join("agent", repo_rel[len("src/agent/"):])
    return repo_rel


def build(n: int, dest: str) -> dict:
    tag = f"module-{n}"
    targets = BUILD_TARGETS[n]
    # 1. lay down the COMPLETE framework as of tag module-N (modules 0..N done)
    for f in tag_files(tag, "src/agent", "examples"):
        rel = dest_path(f)
        full = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(tag_show(tag, f))
    # 2. blank out module N's build targets so the learner writes them
    for path, symbols in targets.items():
        stubbed = stub_source(tag_show(tag, path), symbols, n)
        with open(os.path.join(dest, dest_path(path)), "w", encoding="utf-8") as fh:
            fh.write(stubbed)
    # 3. stage the fixtures this module needs
    staged = []
    for sub in FIXTURES.get(n, []):
        srcdir = os.path.join(REPO, "fixtures", sub)
        if os.path.isdir(srcdir):
            shutil.copytree(srcdir, os.path.join(dest, "fixtures", sub), dirs_exist_ok=True)
            staged.append(f"fixtures/{sub}")
    # 4. stage a smoke test rewired to import THIS my_agent (not the src/ reference),
    #    so `pytest` here actually checks what you wrote.
    tf = TEST_FILE[n]
    os.makedirs(os.path.join(dest, "tests"), exist_ok=True)
    test_src = tag_show(tag, f"tests/{tf}").replace('"..", "src"', '".."')
    with open(os.path.join(dest, "tests", tf), "w", encoding="utf-8") as fh:
        fh.write(test_src)
    return {"stubbed": targets, "fixtures": staged, "test": tf}


# --- verify + report -----------------------------------------------------------

def verify(dest: str) -> list[str]:
    ok = []
    ok.append(f"Python {sys.version_info.major}.{sys.version_info.minor} "
              + (">= 3.10 ✓" if sys.version_info >= (3, 10) else "✗ need >= 3.10"))
    try:
        import numpy  # noqa
        ok.append("numpy installed ✓")
    except ImportError:
        ok.append("numpy MISSING ✗  → pip install -r requirements.txt")
    env = os.path.join(REPO, ".env")
    has_key = os.path.exists(env) and "LLM_API_KEY=" in open(env).read() and \
        any(l.startswith("LLM_API_KEY=") and l.strip() != "LLM_API_KEY=" for l in open(env))
    ok.append("LLM_API_KEY set in .env ✓" if has_key
              else "LLM_API_KEY not set (only needed for the live cells) — cp .env.example .env")
    # my_agent imports cleanly (stubbed funcs raise only when CALLED, not on import)
    r = subprocess.run([sys.executable, "-c", "import agent; agent.__version__"],
                       capture_output=True, text=True, cwd=dest,
                       env={**os.environ, "PYTHONPATH": dest})
    ok.append("my_agent/agent imports cleanly ✓" if r.returncode == 0
              else f"my_agent import FAILED ✗\n    {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ''}")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="Start-anywhere setup for a single module.")
    ap.add_argument("module", type=int, help="module number to build (1..8)")
    ap.add_argument("--reset", action="store_true", help="discard an existing my_agent/ and rebuild")
    ap.add_argument("--dest", default=os.path.join(REPO, "my_agent"), help="output dir (default ./my_agent)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    if a.module not in BUILD_TARGETS:
        ap.error(f"module must be one of {sorted(BUILD_TARGETS)} (module 0 needs no setup — just run examples/hello_agent.py)")

    if os.path.exists(a.dest) and not a.reset:
        print(f"{a.dest} already exists. Keep working in it, or pass --reset to rebuild for module {a.module}.")
        return 1
    if os.path.exists(a.dest):
        shutil.rmtree(a.dest)

    info = build(a.module, a.dest)
    if a.quiet:
        return 0

    print(f"\n  Ready to build Module {a.module}.\n")
    print(f"  Working copy: {os.path.relpath(a.dest, os.getcwd())}/  (modules 0..{a.module-1} complete)")
    print("  You implement (everything else is done for you):")
    for path, syms in info["stubbed"].items():
        print(f"    {path}")
        for s in syms:
            print(f"      - {s}")
    if info["fixtures"]:
        print("  Fixtures staged: " + ", ".join(info["fixtures"]))
    print("\n  Checks:")
    for line in verify(a.dest):
        print("    " + line)
    rel = os.path.relpath(a.dest, os.getcwd())
    print(f"\n  Next: implement the stubbed functions above in {rel}/agent/, then verify:")
    print(f"    cd {rel} && python -m pytest tests/{info['test']}")
    print(f"  Prefer the guided walkthrough of the same module? Open "
          f"{NOTEBOOK_HINT[a.module]} (those build on the src/ reference).\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
