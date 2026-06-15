"""The core agent loop.

Implements: V1.1 (anatomy of the loop), V1.4 (the stopping problem),
V1.5 (the reusable Agent class).

The whole course is, at heart, this one loop:

    observe -> decide -> act -> feed back -> stop

Everything later (tools, memory, planning, multi-agent, evals) hangs off it.
This module ships the minimal, readable version; later modules extend it.
"""

from __future__ import annotations

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


@dataclass
class Agent:
    """A minimal but reusable agent (V1.5).

    Call :meth:`run` with a task string; it drives the observe/decide/act/stop
    loop and returns the model's final answer.
    """

    system_prompt: str = "You are a helpful agent. Reason step by step."
    max_steps: int = 6
    stop: Callable[[LLMResponse, int, int], bool] = default_stop
    model: str | None = None
    # Hook for later modules: given a response, produce the next user message
    # (e.g. tool results). Default just nudges the model to continue.
    on_step: Callable[[LLMResponse], str] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def run(self, task: str) -> str:
        """Run the loop on ``task`` and return the final answer string."""
        self.history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]

        last = LLMResponse(text="")
        for step in range(1, self.max_steps + 1):
            # decide
            last = complete(self.history, model=self.model)
            self.history.append({"role": "assistant", "content": last.text})

            # stop?
            if self.stop(last, step, self.max_steps):
                break

            # act / feed back
            feedback = self.on_step(last) if self.on_step else "Continue."
            self.history.append({"role": "user", "content": feedback})

        return self._final_answer(last.text)

    @staticmethod
    def _final_answer(text: str) -> str:
        if DONE_MARKER in text:
            return text.split(DONE_MARKER, 1)[1].strip()
        return text.strip()
