# MANIFEST — asset coverage at a glance

Every course asset and its path. IDs trace back to [COURSE_SPEC.md](COURSE_SPEC.md).

## Framework (`src/agent/`) — tagged `module-0` … `module-8`

| File | Module | Provides |
|---|---|---|
| `llm.py` | M1 | `complete()`, `embed()`, `LLMResponse` (provider-agnostic) |
| `loop.py` | M1 + M7 + M8 | `Agent` (one hardened loop, optional tools), `ToolAgent`, `default_stop`, `enforce_caps`, `format_log_record`, `guardrail_check` |
| `tools.py` | M2 | `Tool`, `ToolRegistry`, `parse_tool_call`, `dispatch` |
| `memory.py` | M3 | `WorkingMemory`, `EpisodicMemory`, `SemanticMemory`, `cosine_similarity`, `top_k_retrieval`, `context_budget_trim` |
| `planning.py` | M4 | `run_react`, `parse_react_trace`, `reflect_and_retry`, `RetryBudget`, `tree_of_thoughts`, `select_strategy` |
| `multiagent.py` | M5 | `Coordinator`, `Worker`, `route_message`, `DelegationCap`, `synthesize_outputs` |
| `evals.py` | M6 | `run_eval`, `success_rate`, `step_efficiency`, `cost_per_task`, `classify_failure`, `regression_diff` |
| `__init__.py` | M8 | consolidated public API |
| `examples/hello_agent.py` · `examples/minimal_agent.py` · `examples/flagship_agent.py` | M0 · core · M8 | runnable demos (20-line toy · ~120-line canonical single file · full capstone) |

## Lab notebooks (`notebooks/`) — clean + answers each

`lab_v0_4` · `lab_v1_3` · `lab_v1_5` · `lab_v2_4` · `lab_v3_4` · `lab_v3_6` ·
`lab_v4_3` · `lab_v5_6` · `lab_v6_3` · `lab_v7_2`   → 10 labs × 2 = **20 files**

## Assignments (`assignments/`) + grader (`grader/`)

`assignment_1` … `assignment_8` (scaffold + `_solution`) = **16 files** ·
`grader/grade.py` (CLI `python grader/grade.py N`) · `grader/README.md`

## Udemy coding exercises (`udemy_exercises/`) — 24 folders × {starter, solution, evaluation, exercise_meta}

| Module | Exercises (folder = `ex_<slug>`) |
|---|---|
| 1 | `ex_v1_2_normalize_llm_response` · `ex_v1_3_parse_intent` · `ex_v1_4_stopping_condition` |
| 2 | `ex_v2_4_parse_tool_call` · `ex_v2_5_tool_registry` · `ex_v2_7_dispatch_unknown_tool` |
| 3 | `ex_v3_2_context_budget_trim` · `ex_v3_4_cosine_similarity` · `ex_v3_5_top_k_retrieval` · `ex_v3_6_episodic_serialize` |
| 4 | `ex_v4_3_parse_react_trace` · `ex_v4_4_retry_budget` · `ex_v4_6_select_strategy` |
| 5 | `ex_v5_3_route_message` · `ex_v5_4_delegation_cap` · `ex_v5_6_synthesize_outputs` |
| 6 | `ex_v6_4_success_rate` · `ex_v6_4_step_efficiency` · `ex_v6_4_cost_per_task` · `ex_v6_5_classify_failure` · `ex_v6_6_regression_diff` |
| 7 | `ex_v7_2_enforce_caps` · `ex_v7_4_format_log_record` · `ex_v7_5_guardrail_check` |

## Quizzes (`quizzes/`) & cheat sheets (`cheatsheets/`)

`module_0.md` … `module_8.md` in each → **9 quiz banks** + **9 cheat sheets**
(spaced-review questions in quizzes 2, 3, 5, 7, and cumulative recall in 8).

## Fixtures (`fixtures/`) — shipped, offline, deterministic

`traces/runA.json`, `traces/runB.json`, `traces/t1..t5.json` (Module 6) ·
`embeddings/doc_vectors.npy`, `docs.json`, `query_vectors.npy`, `queries.json` (Module 3) ·
`fixtures/README.md` (schema)

## Tests (`tests/`)

`test_module_0.py` … `test_module_8.py` (smoke, offline) · `test_live.py` (opt-in,
`RUN_LIVE=1`) · `run_all.py` (pytest-free runner)

## Coverage summary

8 framework files · 2 examples · 20 lab notebooks · 16 assignment files + grader ·
24 coding exercises (96 files) · 9 quizzes · 9 cheat sheets · 11 fixtures ·
9 test files · 9 git tags.
