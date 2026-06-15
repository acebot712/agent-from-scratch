"""Smoke tests for Module 7 — production hardening (deterministic, no network)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.loop import (  # noqa: E402
    enforce_caps,
    format_log_record,
    guardrail_check,
)


def test_enforce_caps_step():
    assert enforce_caps(5, 0.0, max_steps=5) == "max_steps (5) reached"
    assert enforce_caps(4, 0.0, max_steps=5) is None


def test_enforce_caps_cost():
    assert enforce_caps(1, 0.51, max_cost_usd=0.50).startswith("max_cost")
    assert enforce_caps(1, 0.10, max_cost_usd=0.50) is None


def test_enforce_caps_no_caps_set():
    assert enforce_caps(99, 99.0) is None


def test_format_log_record_shape():
    rec = format_log_record(2, action="llm_call", detail="hello", cost_usd=0.001,
                            cumulative_cost_usd=0.003, tokens=120)
    assert set(rec) == {"step", "action", "detail", "cost_usd",
                        "cumulative_cost_usd", "tokens", "ok"}
    assert rec["step"] == 2 and rec["ok"] is True


def test_guardrail_denylist_wins():
    ok, reason = guardrail_check("rm", {}, block=["rm"], allow=["rm"])
    assert ok is False and "denylist" in reason


def test_guardrail_allowlist():
    assert guardrail_check("search", {}, allow=["search", "calc"])[0] is True
    assert guardrail_check("delete", {}, allow=["search", "calc"])[0] is False


def test_guardrail_pattern_block():
    ok, reason = guardrail_check("shell", {"cmd": "sudo rm -rf /"}, patterns=["*rm -rf*"])
    assert ok is False and "pattern" in reason


def test_guardrail_default_allow():
    assert guardrail_check("anything")[0] is True
