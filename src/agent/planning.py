"""Planning & reasoning.

Implements Module 4: V4.2/V4.3 (ReAct), V4.4 (reflection/retry), V4.5 (a taste
of tree-of-thoughts), V4.6 (strategy selection).

Deterministic exercise targets:
    EX4.1 parse_react_trace, EX4.2 retry_budget, EX4.3 select_strategy.

ReAct (V4.2) interleaves reasoning and acting:
    Thought: ... / Action: tool[args] / Observation: ... (repeat) / Answer: ...
The tool actions are exactly the Module-2 tool calls — planning sits on top of
tools, which is why this module depends on M2.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from .tools import Tool, ToolRegistry, dispatch


# --- Parsing a ReAct trace (V4.3 / EX4.1) --------------------------------------

@dataclass
class ReactStep:
    thought: str | None = None
    action: str | None = None
    action_input: str | None = None
    observation: str | None = None


_THOUGHT = re.compile(r"Thought:\s*(.+)")
_ACTION = re.compile(r"Action:\s*([A-Za-z0-9_\-]+)\s*(?:\[(.*?)\]|\((.*?)\))?", re.DOTALL)
_OBS = re.compile(r"Observation:\s*(.+)")
_ANSWER = re.compile(r"(?:Final\s+)?Answer:\s*(.+)", re.IGNORECASE | re.DOTALL)


def parse_react_trace(text: str) -> list[ReactStep]:
    """Parse Thought/Action/Observation lines into structured steps (EX4.1).

    Tolerant of missing pieces — a step may have only a Thought, or a Thought +
    Action with no Observation yet (the model is mid-turn).
    """
    steps: list[ReactStep] = []
    current = ReactStep()
    have = False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _THOUGHT.match(line)
        if m:
            if have and (current.thought or current.action):
                steps.append(current)
                current = ReactStep()
            current.thought = m.group(1).strip()
            have = True
            continue
        m = _ACTION.match(line)
        if m:
            current.action = m.group(1).strip()
            current.action_input = (m.group(2) or m.group(3) or "").strip() or None
            have = True
            continue
        m = _OBS.match(line)
        if m:
            current.observation = m.group(1).strip()
            steps.append(current)
            current = ReactStep()
            have = False
            continue
    if have and (current.thought or current.action):
        steps.append(current)
    return steps


def extract_answer(text: str) -> str | None:
    """Return the final answer from a ReAct trace if present."""
    m = _ANSWER.search(text)
    return m.group(1).strip() if m else None


REACT_SYSTEM_PROMPT = """Solve the task by reasoning step by step in this format:

Thought: <your reasoning>
Action: <tool_name>[<argument>]
Observation: <filled in for you>
... (repeat Thought/Action/Observation as needed)
Answer: <final answer>

Available tools:
{catalogue}

