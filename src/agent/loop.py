"""The core agent loop + production hardening.

Implements: V1.1 (anatomy of the loop), V1.4 (the stopping problem),
V1.5 (the reusable Agent class) — Module 7 hardening: V7.2 (cost+step caps),
V7.4 (structured per-step logging), V7.5 (guardrails on tool access) — and the
Module 8 consolidation (V8.1): tools plug into this ONE loop instead of a
parallel one, so the agent you actually deploy (with tools) is the same hardened
loop you tested.

Deterministic exercise targets (Module 7):
    EX7.1 enforce_caps, EX7.2 format_log_record, EX7.3 guardrail_check.

The whole course is, at heart, this one loop:

    observe -> decide -> act -> feed back -> stop
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Any, Callable

from .llm import LLMResponse, complete
from .tools import ToolRegistry, dispatch, parse_tool_call

# Sentinel the model emits when it considers the task done. V1.4: a terminal-state
# check needs *something* concrete to test for — this is the simplest such signal.
DONE_MARKER = "FINAL ANSWER:"


def default_stop(response: LLMResponse, step: int, max_steps: int) -> bool:
    """Terminal-state check (V1.4).

    The loop ends when either:
      * the model signals completion (emits ``DONE_MARKER`` or stops naturally
        without requesting a tool), or
      * we hit the step cap (a safety net so the loop can never run forever).
    """
    if step >= max_steps:
        return True
    if DONE_MARKER in response.text:
        return True
    if response.stop_reason in ("stop", "end_turn") and not response.tool_calls:
        return True
    return False


# --- Production hardening: caps (V7.2 / EX7.1) ----------------------------------

def enforce_caps(
    steps: int,
    cost_usd: float,
    *,
    max_steps: int | None = None,
    max_cost_usd: float | None = None,
) -> str | None:
    """Return a halt reason if a cap is exceeded, else ``None`` (EX7.1).

    Pure and deterministic so it can be unit-tested without an agent. The loop
    calls this each iteration and halts on a non-None result.
    """
    if max_steps is not None and steps >= max_steps:
        return f"max_steps ({max_steps}) reached"
    if max_cost_usd is not None and cost_usd >= max_cost_usd:
        return f"max_cost (${max_cost_usd}) reached"
    return None


# Per-1K-token prices (USD) by model substring. These are real, public list
# prices at time of writing — verify against your provider and override as needed.
# Each entry is (prompt_per_1k, completion_per_1k).
MODEL_PRICES = {
    "gpt-4o-mini":     (0.00015, 0.00060),
    "gpt-4o":          (0.00250, 0.01000),
    "claude-haiku":    (0.00080, 0.00400),
    "claude-sonnet":   (0.00300, 0.01500),
    "claude-opus":     (0.01500, 0.07500),
}
# Fallback when the model is unknown; conservative mid-range estimate.
DEFAULT_PRICES = {"prompt": 0.0005, "completion": 0.0015}


def _prices_for(model: str) -> dict[str, float]:
    for key, (p, c) in MODEL_PRICES.items():
        if key in (model or ""):
            return {"prompt": p, "completion": c}
    return DEFAULT_PRICES


def estimate_cost(response: LLMResponse, prices: dict[str, float] | None = None) -> float:
    """Estimate the USD cost of one response from its reported token usage.

    If ``prices`` is given it is used directly; otherwise prices are looked up
    from the response's model name (:data:`MODEL_PRICES`), falling back to
    :data:`DEFAULT_PRICES`. It's an *estimate* — providers and tiers vary, so
    treat the cost cap as a guardrail, not a billing source of truth.
    """
    usage = (response.raw or {}).get("usage", {})
    prompt = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
    completion = usage.get("completion_tokens") or usage.get("output_tokens") or 0
    if prices is None:
        prices = _prices_for((response.raw or {}).get("model", ""))
    return (prompt / 1000) * prices["prompt"] + (completion / 1000) * prices["completion"]


# --- Production hardening: structured logging (V7.4 / EX7.2) --------------------

def format_log_record(
    step: int,
    *,
    action: str,
    detail: str = "",
    cost_usd: float = 0.0,
    cumulative_cost_usd: float = 0.0,
    tokens: int = 0,
    ok: bool = True,
) -> dict[str, Any]:
    """Emit one structured log record per agent step (EX7.2).

    A flat, JSON-serialisable dict with a stable schema — the thing you'd ship to
    a log aggregator. Graded on shape, not content.
    """
    return {
        "step": step,
        "action": action,
        "detail": detail,
        "cost_usd": round(cost_usd, 6),
        "cumulative_cost_usd": round(cumulative_cost_usd, 6),
        "tokens": tokens,
        "ok": ok,
    }


# --- Production hardening: guardrails (V7.5 / EX7.3) ----------------------------

def guardrail_check(
    tool_name: str,
    args: dict[str, Any] | None = None,
    *,
    allow: list[str] | None = None,
    block: list[str] | None = None,
    patterns: list[str] | None = None,
) -> tuple[bool, str]:
    """Apply an allow/block rule to a tool call before executing it (EX7.3).

    Rule-based (not an LLM classifier). Precedence:
      1. explicit ``block`` (denylist) wins,
      2. then ``allow`` (allowlist) — if set, the tool must be on it,
      3. then ``patterns`` matched against ``"tool_name: arg values"`` block.
    Returns ``(allowed, reason)``.
    """
    if block and tool_name in block:
        return False, f"'{tool_name}' is on the denylist"
    if allow is not None and tool_name not in allow:
        return False, f"'{tool_name}' is not on the allowlist"
    if patterns:
        haystack = f"{tool_name}: " + " ".join(str(v) for v in (args or {}).values())
        for pat in patterns:
            if fnmatch.fnmatch(haystack, pat):
                return False, f"matched blocked pattern '{pat}'"
    return True, "allowed"


# --- Tool prompting -------------------------------------------------------------

TOOL_INSTRUCTIONS = """

