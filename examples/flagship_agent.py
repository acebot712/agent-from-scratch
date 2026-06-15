"""Flagship agent — the capstone build on the consolidated framework (V8.3).

A small research assistant that ties the whole framework together:
  * tools        — a calculator + a (fixed) knowledge-base lookup
  * memory       — semantic retrieval injects relevant facts into the prompt
  * planning     — ReAct interleaves reasoning with tool calls
  * hardening    — step cap + structured logging + a guardrail denylist

Run it:
    LLM_PROVIDER=openai LLM_API_KEY=sk-... python examples/flagship_agent.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import (  # noqa: E402
    SemanticMemory,
    Tool,
    ToolAgent,
    ToolRegistry,
)

# --- knowledge base (fixed vectors so the demo needs no embedding key) ---------
FACTS = {
    "Mercury is the closest planet to the Sun.": [1.0, 0.0, 0.0],
    "Water boils at 100 degrees Celsius at sea level.": [0.0, 1.0, 0.0],
    "The mitochondrion is the powerhouse of the cell.": [0.0, 0.0, 1.0],
}
kb = SemanticMemory(embedder=lambda ts: [[1.0, 0.0, 0.0]] * len(ts))  # demo embedder
for fact, vec in FACTS.items():
    kb.add(fact, vector=vec)


# --- tools --------------------------------------------------------------------
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression."""
    return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307 (demo only)


def kb_lookup(query: str) -> str:
    """Return the most relevant known fact."""
    hits = kb.retrieve(query, k=1, query_vector=[1.0, 0.0, 0.0])
    return hits[0] if hits else "no fact found"


def build() -> ToolAgent:
    registry = ToolRegistry()
    registry.register(Tool(
        name="calculator", description="evaluate arithmetic, arg: expression",
        run=calculator,
        parameters={"type": "object", "properties": {"expression": {"type": "string"}}},
    ))
    registry.register(Tool(
        name="kb_lookup", description="look up a fact, arg: query",
        run=kb_lookup,
        parameters={"type": "object", "properties": {"query": {"type": "string"}}},
    ))
    # guardrail: never let the model call a tool named 'shell'
    return ToolAgent(registry, max_steps=6, block=["shell"])


if __name__ == "__main__":
    agent = build()
    print(agent.run("What is 12 * 9, and which planet is closest to the Sun?"))
