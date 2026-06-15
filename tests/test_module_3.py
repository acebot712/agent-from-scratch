"""Smoke tests for Module 3 — memory (deterministic, no network)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.memory import (  # noqa: E402
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory,
    context_budget_trim,
    cosine_similarity,
    count_tokens,
    top_k_retrieval,
)


def test_cosine_basic():
    assert cosine_similarity([1, 0], [1, 0]) == 1.0
    assert cosine_similarity([1, 0], [0, 1]) == 0.0
    assert cosine_similarity([0, 0], [1, 1]) == 0.0  # zero vector guard


def test_top_k_orders_by_similarity():
    q = [1.0, 0.0]
    docs = [[0.0, 1.0], [1.0, 0.1], [0.9, 0.0]]
    ranked = top_k_retrieval(q, docs, k=2)
    assert [i for i, _ in ranked] == [2, 1]


def test_context_budget_trim_keeps_recent_and_system():
    msgs = [
        {"role": "system", "content": "sys here"},
        {"role": "user", "content": "one two three four"},
        {"role": "assistant", "content": "five six"},
        {"role": "user", "content": "seven"},
    ]
    trimmed = context_budget_trim(msgs, budget=5, counter=count_tokens)
    assert trimmed[0]["role"] == "system"
    assert trimmed[-1]["content"] == "seven"
    assert sum(count_tokens(m["content"]) for m in trimmed) <= 5


def test_working_memory_compress_overflow():
    wm = WorkingMemory(budget=4)
    for i in range(6):
        wm.add("user", f"message number {i}")
    wm.compress_overflow(summarizer=lambda msgs: f"compressed {len(msgs)} msgs")
    assert wm.summary is not None
    assert wm.tokens() <= wm.budget


def test_semantic_retrieve_with_injected_embedder():
    # fixed embeddings so no network is needed
    table = {"cats": [1.0, 0.0], "dogs": [0.9, 0.1], "stocks": [0.0, 1.0]}
    mem = SemanticMemory(embedder=lambda ts: [table[t] for t in ts])
    for word in ("cats", "dogs", "stocks"):
        mem.add(word)
    got = mem.retrieve("cats", k=2, query_vector=[1.0, 0.0])
    assert got == ["cats", "dogs"]


def test_episodic_roundtrip_persistence():
    mem = EpisodicMemory()
    mem.record("user", "hello", step=1)
    mem.record("assistant", "hi", step=2)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "mem.json")
        mem.save(path)
        again = EpisodicMemory.load(path)
    assert len(again.episodes) == 2
    assert again.episodes[0].content == "hello"
    assert again.episodes[1].meta["step"] == 2
