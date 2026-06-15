"""agent-from-scratch — a ~600-800 line agent framework you build yourself.

Public API (finalised in module-8). At module-0/1 it is intentionally tiny:
the LLM wrapper and the core loop.
"""

from .llm import LLMResponse, ToolCall, complete, embed
from .loop import DONE_MARKER, Agent, default_stop

__all__ = [
    "Agent",
    "default_stop",
    "DONE_MARKER",
    "complete",
    "embed",
    "LLMResponse",
    "ToolCall",
]

__version__ = "0.0.0"  # bumped per module tag
