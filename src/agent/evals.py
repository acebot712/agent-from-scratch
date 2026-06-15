"""Evaluating agents.

Implements Module 6: V6.2 (success predicate), V6.3 (eval harness), V6.4
(metrics: success rate, steps, cost), V6.5 (failure taxonomy), V6.6 (regression
diff).

Deterministic exercise targets:
    EX6.1 success_rate, EX6.2 step_efficiency, EX6.3 cost_per_task,
    EX6.4 classify_failure (rule-based), EX6.5 regression_diff.

This module runs on **recorded trace fixtures** (see ``fixtures/traces/``), so it
works even if the learner never built the earlier agents — Module 6 is the one
independently-runnable module.

Trace schema (one run):
    {
      "task_id": str,
      "success": bool,
      "steps": int,
      "max_steps": int,
      "cost_usd": float,
      "final_answer": str | null,
      "tool_errors": int,
      "stop_reason": "final_answer" | "max_steps" | "error",
    }
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Iterable


# --- Success predicate (V6.2) --------------------------------------------------

def exact_match(expected: str) -> Callable[[dict[str, Any]], bool]:
    """A success predicate: trace is successful iff final_answer == expected."""
    def predicate(trace: dict[str, Any]) -> bool:
        return (trace.get("final_answer") or "").strip() == expected.strip()
    return predicate


def contains(expected: str) -> Callable[[dict[str, Any]], bool]:
    """A success predicate: final_answer contains ``expected`` (case-insensitive)."""
    def predicate(trace: dict[str, Any]) -> bool:
        return expected.strip().lower() in (trace.get("final_answer") or "").lower()
    return predicate


# --- Metrics (V6.4 / EX6.1-6.3) ------------------------------------------------

def success_rate(traces: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool] | None = None) -> float:
    """Fraction of traces that succeeded (EX6.1).

    If a ``predicate`` is given it is applied; otherwise the trace's own
    ``success`` field is used.
    """
    if not traces:
        return 0.0
    if predicate is None:
        wins = sum(1 for t in traces if t.get("success"))
    else:
        wins = sum(1 for t in traces if predicate(t))
    return wins / len(traces)


def step_efficiency(traces: list[dict[str, Any]]) -> float:
    """Average steps used by **successful** traces (EX6.2).

    Lower is better. Returns 0.0 if there are no successful traces.
    """
    wins = [t for t in traces if t.get("success")]
    if not wins:
        return 0.0
    return sum(t.get("steps", 0) for t in wins) / len(wins)


def cost_per_task(traces: list[dict[str, Any]]) -> float:
    """Average cost in USD across all traces (EX6.3)."""
    if not traces:
        return 0.0
    return sum(float(t.get("cost_usd", 0.0)) for t in traces) / len(traces)


def summarize(traces: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool] | None = None) -> dict[str, Any]:
    """Roll up the three headline metrics for a run."""
    return {
        "n": len(traces),
        "success_rate": success_rate(traces, predicate),
        "step_efficiency": step_efficiency(traces),
        "cost_per_task": cost_per_task(traces),
    }


# --- Failure taxonomy (V6.5 / EX6.4) -------------------------------------------

# Rule-based categories, in priority order.
FAILURE_CATEGORIES = ("max_steps_hit", "tool_error", "no_final_answer", "wrong_answer")


def classify_failure(trace: dict[str, Any], predicate: Callable[[dict[str, Any]], bool] | None = None) -> str | None:
    """Classify a failed run into a failure category from its trace (EX6.4).

    Rule-based (not LLM-judged). Returns ``None`` if the run actually succeeded.
    """
    succeeded = predicate(trace) if predicate else bool(trace.get("success"))
    if succeeded:
        return None
    if trace.get("stop_reason") == "max_steps" or trace.get("steps", 0) >= trace.get("max_steps", float("inf")):
        return "max_steps_hit"
    if trace.get("tool_errors", 0) > 0 or trace.get("stop_reason") == "error":
        return "tool_error"
    if not trace.get("final_answer"):
        return "no_final_answer"
    return "wrong_answer"


def failure_breakdown(traces: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool] | None = None) -> dict[str, int]:
    """Count failures per category across a run."""
    counts: dict[str, int] = {}
    for t in traces:
        cat = classify_failure(t, predicate)
        if cat is not None:
            counts[cat] = counts.get(cat, 0) + 1
    return counts


# --- Regression detection (V6.6 / EX6.5) ---------------------------------------

def regression_diff(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    """Diff two eval runs to detect regressions (EX6.5).

    Matches traces by ``task_id`` and reports tasks that went success->fail
    (regressions) and fail->success (fixes), plus the success-rate delta.
    """
    before_ok = {t["task_id"]: bool(t.get("success")) for t in before}
    after_ok = {t["task_id"]: bool(t.get("success")) for t in after}
    common = before_ok.keys() & after_ok.keys()

    regressions = sorted(tid for tid in common if before_ok[tid] and not after_ok[tid])
    fixes = sorted(tid for tid in common if not before_ok[tid] and after_ok[tid])
    return {
        "regressions": regressions,
        "fixes": fixes,
        "success_rate_before": success_rate(before),
        "success_rate_after": success_rate(after),
        "delta": success_rate(after) - success_rate(before),
        "regressed": len(regressions) > 0,
    }


# --- Eval harness (V6.3) -------------------------------------------------------

def load_traces(path: str) -> list[dict[str, Any]]:
    """Load a list of trace dicts from a JSON file (a shipped fixture)."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data["traces"] if isinstance(data, dict) and "traces" in data else data


def run_eval(
    tasks: Iterable[dict[str, Any]],
    runner: Callable[[dict[str, Any]], dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Run ``runner`` over a task set and collect results into a report (V6.3).

    ``runner(task) -> trace``. Works with a live agent or a fixture replayer.
    """
    traces = [runner(task) for task in tasks]
    report = summarize(traces, predicate)
    report["failures"] = failure_breakdown(traces, predicate)
    report["traces"] = traces
    return report


def replay_runner(fixtures_dir: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """A runner that 'runs' a task by loading its recorded trace (offline V6.3)."""
    def runner(task: dict[str, Any]) -> dict[str, Any]:
        path = os.path.join(fixtures_dir, f"{task['task_id']}.json")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return runner
