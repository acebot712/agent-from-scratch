"""Multi-agent systems.

Implements Module 5: V5.2 (coordinator/worker), V5.3 (message passing), V5.4
(delegation cap), V5.5 (role design), V5.6 (synthesizing worker outputs).

Deterministic exercise targets:
    EX5.1 route_message, EX5.2 delegation_cap, EX5.3 synthesize_outputs
    (the mechanical merge — combine/dedupe/order).

A multi-agent system is just several agent loops that pass each other messages.
The two things that make it *safe* are a delegation cap (so it can't recurse
forever) and a deterministic merge (so results are reproducible).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


# --- Messages (V5.3 / EX5.1) ---------------------------------------------------

@dataclass
class Message:
    """A structured message routed between agents."""

    sender: str
    recipient: str
    content: str
    meta: dict[str, Any] = field(default_factory=dict)


def route_message(message: Message, roles: dict[str, Any]) -> Any:
    """Route a message to its recipient role; raise if no such role (EX5.1).

    ``roles`` maps role name -> handler (an agent, a worker, anything). Routing
    is deterministic: by the message's ``recipient`` field.
    """
    if message.recipient not in roles:
        raise KeyError(f"no agent registered for role '{message.recipient}'")
    return roles[message.recipient]


# --- Delegation cap (V5.4 / EX5.2) ---------------------------------------------

class DelegationError(RuntimeError):
    """Raised when delegation would exceed the configured depth cap."""


@dataclass
class DelegationCap:
    """Enforce a delegation-depth cap to prevent runaway loops (EX5.2)."""

    max_depth: int
    depth: int = 0

    def enter(self) -> "DelegationCap":
        """Descend one level; raise :class:`DelegationError` past the cap."""
        if self.depth >= self.max_depth:
            raise DelegationError(f"delegation depth cap ({self.max_depth}) exceeded")
        return DelegationCap(max_depth=self.max_depth, depth=self.depth + 1)

    def allows(self) -> bool:
        return self.depth < self.max_depth


# --- Roles (V5.5) --------------------------------------------------------------

@dataclass
class Worker:
    """A role-specialised agent defined by its system prompt (V5.5)."""

    name: str
    system_prompt: str
    model: str | None = None

    def handle(self, task: str) -> str:
        from .llm import complete

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]
        return complete(messages, model=self.model).text.strip()


# --- Synthesis (V5.6 / EX5.3) --------------------------------------------------

def synthesize_outputs(outputs: list[str], *, dedupe: bool = True) -> dict[str, Any]:
    """Mechanically merge worker outputs into one structured result (EX5.3).

    This is the **deterministic** merge: trim, drop blanks, optionally dedupe
    (order-preserving), and return a stable combined string + the parts. The
    LLM-written synthesis is a separate, ungraded path.
    """
    parts: list[str] = []
    seen: set[str] = set()
    for o in outputs:
        o = (o or "").strip()
        if not o:
            continue
        if dedupe and o in seen:
            continue
        seen.add(o)
        parts.append(o)
    return {"parts": parts, "combined": "\n".join(parts), "count": len(parts)}


# --- Coordinator/worker (V5.2) -------------------------------------------------

@dataclass
class Coordinator:
    """Decompose a task, delegate to workers, and synthesize results (V5.2).

    ``decompose`` splits a task into subtasks (an LLM call in practice; injected
    so the structure is testable offline). ``cap`` bounds delegation depth.
    """

    workers: dict[str, Worker]
    cap: DelegationCap = field(default_factory=lambda: DelegationCap(max_depth=3))
    decompose: Callable[[str], list[tuple[str, str]]] | None = None

    def run(self, task: str) -> dict[str, Any]:
        """Return ``{"subtasks", "results", "synthesis"}`` for ``task``."""
        cap = self.cap.enter()  # delegating one level down
        subtasks = self.decompose(task) if self.decompose else [(name, task) for name in self.workers]

        results: list[dict[str, str]] = []
        for role, subtask in subtasks:
            if role not in self.workers:
                raise KeyError(f"no worker for role '{role}'")
            if not cap.allows():
                raise DelegationError("delegation cap reached during dispatch")
            output = self.workers[role].handle(subtask)
            results.append({"role": role, "subtask": subtask, "output": output})

        synthesis = synthesize_outputs([r["output"] for r in results])
        return {"subtasks": subtasks, "results": results, "synthesis": synthesis}
