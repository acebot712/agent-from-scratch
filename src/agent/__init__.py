"""agent-from-scratch — a complete, readable agent framework in pure Python.

This is the consolidated public API (V8.1). Everything the course builds is
re-exported here, so ``from agent import ...`` is the one import you need.

The whole framework, by module:

    M1  loop.py        Agent + the observe/decide/act/feed-back/stop loop
    M2  tools.py       Tool, ToolRegistry, parse_tool_call, dispatch, ToolAgent
    M3  memory.py      working / episodic / semantic memory + retrieval
    M4  planning.py    ReAct, reflection/retry, tree-of-thoughts, strategy
    M5  multiagent.py  Coordinator/Worker, routing, delegation cap, synthesis
    M6  evals.py       metrics, failure taxonomy, regression diff, harness
    M7  loop.py        caps, structured logging, guardrails (hardening)

Framework-equivalence map (V8.4) — what our piece is called elsewhere:

    ours                     LangChain            CrewAI / AutoGen
    ----                     ---------            ----------------
    Agent / run loop         AgentExecutor        Agent / ConversableAgent
    Tool / ToolRegistry      Tool / @tool         tool / function
    SemanticMemory           VectorStoreRetriever Knowledge / RAG
    Coordinator/Worker       (LCEL chains)        Crew / GroupChat
    run_eval / metrics       LangSmith evals      (custom)
    enforce_caps/guardrails  callbacks/limits     max_round / guardrails
"""

# --- M1: the loop + M7: hardening ---------------------------------------------
from .loop import (
    DONE_MARKER,
    Agent,
    ToolAgent,
    default_stop,
    enforce_caps,
    estimate_cost,
    format_log_record,
    guardrail_check,
)

# --- the LLM wrapper ----------------------------------------------------------
from .llm import LLMResponse, ToolCall, complete, embed

# --- M2: tools ----------------------------------------------------------------
from .tools import (
    Tool,
    ToolRegistry,
    ToolResult,
    UnknownToolError,
    dispatch,
    parse_tool_call,
    tool,
)

# --- M3: memory ---------------------------------------------------------------
from .memory import (
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory,
    context_budget_trim,
    cosine_similarity,
    count_tokens,
    top_k_retrieval,
)

# --- M4: planning -------------------------------------------------------------
from .planning import (
    RetryBudget,
    extract_answer,
    parse_react_trace,
    reflect_and_retry,
    run_react,
    select_strategy,
    tree_of_thoughts,
)

# --- M5: multi-agent ----------------------------------------------------------
from .multiagent import (
    Coordinator,
    DelegationCap,
    DelegationError,
    Message,
    Worker,
    route_message,
    synthesize_outputs,
)

# --- M6: evals ----------------------------------------------------------------
from .evals import (
    classify_failure,
    contains,
    cost_per_task,
    exact_match,
    failure_breakdown,
    load_traces,
    regression_diff,
    replay_runner,
    run_eval,
    step_efficiency,
    success_rate,
    summarize,
)

__all__ = [
    # llm
    "complete", "embed", "LLMResponse", "ToolCall",
    # loop + hardening
    "Agent", "default_stop", "DONE_MARKER",
    "enforce_caps", "format_log_record", "guardrail_check", "estimate_cost",
    # tools
    "Tool", "tool", "ToolRegistry", "ToolResult", "ToolAgent",
    "dispatch", "parse_tool_call", "UnknownToolError",
    # memory
    "WorkingMemory", "EpisodicMemory", "SemanticMemory",
    "cosine_similarity", "top_k_retrieval", "context_budget_trim", "count_tokens",
    # planning
    "run_react", "parse_react_trace", "extract_answer",
    "reflect_and_retry", "RetryBudget", "tree_of_thoughts", "select_strategy",
    # multi-agent
    "Coordinator", "Worker", "Message", "route_message",
    "DelegationCap", "DelegationError", "synthesize_outputs",
    # evals
    "run_eval", "summarize", "success_rate", "step_efficiency", "cost_per_task",
    "classify_failure", "failure_breakdown", "regression_diff",
    "load_traces", "replay_runner", "exact_match", "contains",
]

__version__ = "1.0.0"  # module-8: framework consolidated
