"""agent-from-scratch — a ~600-800 line agent framework you build yourself.

Public API. It grows one module at a time and is consolidated/cleaned in
module-8 (see V8.1). Importing :mod:`agent` should give you everything the
course has built so far.
"""

from .llm import LLMResponse, ToolCall, complete, embed
from .loop import DONE_MARKER, Agent, default_stop
from .tools import (
    Tool,
    ToolAgent,
    ToolArgumentError,
    ToolRegistry,
    ToolResult,
    UnknownToolError,
    dispatch,
    parse_tool_call,
    tool,
)
from .memory import (
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory,
    context_budget_trim,
    cosine_similarity,
    count_tokens,
    top_k_retrieval,
)

__all__ = [
    # llm
    "complete",
    "embed",
    "LLMResponse",
    "ToolCall",
    # loop
    "Agent",
    "default_stop",
    "DONE_MARKER",
    # tools
    "Tool",
    "tool",
    "ToolRegistry",
    "ToolResult",
    "ToolAgent",
    "dispatch",
    "parse_tool_call",
    "UnknownToolError",
    "ToolArgumentError",
    # memory
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "cosine_similarity",
    "top_k_retrieval",
    "context_budget_trim",
    "count_tokens",
]

__version__ = "0.3.0"  # module-3
