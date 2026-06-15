"""Smoke tests for Module 2 — tools (deterministic, no network)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.tools import (  # noqa: E402
    Tool,
    ToolRegistry,
    UnknownToolError,
    dispatch,
    parse_tool_call,
)


def _registry():
    reg = ToolRegistry()
    reg.register(Tool(name="add", description="add two ints",
                      run=lambda a, b: a + b,
                      parameters={"type": "object",
                                  "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}}))
    return reg


def test_parse_tool_call_lines():
    call = parse_tool_call('TOOL: add\nARGS: {"a": 2, "b": 3}')
    assert call == {"name": "add", "args": {"a": 2, "b": 3}}


def test_parse_tool_call_fenced_json():
    call = parse_tool_call('```json\n{"name": "add", "args": {"a": 1, "b": 1}}\n```')
    assert call["name"] == "add" and call["args"] == {"a": 1, "b": 1}


def test_parse_tool_call_none_when_no_request():
    assert parse_tool_call("The answer is 5.") is None


def test_dispatch_runs_tool():
    res = dispatch(_registry(), {"name": "add", "args": {"a": 2, "b": 3}})
    assert res.ok and res.output == 5


def test_dispatch_unknown_tool_is_graceful():
    res = dispatch(_registry(), {"name": "subtract", "args": {}})
    assert res.ok is False and "unknown tool" in res.error


def test_dispatch_bad_args_is_graceful():
    res = dispatch(_registry(), {"name": "add", "args": {"a": 1}})
    assert res.ok is False and "bad arguments" in res.error


def test_registry_rejects_unknown_get():
    try:
        _registry().get("nope")
    except UnknownToolError:
        return
    raise AssertionError("expected UnknownToolError")
