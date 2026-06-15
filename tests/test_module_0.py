"""Smoke tests for the module-0 seed — no network required.

These check the wiring (imports, response normalisation, stopping condition)
without calling a live model.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import Agent, LLMResponse, default_stop  # noqa: E402
from agent.loop import DONE_MARKER  # noqa: E402


def test_public_api_imports():
    assert callable(Agent)
    assert Agent().max_steps == 6


def test_stop_on_done_marker():
    resp = LLMResponse(text=f"{DONE_MARKER} 391")
    assert default_stop(resp, step=1, max_steps=6) is True


def test_stop_on_step_cap():
    resp = LLMResponse(text="still thinking")
    assert default_stop(resp, step=6, max_steps=6) is True


def test_does_not_stop_midway():
    resp = LLMResponse(text="thinking", stop_reason=None)
    assert default_stop(resp, step=1, max_steps=6) is False


def test_final_answer_extraction():
    assert Agent._final_answer(f"work...\n{DONE_MARKER} 42") == "42"
