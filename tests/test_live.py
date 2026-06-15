"""Optional live end-to-end tests — require a real key.

These are SKIPPED unless RUN_LIVE=1 and LLM_API_KEY are set, so the offline
suite stays green. They prove the framework runs end-to-end against a provider.

    RUN_LIVE=1 LLM_PROVIDER=openai LLM_API_KEY=sk-... pytest tests/test_live.py
    RUN_LIVE=1 LLM_PROVIDER=openai LLM_API_KEY=sk-... python tests/run_all.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    import pytest  # noqa
    _skip = pytest.mark.skipif(
        os.environ.get("RUN_LIVE") != "1" or not os.environ.get("LLM_API_KEY"),
        reason="set RUN_LIVE=1 and LLM_API_KEY to run live tests",
    )
except ImportError:  # running under tests/run_all.py (name contains 'live' -> skipped there)
    def _skip(fn):
        return fn


@_skip
def test_live_agent_answers():
    from agent import Agent
    out = Agent(max_steps=4).run("What is 17 * 23? End with 'FINAL ANSWER: <number>'.")
    assert "391" in out


@_skip
def test_live_tool_agent_uses_tool():
    from agent import Tool, ToolAgent, ToolRegistry
    reg = ToolRegistry()
    reg.register(Tool(
        name="multiply", description="multiply two integers a and b",
        run=lambda a, b: int(a) * int(b),
        parameters={"type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
    ))
    out = ToolAgent(reg, max_steps=5).run("Use the multiply tool to compute 17 * 23.")
    assert "391" in out


@_skip
def test_live_embed_then_retrieve():
    from agent import SemanticMemory, embed  # noqa: F401
    mem = SemanticMemory()  # uses real embed()
    for fact in ["Cats are mammals.", "Python is a language.", "The sky is blue."]:
        mem.add(fact)
    hits = mem.retrieve("programming language", k=1)
    assert "Python" in hits[0]
