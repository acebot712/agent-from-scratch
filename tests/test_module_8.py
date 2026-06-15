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


def test_toolagent_is_the_same_hardened_agent_loop():
    # consolidation (V8.1): ToolAgent is an Agent, so caps/logging/guardrails apply
    from agent import Agent, ToolAgent
    assert issubclass(ToolAgent, Agent)


def test_unified_loop_drives_tools_logs_and_stops_offline():
    # exercise the REAL loop offline by scripting the model (no network/key)
    import agent.loop as loop
    from agent import Tool, ToolRegistry, ToolAgent
    from agent.llm import LLMResponse

    reg = ToolRegistry()
    reg.register(Tool("calc", "eval arithmetic; arg: expression",
                      run=lambda expression: str(eval(expression, {"__builtins__": {}}, {})),
                      parameters={"type": "object", "properties": {"expression": {"type": "string"}}}))

    # scripted "model": first asks for the tool, then gives the final answer
    scripted = iter([
        'TOOL: calc\nARGS: {"expression": "6*7"}',
        "FINAL ANSWER: 42",
    ])
    real = loop.complete
    loop.complete = lambda messages, model=None: LLMResponse(text=next(scripted))
    try:
        a = ToolAgent(reg, max_steps=5)
        answer = a.run("what is 6*7?")
    finally:
        loop.complete = real

    assert answer == "42"
    # the tool actually ran and was logged on the same hardened loop
    assert any("Observation: calc -> 42" in m["content"] for m in a.history)
    assert any(r["action"] == "tool:calc" for r in a.log)


def test_minimal_agent_parses_and_dispatches_offline():
    # the single-file canonical agent: its parsing + dispatch work with no key
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "examples"))
    import minimal_agent as m
    call = m.parse_call('TOOL: calculator ARGS: {"expression": "6*7"}')
    assert call == {"name": "calculator", "args": {"expression": "6*7"}}
    assert m.run_tool(call) == "42"
    assert "unknown tool" in m.run_tool({"name": "ghost", "args": {}})


def test_unified_loop_guardrail_blocks_tool_offline():
    import agent.loop as loop
    from agent import Tool, ToolRegistry, ToolAgent
    from agent.llm import LLMResponse

    reg = ToolRegistry()
    reg.register(Tool("shell", "run shell", run=lambda cmd: "ran",
                      parameters={"type": "object", "properties": {"cmd": {"type": "string"}}}))
    scripted = iter(['TOOL: shell\nARGS: {"cmd": "rm -rf /"}', "FINAL ANSWER: done"])
    real = loop.complete
    loop.complete = lambda messages, model=None: LLMResponse(text=next(scripted))
    try:
        a = ToolAgent(reg, max_steps=4, block=["shell"])
        a.run("delete everything")
    finally:
        loop.complete = real
    assert any("BLOCKED" in m["content"] for m in a.history)


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
