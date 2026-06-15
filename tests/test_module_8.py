"""Smoke tests for Module 8 — the consolidated public API (no network)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import agent  # noqa: E402


def test_public_api_is_complete():
    # one representative symbol from every module must be importable from the top
    expected = [
        "Agent", "complete", "embed",                  # loop + llm
        "Tool", "ToolRegistry", "ToolAgent",           # tools
        "SemanticMemory", "cosine_similarity",         # memory
        "run_react", "reflect_and_retry",              # planning
        "Coordinator", "synthesize_outputs",           # multi-agent
        "run_eval", "regression_diff",                 # evals
        "enforce_caps", "guardrail_check",             # hardening
    ]
    for name in expected:
        assert hasattr(agent, name), f"missing public export: {name}"
        assert name in agent.__all__, f"not in __all__: {name}"


def test_version_is_consolidated():
    assert agent.__version__ == "1.0.0"


def test_flagship_example_builds_offline():
    # the capstone example must at least import and assemble without a key
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
    import flagship_agent
    a = flagship_agent.build()
    assert "calculator" in a.registry.names()
    assert "kb_lookup" in a.registry.names()
    assert a.block == ["shell"]
    # the kb lookup tool works fully offline
    assert "Mercury" in flagship_agent.kb_lookup("closest planet")
