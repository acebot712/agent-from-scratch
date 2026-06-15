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


class ToolArgumentError(ToolError):
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


# --- A tool-using agent (wires the registry into the loop) ----------------------

TOOL_SYSTEM_PROMPT = """You are an agent that can call tools.

To call a tool, reply with exactly:
TOOL: <tool_name>
ARGS: {{"arg": "value"}}

Available tools:
{catalogue}

When you have the final answer and need no more tools, reply with:
FINAL ANSWER: <answer>
"""


class ToolAgent:
    """An agent that prompts for tools by hand, dispatches them, and loops.

    Deliberately mirrors :class:`agent.loop.Agent` but adds the tool turn:
    parse -> dispatch -> feed the observation back. This is the from-scratch
    version V2.6 maps onto native function calling.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        *,
        max_steps: int = 6,
        model: str | None = None,
        allow: list[str] | None = None,
        block: list[str] | None = None,
    ):
        self.registry = registry
        self.max_steps = max_steps
        self.model = model
        self.allow = allow  # guardrail allowlist (V7.5)
        self.block = block  # guardrail denylist
        self.history: list[dict[str, Any]] = []

    def run(self, task: str) -> str:
        from .llm import complete  # local import keeps module import order simple

        system = TOOL_SYSTEM_PROMPT.format(catalogue=self.registry.describe())
        self.history = [
            {"role": "system", "content": system},
            {"role": "user", "content": task},
        ]
        text = ""
        for _ in range(self.max_steps):
            text = complete(self.history, model=self.model).text
            self.history.append({"role": "assistant", "content": text})

            if "FINAL ANSWER:" in text:
                return text.split("FINAL ANSWER:", 1)[1].strip()

            call = parse_tool_call(text)
            if call is None:
                # No tool, no final answer — nudge it to decide.
                self.history.append({"role": "user", "content": "Call a tool or give FINAL ANSWER."})
                continue

            # Guardrail check before executing (V7.5).
            if self.allow is not None or self.block is not None:
                from .loop import guardrail_check
                ok, reason = guardrail_check(
                    call["name"], call.get("args"), allow=self.allow, block=self.block
                )
                if not ok:
                    self.history.append({"role": "user", "content": f"Observation: BLOCKED ({reason})"})
                    continue

            result = dispatch(self.registry, call)
            self.history.append({"role": "user", "content": f"Observation: {result.as_observation()}"})

        return text.strip()
