"""Tool use from scratch.

Implements Module 2: V2.2 (clean tool interface), V2.3/V2.4 (manual tool
requests + parsing), V2.5 (registry + dispatch), V2.6 (native function calling
mapping), V2.7 (hallucinated / malformed tool handling).

Deterministic exercise targets live here too:
    EX2.1 parse_tool_call, EX2.2 ToolRegistry, EX2.3 dispatch (unknown tool).

The big idea (V2.1): the model can't run code. "Tool use" is just the model
*asking* for a call in text; *we* run it and feed the result back into the loop.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable


# --- The tool interface (V2.2) -------------------------------------------------

@dataclass
class Tool:
    """A consistent tool signature: name, description, args schema, run().

    ``parameters`` is a JSON-schema-ish dict describing the arguments; it is
    what we hand to a native function-calling API (V2.6) and what we show the
    model when prompting by hand (V2.3).
    """

    name: str
    description: str
    run: Callable[..., Any]
    parameters: dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})

    def to_schema(self) -> dict[str, Any]:
        """Render as a provider tool schema (the shape ``llm.complete`` wants)."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


def tool(name: str, description: str, parameters: dict[str, Any] | None = None):
    """Decorator sugar: turn a plain function into a :class:`Tool`."""

    def wrap(fn: Callable[..., Any]) -> Tool:
        return Tool(
            name=name,
            description=description,
            run=fn,
            parameters=parameters or {"type": "object", "properties": {}},
        )

    return wrap


# --- Errors (V2.7) -------------------------------------------------------------

class ToolError(Exception):
    """Base class for tool problems we want to feed back to the model."""


class UnknownToolError(ToolError):
    pass


# --- Registry + dispatch (V2.5) ------------------------------------------------

@dataclass
class ToolRegistry:
    """Register tools and dispatch a parsed call to the right one (EX2.2)."""

    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, t: Tool) -> Tool:
        if t.name in self._tools:
            raise ValueError(f"tool already registered: {t.name}")
        self._tools[t.name] = t
        return t

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise UnknownToolError(name)
        return self._tools[name]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def schemas(self) -> list[dict[str, Any]]:
        """All tool schemas, for passing to native function calling (V2.6)."""
        return [t.to_schema() for t in self._tools.values()]

    def describe(self) -> str:
        """Human-readable catalogue, for hand-rolled tool prompting (V2.3)."""
        lines = []
        for t in self._tools.values():
            props = (t.parameters or {}).get("properties", {})
            args = ", ".join(props) or "(none)"
            lines.append(f"- {t.name}({args}): {t.description}")
        return "\n".join(lines)


# --- Parsing a tool request from free text (V2.3 / V2.4 / EX2.1) ---------------

# We teach two shapes. The "by hand" prompt asks the model to emit:
#     TOOL: <name>
#     ARGS: {"json": "object"}
# We also accept a bare ```json {"tool"/"name": ..., "args": ...} ``` fenced block,
# because that's what models tend to drift toward.

_TOOL_LINE = re.compile(r"TOOL:\s*([A-Za-z0-9_\-]+)", re.IGNORECASE)
_ARGS_LINE = re.compile(r"ARGS:\s*(\{.*?\})\s*$", re.IGNORECASE | re.DOTALL)
_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def parse_tool_call(text: str) -> dict[str, Any] | None:
    """Parse a tool request into ``{"name": str, "args": dict}`` (EX2.1).

    Returns ``None`` when the text contains no tool request at all (the model
    is answering directly, not calling a tool). Raises nothing — malformed JSON
    degrades to an empty/raw args dict so the caller (dispatch) decides policy.
    """
    if not text:
        return None

    # Shape 1: TOOL:/ARGS: lines.
    m_name = _TOOL_LINE.search(text)
    if m_name:
        name = m_name.group(1)
        m_args = _ARGS_LINE.search(text)
        args = _safe_json(m_args.group(1)) if m_args else {}
        return {"name": name, "args": args}

    # Shape 2: a fenced JSON object naming the tool.
    m_fence = _FENCE.search(text)
    if m_fence:
        obj = _safe_json(m_fence.group(1))
        name = obj.get("name") or obj.get("tool")
        if name:
            args = obj.get("args") or obj.get("arguments") or {}
            if not isinstance(args, dict):
                args = {"_raw": args}
            return {"name": name, "args": args}

    return None


def _safe_json(s: str) -> dict[str, Any]:
    try:
        out = json.loads(s)
        return out if isinstance(out, dict) else {"_raw": out}
    except (json.JSONDecodeError, TypeError):
        return {"_malformed": s}


# --- Dispatch (V2.5 + V2.7 / EX2.3) --------------------------------------------

@dataclass
class ToolResult:
    """Outcome of a dispatch: either ``ok`` with output, or an error string."""

    name: str
    ok: bool
    output: Any = None
    error: str | None = None

    def as_observation(self) -> str:
        """Render for feeding back into the loop as an Observation."""
        if self.ok:
            return f"{self.name} -> {self.output}"
        return f"{self.name} ERROR: {self.error}"


def dispatch(registry: ToolRegistry, call: dict[str, Any] | None) -> ToolResult:
    """Run a parsed call against the registry, handling failures gracefully.

    Hallucinated tools (V2.7) and malformed args never raise out of here — they
    come back as a :class:`ToolResult` with ``ok=False`` so the agent can tell
    the model what went wrong and let it recover.
    """
    if not call or "name" not in call:
        return ToolResult(name="<none>", ok=False, error="no tool call found")

    name = call["name"]
    args = call.get("args") or {}

    if name not in registry:
        return ToolResult(
            name=name,
            ok=False,
            error=f"unknown tool '{name}'. available: {registry.names()}",
        )

    if "_malformed" in args:
        return ToolResult(name=name, ok=False, error=f"malformed arguments: {args['_malformed']}")

    tool_obj = registry.get(name)
    try:
        output = tool_obj.run(**args)
    except TypeError as exc:  # wrong/missing kwargs
        return ToolResult(name=name, ok=False, error=f"bad arguments: {exc}")
    except Exception as exc:  # tool blew up at runtime
        return ToolResult(name=name, ok=False, error=f"{type(exc).__name__}: {exc}")
    return ToolResult(name=name, ok=True, output=output)


# The tool-using agent lives in loop.py: tools plug into the ONE hardened agent
# loop (caps, logging, guardrails) rather than a parallel loop. See agent.loop.Agent
# (tools=...) and the ToolAgent convenience wrapper.
