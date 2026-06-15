"""Smoke tests for Module 5 — multi-agent (deterministic, no network)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.multiagent import (  # noqa: E402
    Coordinator,
    DelegationCap,
    DelegationError,
    Message,
    Worker,
    route_message,
    synthesize_outputs,
)


def test_route_message_to_recipient():
    roles = {"writer": "W", "reviewer": "R"}
    msg = Message(sender="coord", recipient="reviewer", content="check this")
    assert route_message(msg, roles) == "R"


def test_route_message_unknown_recipient():
    try:
        route_message(Message("a", "ghost", "x"), {"writer": 1})
    except KeyError:
        return
    raise AssertionError("expected KeyError")


def test_delegation_cap_enter_and_block():
    cap = DelegationCap(max_depth=2)
    c1 = cap.enter()
    c2 = c1.enter()
    assert c2.depth == 2
    try:
        c2.enter()
    except DelegationError:
        return
    raise AssertionError("expected DelegationError at depth cap")


def test_synthesize_dedupes_and_orders():
    out = synthesize_outputs(["a", "b", "a", "", "  c "])
    assert out["parts"] == ["a", "b", "c"]
    assert out["count"] == 3
    assert out["combined"] == "a\nb\nc"


def test_coordinator_runs_with_injected_workers():
    # workers monkeypatched to avoid network
    w1 = Worker(name="research", system_prompt="research")
    w2 = Worker(name="write", system_prompt="write")
    w1.handle = lambda task: f"facts about {task}"
    w2.handle = lambda task: f"essay on {task}"
    coord = Coordinator(
        workers={"research": w1, "write": w2},
        cap=DelegationCap(max_depth=3),
        decompose=lambda task: [("research", task), ("write", task)],
    )
    out = coord.run("otters")
    assert len(out["results"]) == 2
    assert out["synthesis"]["count"] == 2
    assert "facts about otters" in out["synthesis"]["combined"]
