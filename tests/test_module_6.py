"""Smoke tests for Module 6 — evals (deterministic, runs on shipped fixtures)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.evals import (  # noqa: E402
    classify_failure,
    cost_per_task,
    failure_breakdown,
    load_traces,
    regression_diff,
    replay_runner,
    run_eval,
    step_efficiency,
    success_rate,
)

FIX = os.path.join(os.path.dirname(__file__), "..", "fixtures", "traces")


def test_metrics_on_fixture():
    traces = load_traces(os.path.join(FIX, "runA.json"))
    assert success_rate(traces) == 3 / 5
    # successful traces use 3,5,4 steps -> mean 4.0
    assert step_efficiency(traces) == 4.0
    assert abs(cost_per_task(traces) - (0.012 + 0.021 + 0.040 + 0.008 + 0.018) / 5) < 1e-9


def test_classify_failure_rules():
    traces = {t["task_id"]: t for t in load_traces(os.path.join(FIX, "runA.json"))}
    assert classify_failure(traces["t1"]) is None          # succeeded
    assert classify_failure(traces["t3"]) == "max_steps_hit"
    assert classify_failure(traces["t4"]) == "tool_error"   # stop_reason == error


def test_failure_breakdown():
    traces = load_traces(os.path.join(FIX, "runA.json"))
    bd = failure_breakdown(traces)
    assert bd == {"max_steps_hit": 1, "tool_error": 1}


def test_regression_diff_between_runs():
    a = load_traces(os.path.join(FIX, "runA.json"))
    b = load_traces(os.path.join(FIX, "runB.json"))
    diff = regression_diff(a, b)
    assert diff["regressions"] == ["t2"]
    assert diff["fixes"] == ["t3"]
    assert diff["regressed"] is True


def test_run_eval_with_replay_runner():
    tasks = [{"task_id": f"t{i}"} for i in range(1, 6)]
    report = run_eval(tasks, replay_runner(FIX))
    assert report["n"] == 5
    assert report["success_rate"] == 3 / 5
