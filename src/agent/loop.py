"""The core agent loop + production hardening.

Implements: V1.1 (anatomy of the loop), V1.4 (the stopping problem),
V1.5 (the reusable Agent class) — and Module 7 hardening: V7.2 (cost+step caps),
V7.4 (structured per-step logging), V7.5 (guardrails on tool access).

Deterministic exercise targets (Module 7):
    EX7.1 enforce_caps, EX7.2 format_log_record, EX7.3 guardrail_check.

The whole course is, at heart, this one loop:

    observe -> decide -> act -> feed back -> stop

Everything later (tools, memory, planning, multi-agent, evals) hangs off it.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Any, Callable

from .llm import LLMResponse, complete

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

class CapExceeded(RuntimeError):
    """Raised/returned when an agent hits a cost or step cap."""


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


# Rough per-1K-token prices (USD); override via Agent(price_table=...).
DEFAULT_PRICES = {
    "prompt": 0.0005,
    "completion": 0.0015,
}


def estimate_cost(response: LLMResponse, prices: dict[str, float] = DEFAULT_PRICES) -> float:
    """Estimate the USD cost of one response from its usage, if reported."""
    usage = (response.raw or {}).get("usage", {})
    prompt = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
    completion = usage.get("completion_tokens") or usage.get("output_tokens") or 0
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


# --- The Agent (V1.5 + hardening) ----------------------------------------------

@dataclass
class Agent:
    """A minimal but reusable agent (V1.5), hardened for production (Module 7).

    Call :meth:`run` with a task string; it drives the observe/decide/act/stop
    loop and returns the model's final answer. With ``max_cost_usd`` and/or a
    ``logger`` it also enforces a cost cap and emits a structured log per step.
    """

    system_prompt: str = "You are a helpful agent. Reason step by step."
    max_steps: int = 6
    max_cost_usd: float | None = None
    stop: Callable[[LLMResponse, int, int], bool] = default_stop
    model: str | None = None
    on_step: Callable[[LLMResponse], str] | None = None
    logger: Callable[[dict[str, Any]], None] | None = None
    price_table: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_PRICES))
    # populated during run():
    history: list[dict[str, Any]] = field(default_factory=list)
    log: list[dict[str, Any]] = field(default_factory=list)
    cost_usd: float = 0.0
    stop_reason: str = ""

    def run(self, task: str) -> str:
        """Run the loop on ``task`` and return the final answer string."""
        self.history = [
            {"role": "system", "content": self.system_prompt},
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

            # caps (V7.2): cost cap can halt mid-loop; step cap handled by range + stop
            reason = enforce_caps(step, self.cost_usd, max_cost_usd=self.max_cost_usd)
            if reason:
                self.stop_reason = reason
                break

            # stop?
            if self.stop(last, step, self.max_steps):
                self.stop_reason = "stop_condition"
                break

            # act / feed back
            feedback = self.on_step(last) if self.on_step else "Continue."
            self.history.append({"role": "user", "content": feedback})
        else:
            self.stop_reason = "max_steps"

        return self._final_answer(last.text)

    def _emit(self, record: dict[str, Any]) -> None:
        self.log.append(record)
        if self.logger:
            self.logger(record)

    @staticmethod
    def _final_answer(text: str) -> str:
        if DONE_MARKER in text:
            return text.split(DONE_MARKER, 1)[1].strip()
        return text.strip()