Only emit ONE Thought/Action per turn, then wait for the Observation.
"""


def run_react(task: str, registry: ToolRegistry, *, max_steps: int = 6, model: str | None = None) -> str:
    """Implement and drive a ReAct loop from scratch (V4.3).

    Single-argument tools are assumed for the from-scratch version (the action
    input is passed positionally), which keeps the parser simple.
    """
    from .llm import complete

    catalogue = registry.describe()
    history = [
        {"role": "system", "content": REACT_SYSTEM_PROMPT.format(catalogue=catalogue)},
        {"role": "user", "content": task},
    ]
    for _ in range(max_steps):
        text = complete(history, model=model).text
        history.append({"role": "assistant", "content": text})

        answer = extract_answer(text)
        if answer is not None:
            return answer

        steps = parse_react_trace(text)
        if steps and steps[-1].action:
            step = steps[-1]
            tool = registry.get(step.action) if step.action in registry else None
            args = _coerce_args(step.action_input, tool)
            result = dispatch(registry, {"name": step.action, "args": args})
            history.append({"role": "user", "content": f"Observation: {result.as_observation()}"})
        else:
            history.append({"role": "user", "content": "Continue with Thought/Action or give Answer:."})
    return extract_answer(history[-1]["content"]) or history[-1]["content"]


def _coerce_scalar(value: str) -> Any:
    """Turn an action-input token into an int/float when it looks numeric."""
    v = value.strip().strip('"').strip("'")
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            continue
    return v


def _coerce_args(raw: str | None, tool: "Tool | None") -> dict[str, Any]:
    """Map a ReAct action input onto a tool's actual parameters.

    Handles three shapes the model commonly emits, in order:
      * a JSON object         -> used directly        ``{"a": 1, "b": 2}``
      * ``key=value`` pairs   -> parsed into kwargs    ``a=1, b=2``
      * positional value(s)   -> zipped onto the tool's declared parameters
                                 (``add[2, 3]`` -> ``{"a": 2, "b": 3}``)

    The parameter *names* come from the tool's own schema, so a tool can declare
    any argument names it likes — there is no hidden ``x`` convention.
    """
    raw = (raw or "").strip()
    if not raw:
        return {}

    if raw.startswith("{"):  # JSON object
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if parts and all("=" in p for p in parts):  # key=value pairs
        out = {}
        for p in parts:
            k, _, v = p.partition("=")
            out[k.strip()] = _coerce_scalar(v)
        return out

    # positional: zip onto the tool's declared parameter names
    props = list((tool.parameters or {}).get("properties", {})) if tool else []
    if not props:
        return {"input": _coerce_scalar(raw)} if len(parts) <= 1 else {"input": raw}
    if len(props) == 1:
        return {props[0]: _coerce_scalar(raw)}
    return {name: _coerce_scalar(val) for name, val in zip(props, parts)}


# --- Reflection: critique and retry (V4.4 / EX4.2) -----------------------------

@dataclass
class RetryBudget:
    """A bounded retry counter (the deterministic core of reflection, EX4.2)."""

    max_retries: int
    used: int = 0

    def can_retry(self) -> bool:
        return self.used < self.max_retries

    def consume(self) -> bool:
        """Use one retry; return True if it was available."""
        if not self.can_retry():
            return False
        self.used += 1
        return True

    @property
    def remaining(self) -> int:
        return max(0, self.max_retries - self.used)


def reflect_and_retry(
    attempt: Callable[[], Any],
    is_good: Callable[[Any], bool],
    critique: Callable[[Any], str],
    *,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Run ``attempt``; if the result fails ``is_good``, critique and retry (V4.4).

    Stays within ``max_retries``. Returns a record with the final result, whether
    it succeeded, how many retries were used, and the critiques produced — the
    structural properties the grader checks.
    """
    budget = RetryBudget(max_retries)
    critiques: list[str] = []
    result = attempt()
    while not is_good(result) and budget.consume():
        critiques.append(critique(result))
        result = attempt()
    return {
        "result": result,
        "success": is_good(result),
        "retries_used": budget.used,
        "critiques": critiques,
    }


# --- A taste of tree-of-thoughts (V4.5) ----------------------------------------

def tree_of_thoughts(
    propose: Callable[[], list[Any]],
    score: Callable[[Any], float],
    *,
    expand: Callable[[Any], list[Any]] | None = None,
    keep: int = 1,
    beam_width: int = 3,
    depth: int = 1,
) -> list[Any]:
    """Explore multiple candidate paths and select the best (V4.5).

    Beam search over a tree of partial solutions:
      * ``propose()`` seeds the frontier with candidate thoughts/paths.
      * ``score(c)`` rates a candidate (higher = better).
      * ``expand(c)`` (optional) grows a candidate one step into successors.

    With no ``expand`` (``depth=1``) this is the one-level version: propose,
    score, keep the top-N. With ``expand`` and ``depth>1`` it keeps the best
    ``beam_width`` each level and expands them — real lookahead, not one shot.
    """
    frontier = list(propose())
    if expand is not None:
        for _ in range(max(0, depth - 1)):
            best = sorted(frontier, key=score, reverse=True)[:beam_width]
            grown = [child for node in best for child in expand(node)]
            frontier = grown or best  # stop growing if a level is a dead end
    ranked = sorted(frontier, key=score, reverse=True)
    return ranked[: max(1, keep)]


# --- Strategy selection (V4.6 / EX4.3) -----------------------------------------

def select_strategy(task_meta: dict[str, Any]) -> str:
    """Pick a reasoning strategy from task metadata, rule-based (EX4.3).

    Returns one of: ``"direct"``, ``"react"``, ``"reflection"``, ``"tot"``.
    """
    if task_meta.get("needs_tools"):
        return "react"
    if task_meta.get("verifiable") and task_meta.get("difficulty") == "hard":
        return "reflection"
    if task_meta.get("open_ended") or task_meta.get("branching"):
        return "tot"
    return "direct"
