"""Memory architectures.

Implements Module 3: V3.1 (three memories), V3.2 (context budget), V3.3
(summarization on overflow), V3.4 (cosine in numpy), V3.5 (top-k retrieval),
V3.6 (persistence across sessions).

Deterministic exercise targets:
    EX3.1 cosine_similarity, EX3.2 top_k_retrieval, EX3.3 context_budget_trim,
    EX3.4 episodic_serialize.

The three memories (V3.1):
  * working   — the live message window (bounded by a token budget).
  * episodic  — a log of past events/turns, persisted across sessions.
  * semantic  — facts/documents retrievable by similarity (uses ``embed()``).
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

import numpy as np


# --- Token budget proxy (V3.2 / EX3.3) -----------------------------------------

def count_tokens(text: str) -> int:
    """A tokenizer-free token proxy: ~1 token per whitespace word.

    Real tokenizers aren't deterministic across versions and pull in heavy deps;
    for budgeting and for the offline coding exercise a word count is plenty.
    """
    return len(text.split())


def context_budget_trim(
    messages: list[dict[str, Any]],
    budget: int,
    counter: Callable[[str], int] = count_tokens,
    *,
    keep_system: bool = True,
) -> list[dict[str, Any]]:
    """Drop the oldest messages until the history fits ``budget`` tokens (EX3.3).

    The system message (if first and ``keep_system``) is always retained; the
    most recent messages are preferred over older ones.
    """
    if budget <= 0:
        return []

    system: list[dict[str, Any]] = []
    rest = list(messages)
    if keep_system and rest and rest[0].get("role") == "system":
        system = [rest.pop(0)]

    sys_cost = sum(counter(m.get("content", "")) for m in system)
    remaining = budget - sys_cost
    kept_reversed: list[dict[str, Any]] = []
    for m in reversed(rest):
        cost = counter(m.get("content", ""))
        if cost <= remaining:
            kept_reversed.append(m)
            remaining -= cost
        else:
            break
    return system + list(reversed(kept_reversed))


# --- Working memory ------------------------------------------------------------

@dataclass
class WorkingMemory:
    """The live message window, kept under a token budget (V3.2/V3.3)."""

    budget: int = 2000
    counter: Callable[[str], int] = count_tokens
    messages: list[dict[str, Any]] = field(default_factory=list)
    summary: str | None = None  # running compression of overflow (V3.3)

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def tokens(self) -> int:
        return sum(self.counter(m.get("content", "")) for m in self.messages)

    def window(self) -> list[dict[str, Any]]:
        """Return the messages trimmed to budget (prepending any summary)."""
        msgs = list(self.messages)
        if self.summary:
            msgs = [{"role": "system", "content": f"Summary so far: {self.summary}"}] + msgs
        return context_budget_trim(msgs, self.budget, self.counter)

    def compress_overflow(self, summarizer: Callable[[list[dict[str, Any]]], str]) -> None:
        """When over budget, fold the oldest turns into ``summary`` (V3.3).

        ``summarizer`` is injected (an LLM call in practice) so this stays
        testable offline.
        """
        if self.tokens() <= self.budget:
            return
        kept = context_budget_trim(self.messages, self.budget, self.counter, keep_system=False)
        overflow = self.messages[: len(self.messages) - len(kept)]
        if overflow:
            new = summarizer(overflow)
            self.summary = f"{self.summary}\n{new}".strip() if self.summary else new
            self.messages = kept


# --- Similarity + retrieval (V3.4 / V3.5 / EX3.1 / EX3.2) -----------------------

def cosine_similarity(a, b) -> float:
    """Cosine similarity between two vectors, from scratch in numpy (EX3.1)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def top_k_retrieval(query_vec, doc_vecs, k: int = 3) -> list[tuple[int, float]]:
    """Rank doc vectors by cosine similarity to the query; return top-k (EX3.2).

    Input is **precomputed embedding vectors**, not text. Returns a list of
    ``(index, score)`` sorted by score descending.
    """
    scored = [(i, cosine_similarity(query_vec, v)) for i, v in enumerate(doc_vecs)]
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[: max(0, k)]


# --- Semantic memory -----------------------------------------------------------

@dataclass
class SemanticMemory:
    """Documents retrievable by embedding similarity (V3.5).

    Embeddings are taken as given via an injected ``embedder`` (defaults to
    :func:`agent.llm.embed`), keeping the math here pure-numpy and testable.
    """

    embedder: Callable[[list[str]], list[list[float]]] | None = None
    docs: list[str] = field(default_factory=list)
    vectors: list[list[float]] = field(default_factory=list)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        if self.embedder is not None:
            return self.embedder(texts)
        from .llm import embed  # lazy import: avoid needing a key at import time
        return embed(texts)

    def add(self, text: str, vector: list[float] | None = None) -> None:
        self.docs.append(text)
        self.vectors.append(vector if vector is not None else self._embed([text])[0])

    def retrieve(self, query: str, k: int = 3, query_vector: list[float] | None = None) -> list[str]:
        """Return the top-k most similar documents to ``query``."""
        if not self.vectors:
            return []
        qv = query_vector if query_vector is not None else self._embed([query])[0]
        ranked = top_k_retrieval(qv, self.vectors, k)
        return [self.docs[i] for i, _ in ranked]


# --- Episodic memory + persistence (V3.6 / EX3.4) ------------------------------

@dataclass
class Episode:
    role: str
    content: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class EpisodicMemory:
    """An append-only log of episodes that survives across sessions (V3.6)."""

    episodes: list[Episode] = field(default_factory=list)

    def record(self, role: str, content: str, **meta: Any) -> None:
        self.episodes.append(Episode(role=role, content=content, meta=meta))

    def to_json(self) -> str:
        """Serialise to a JSON string (EX3.4)."""
        return json.dumps([asdict(e) for e in self.episodes], indent=2)

    @classmethod
    def from_json(cls, blob: str) -> "EpisodicMemory":
        data = json.loads(blob) if blob.strip() else []
        return cls(episodes=[Episode(**d) for d in data])

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_json())

    @classmethod
    def load(cls, path: str) -> "EpisodicMemory":
        if not os.path.exists(path):
            return cls()
        with open(path, encoding="utf-8") as fh:
            return cls.from_json(fh.read())
