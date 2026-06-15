"""Smoke tests for Module 4 — planning (deterministic, no network)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.planning import (  # noqa: E402
    RetryBudget,
    _coerce_args,
    extract_answer,
    parse_react_trace,
    reflect_and_retry,
    select_strategy,
    tree_of_thoughts,
)
from agent.tools import Tool  # noqa: E402


def _calc():
    return Tool("calc", "eval arithmetic", run=lambda expression: expression,
                parameters={"type": "object", "properties": {"expression": {"type": "string"}}})


def _add():
    return Tool("add", "add a,b", run=lambda a, b: a + b,
                parameters={"type": "object",
                            "properties": {"a": {"type": "number"}, "b": {"type": "number"}}})


def test_react_args_use_real_param_name_not_x():
    # regression: a tool whose single arg is NOT named 'x' must still get its value
    assert _coerce_args("2+2", _calc()) == {"expression": "2+2"}


def test_react_args_positional_multi_arg():
    assert _coerce_args("2, 3", _add()) == {"a": 2, "b": 3}


def test_react_args_key_value():
    assert _coerce_args("a=10, b=5", _add()) == {"a": 10, "b": 5}


def test_react_args_json_object():
    assert _coerce_args('{"a": 1, "b": 2}', _add()) == {"a": 1, "b": 2}


def test_parse_react_trace():
    text = (
        "Thought: I should add.\n"
        "Action: add[2, 3]\n"
        "Observation: 5\n"
        "Thought: done.\n"
        "Answer: 5"
    )
    steps = parse_react_trace(text)
    assert steps[0].action == "add"
    assert steps[0].action_input == "2, 3"
    assert steps[0].observation == "5"
    assert extract_answer(text) == "5"


def test_retry_budget():
    b = RetryBudget(max_retries=2)
    assert b.consume() and b.consume()
    assert not b.consume()
    assert b.remaining == 0


def test_reflect_and_retry_succeeds_within_budget():
    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        return calls["n"]  # returns 1, then 2, then 3...

    rec = reflect_and_retry(attempt, is_good=lambda r: r >= 3,
                            critique=lambda r: f"too small: {r}", max_retries=5)
    assert rec["success"] is True
    assert rec["retries_used"] == 2
    assert len(rec["critiques"]) == 2


def test_reflect_and_retry_respects_cap():
    rec = reflect_and_retry(lambda: 0, is_good=lambda r: r == 1,
                            critique=lambda r: "nope", max_retries=2)
    assert rec["success"] is False
    assert rec["retries_used"] == 2


def test_tree_of_thoughts_picks_best():
    best = tree_of_thoughts(propose=lambda: [1, 9, 4], score=lambda x: x, keep=1)
    assert best == [9]


def test_tree_of_thoughts_beam_expansion():
    # depth-2 beam: seeds 1,2; expand multiplies; best leaf should win
    best = tree_of_thoughts(
        propose=lambda: [1, 2],
        expand=lambda n: [n * 10, n * 3],
        score=lambda x: x,
        keep=1, beam_width=2, depth=2,
    )
    assert best == [20]  # 2 -> 20 beats 1 -> 10


def test_select_strategy_rules():
    assert select_strategy({"needs_tools": True}) == "react"
    assert select_strategy({"verifiable": True, "difficulty": "hard"}) == "reflection"
    assert select_strategy({"open_ended": True}) == "tot"
    assert select_strategy({}) == "direct"