You can call tools. To call one, reply with exactly:
TOOL: <tool_name>
ARGS: {{"arg": "value"}}

Available tools:
{catalogue}

When you have the final answer and need no more tools, reply with:
FINAL ANSWER: <answer>"""


# --- The Agent (V1.5 + hardening + tools, one loop) -----------------------------

@dataclass
class Agent:
    """The reusable agent (V1.5), hardened for production (Module 7) and able to
    use tools (Module 2) — all in **one** loop (consolidated in Module 8).

    Pass ``tools=<ToolRegistry>`` to give the agent tools: each step, a tool
    request in the model's reply is guardrail-checked, dispatched, and the
    observation fed back. Without ``tools`` it's the plain reason-and-answer
    loop. Either way it enforces the step/cost caps and emits a structured log.
    """

    system_prompt: str = "You are a helpful agent. Reason step by step."
    max_steps: int = 6
    max_cost_usd: float | None = None
    stop: Callable[[LLMResponse, int, int], bool] = default_stop
    model: str | None = None
    tools: ToolRegistry | None = None
    allow: list[str] | None = None   # guardrail allowlist (V7.5)
    block: list[str] | None = None   # guardrail denylist
    on_step: Callable[[LLMResponse], str] | None = None
    logger: Callable[[dict[str, Any]], None] | None = None
    price_table: dict[str, float] | None = None  # None -> price by model name
    # populated during run():
    history: list[dict[str, Any]] = field(default_factory=list)
    log: list[dict[str, Any]] = field(default_factory=list)
    cost_usd: float = 0.0
    stop_reason: str = ""

    def _system(self) -> str:
        """Effective system prompt — appends the tool catalogue when tools exist."""
        if self.tools is None:
            return self.system_prompt
        return self.system_prompt + TOOL_INSTRUCTIONS.format(catalogue=self.tools.describe())

    def run(self, task: str) -> str:
        """Run the loop on ``task`` and return the final answer string."""
        self.history = [
            {"role": "system", "content": self._system()},
            {"role": "user", "content": task},
        ]
        self.log = []
        self.cost_usd = 0.0
        self.stop_reason = ""

        last = LLMResponse(text="")
        for step in range(1, self.max_steps + 1):
            # decide
            last = complete(self.history, model=self.model)
            self.history.append({"role": "assistant", "content": last.text})

            # account + log
            step_cost = estimate_cost(last, self.price_table)
            self.cost_usd += step_cost
            self._emit(format_log_record(
                step, action="llm_call", detail=last.text[:80],
                cost_usd=step_cost, cumulative_cost_usd=self.cost_usd,
            ))

            # cost cap can halt mid-loop (V7.2); the step cap is the for-range bound
            reason = enforce_caps(step, self.cost_usd, max_cost_usd=self.max_cost_usd)
            if reason:
                self.stop_reason = reason
                break

            # done? (default_stop already checks the DONE_MARKER; a custom stop is
            # fully in control — no hidden marker override)
            if self.stop(last, step, self.max_steps):
                self.stop_reason = "stop_condition"
                break

            # act / feed back
            if self.tools is not None:
                self._take_tool_turn(last, step)
            else:
                feedback = self.on_step(last) if self.on_step else "Continue."
                self.history.append({"role": "user", "content": feedback})
        else:
            self.stop_reason = "max_steps"

        return self._final_answer(last.text)

    def _take_tool_turn(self, response: LLMResponse, step: int) -> None:
        """Parse a tool request, guardrail-check it, dispatch, feed back (V2.5/V7.5)."""
        call = parse_tool_call(response.text)
        if call is None:
            self.history.append({"role": "user", "content": "Call a tool or give FINAL ANSWER."})
            return
        if self.allow is not None or self.block is not None:
            ok, why = guardrail_check(call["name"], call.get("args"), allow=self.allow, block=self.block)
            if not ok:
                self._emit(format_log_record(step, action="tool_blocked", detail=call["name"],
                                             cumulative_cost_usd=self.cost_usd, ok=False))
                self.history.append({"role": "user", "content": f"Observation: BLOCKED ({why})"})
                return
        result = dispatch(self.tools, call)
        self._emit(format_log_record(step, action=f"tool:{call['name']}", detail=str(result.output)[:80],
                                     cumulative_cost_usd=self.cost_usd, ok=result.ok))
        self.history.append({"role": "user", "content": f"Observation: {result.as_observation()}"})

    def _emit(self, record: dict[str, Any]) -> None:
        self.log.append(record)
        if self.logger:
            self.logger(record)

    @staticmethod
    def _final_answer(text: str) -> str:
        if DONE_MARKER in text:
            return text.split(DONE_MARKER, 1)[1].strip()
        return text.strip()


class ToolAgent(Agent):
    """Convenience wrapper: an :class:`Agent` pre-wired with a tool registry.

    ``ToolAgent(registry, block=["shell"])`` is exactly ``Agent(tools=registry,
    block=["shell"], ...)`` with a tool-oriented system prompt. It is the *same*
    hardened loop — caps, logging, and guardrails all apply.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        *,
        max_steps: int = 6,
        model: str | None = None,
        allow: list[str] | None = None,
        block: list[str] | None = None,
        max_cost_usd: float | None = None,
        logger: Callable[[dict[str, Any]], None] | None = None,
    ):
        super().__init__(
            system_prompt="You are an agent that can call tools.",
            max_steps=max_steps,
            model=model,
            tools=registry,
            allow=allow,
            block=block,
            max_cost_usd=max_cost_usd,
            logger=logger,
        )

    @property
    def registry(self) -> ToolRegistry:
        return self.tools
