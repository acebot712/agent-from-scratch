# COURSE_SPEC.md
**Source of truth for "Build an AI Agent From Scratch."** Every downstream asset (repo code, notebooks, graders, Udemy coding exercises, quizzes, cheat sheets, slides, scripts, listing copy) references the stable IDs defined here. Do not renumber IDs once assets are generated.

> **v2 — production-lead review applied.** Changes: V8.3 extended to 16m (edited build); V3.4 retitled; token-budget exercise made tokenizer-free; retrieval exercises pinned to embedding fixtures; mechanical-vs-LLM versions disambiguated; spaced-review added at Modules 2 & 8; per-module prerequisites added; Module 6 ships trace fixtures; `embed()` added to the LLM wrapper.

---

## 1. Course identity

- **Title:** Build an AI Agent From Scratch
- **Subtitle:** Stop using frameworks you don't understand. Build the whole thing yourself in pure Python.
- **One-line promise:** By the end you will have built your own ~1,200-line agent framework — tool use, memory, planning, multi-agent, and evals — and you'll be able to recognise every *concept* in any agent framework on the market (they're your own pieces under different names).
- **Target learner:** Working developers and technical builders who use LLMs but treat agents as magic. People who've wired up LangChain/CrewAI without understanding what's underneath and want first-principles mastery.
- **Prerequisites:** Solid Python (functions, classes, dicts, basic async is a bonus). Has called an LLM API at least once. **No ML math required** — no calculus, no linear algebra beyond an intuitive dot product, which is taught from scratch.
- **Final artifact:** A single coherent, readable agent framework (~1,200 lines) the learner builds themselves across the course, living in one public GitHub repo, tagged per module. The capstone uses it to build a flagship end-to-end agent.
- **Format:** Short single-concept videos (3–16 min), guided lab notebooks, autograded Udemy coding exercises for deterministic concepts, scaffolded assignment notebooks with a local autograder for LLM-dependent work, per-module quizzes, and per-module cheat sheets.
- **Total video runtime:** ~6.5 hours across 9 modules / 49 micro-videos (hands-on work brings total learner time into the 8–12h range).
- **Course is sequential.** Modules build on each other and the code is monotonic (each module imports prior modules). Udemy lets learners jump around, so every module states its prerequisites and the listing copy will recommend taking it in order. Module 6 is the one module made independently runnable via shipped fixtures.
- **Tech constraints:** Python 3.10 target (matches Udemy's coding-exercise sandbox). Framework dependencies limited to **numpy + a provider-agnostic LLM client**. The client (`llm.py`) exposes **both** `complete(messages, tools=None)` and `embed(texts)` — memory retrieval needs embeddings, which is a distinct call from chat completion. No LangChain, no vector DB, no heavyweight deps. Coding exercises use **standard library + numpy only** and must be fully offline/deterministic.

### Module map (runtime)

| Module | Title | Videos | Runtime | Free? | Depends on |
|---|---|---|---|---|---|
| 0 | What an agent actually is | 4 | 25m | **Free preview** | — |
| 1 | The agent loop, properly | 5 | 42m | V1.1 free preview | M0 |
| 2 | Tool use from scratch | 7 | 53m | paid | M1 |
| 3 | Memory architectures | 6 | 50m | paid | M1 |
| 4 | Planning & reasoning | 6 | 50m | paid | M1, M2 |
| 5 | Multi-agent systems | 6 | 46m | paid | M1, M2 (M3 helpful) |
| 6 | Evaluating agents | 6 | 47m | paid | M1 concepts; runs on shipped fixtures |
| 7 | Production realities | 5 | 37m | paid | M1, M2 |
| 8 | Capstone | 4 | 37m | paid | M1–M7 |

---

## 2. Module & micro-lesson breakdown

> Each module opens with an **objective card** (one slide: "By the end you'll be able to ___"). **Spaced-review checkpoints** (2 quick recall questions on earlier material) open Modules **2, 3, 5, 7, and 8** as noted inline.

### Module 0 — What an agent actually is `[FREE]`
*Depends on: nothing. Objective card: By the end you'll be able to define an agent precisely and write one in 20 lines.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V0.1 | Course promise + what you'll build | 3 | State what the course delivers and what the final artifact is. |
| V0.2 | The definition: an LLM in a loop with tools | 7 | Define an agent as an LLM in a loop that chooses its own next action. |
| V0.3 | Why LangChain/CrewAI hide this from you | 6 | Explain that frameworks are abstraction over one simple loop. |
| V0.4 | Live build: a working agent in 20 lines | 9 | Write a minimal agent loop that calls an LLM and acts. |

### Module 1 — The agent loop, properly
*Depends on: M0. Objective card: By the end you'll be able to build a reusable Agent class with a correct stopping condition.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V1.1 | Anatomy of the loop `[free preview]` | 8 | Identify the five parts of the agent loop (observe→decide→act→feed back→stop). |
| V1.2 | A provider-agnostic LLM wrapper | 8 | Normalise responses from different LLM providers behind one interface. |
| V1.3 | Parsing the model's intent | 9 | Extract a structured action from a free-text model response. |
| V1.4 | The stopping problem | 7 | Implement a terminal-state check that ends the loop correctly. |
| V1.5 | Building the reusable Agent class | 10 | Assemble the pieces into an `Agent.run(task)` class. |

### Module 2 — Tool use from scratch
*Depends on: M1. **Spaced review (start):** recall the loop's stopping condition (M1) + the agent definition (M0).*
*Objective card: By the end you'll be able to give an agent tools and handle tool calls reliably.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V2.1 | What "tool use" really means | 6 | Explain how an LLM "uses" a tool it cannot execute itself. |
| V2.2 | Designing a clean tool interface | 7 | Define a consistent tool signature (name, description, args, run). |
| V2.3 | Getting the model to request a tool — by hand | 10 | Prompt a model to emit a tool request without native function calling. |
| V2.4 | Parsing tool calls reliably | 9 | Parse a tool request into a structured `{name, args}` object. |
| V2.5 | The tool registry + dispatch | 8 | Register tools and dispatch a parsed call to the right one. |
| V2.6 | Native function calling — and why you now understand it | 7 | Map the native function-calling API onto the from-scratch version. |
| V2.7 | When the model hallucinates a tool | 6 | Handle unknown-tool and malformed-arg errors gracefully. |

### Module 3 — Memory architectures
*Depends on: M1. **Spaced review (start):** recall tool dispatch (M2) + intent parsing (M1).*
*Objective card: By the end you'll be able to give an agent working, episodic, and semantic memory.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V3.1 | The three memories | 8 | Distinguish working, episodic, and semantic memory. |
| V3.2 | The context window as a budget | 7 | Trim a message history to fit a token budget. |
| V3.3 | Summarization when you overflow | 9 | Compress old turns into a running summary on overflow. |
| V3.4 | Similarity from scratch: cosine in numpy | 10 | Compute cosine similarity between two vectors in numpy (embeddings taken as given via `embed()`). |
| V3.5 | Retrieval without a vector DB | 9 | Rank documents by similarity and return top-k. |
| V3.6 | Persisting episodic memory across sessions | 7 | Serialise and reload memory so an agent remembers across runs. |

### Module 4 — Planning & reasoning
*Depends on: M1, M2 (ReAct actions are tool calls). Objective card: By the end you'll be able to make an agent plan, act, and self-correct.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V4.1 | Why a single LLM call isn't enough | 6 | Explain why complex tasks need iterative reasoning. |
| V4.2 | ReAct: interleaving reasoning and action | 10 | Describe the Thought→Action→Observation cycle. |
| V4.3 | Implementing ReAct from scratch | 10 | Implement and parse a ReAct loop. *(Production note: walk pre-written code; do not type live.)* |
| V4.4 | Reflection: critique and retry | 9 | Implement a self-critique-and-retry loop within a retry budget. |
| V4.5 | A taste of tree-of-thoughts | 9 | Explore multiple candidate paths and select the best. |
| V4.6 | Picking a strategy per task type | 6 | Select a reasoning strategy based on task metadata. |

### Module 5 — Multi-agent systems
*Depends on: M1, M2 (M3 helpful). **Spaced review (start):** recall memory budgeting (M3) + ReAct (M4).*
*Objective card: By the end you'll be able to coordinate multiple agents without infinite loops.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V5.1 | From one loop to many | 6 | Explain when multiple agents beat one. |
| V5.2 | The coordinator/worker pattern | 9 | Describe how a coordinator decomposes and delegates work. |
| V5.3 | Message passing between agents | 9 | Route a structured message from one agent to another. |
| V5.4 | Stopping infinite delegation | 7 | Enforce a delegation-depth cap to prevent runaway loops. |
| V5.5 | Role design and prompting | 8 | Define agent roles via system prompts. |
| V5.6 | Synthesizing worker outputs | 7 | Merge multiple worker outputs into one result. |

### Module 6 — Evaluating agents
*Depends on: M1 concepts only; **runs on shipped trace fixtures** so it works even if earlier agents weren't built by the learner. Objective card: By the end you'll be able to measure whether an agent actually works.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V6.1 | You can't ship what you can't measure | 6 | Explain why agents need evals, not vibes. |
| V6.2 | Defining task success precisely | 8 | Write a success predicate for a task. |
| V6.3 | Building the eval harness | 10 | Run an agent over a task set and collect results. |
| V6.4 | Metrics: success rate, steps, cost | 8 | Compute success rate, step efficiency, and cost per task. |
| V6.5 | A failure-mode taxonomy | 8 | Classify a failed run into a failure category from its trace. |
| V6.6 | Catching regressions when you tweak a prompt | 7 | Diff two eval runs to detect a regression. |

### Module 7 — Production realities
*Depends on: M1, M2. **Spaced review (start):** recall delegation caps (M5) + eval metrics (M6).*
*Objective card: By the end you'll be able to harden an agent against runaway cost and silent failure.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V7.1 | Agents that burn money: a runaway loop, live | 7 | Recognise how an uncapped loop runs up cost. |
| V7.2 | Cost and step caps | 7 | Enforce a max-step and max-cost cap that halts the loop. |
| V7.3 | Latency and streaming | 7 | Explain where latency comes from and how streaming helps. |
| V7.4 | Observability: logging every step | 8 | Emit a structured log record per agent step. |
| V7.5 | Guardrails and tool-access risk | 8 | Apply an allow/block rule to a tool call before executing it. |

### Module 8 — Capstone
*Depends on: M1–M7. **Spaced review (start):** cumulative recall — one question each on tools (M2), memory (M3), and evals (M6).*
*Objective card: By the end you'll have assembled the framework and shipped a flagship agent.*

| ID | Title | Min | Single learning objective |
|---|---|---|---|
| V8.1 | Refactoring into a coherent framework | 9 | Consolidate all modules into one clean public API. |
| V8.2 | Designing your flagship agent | 7 | Scope an end-to-end agent worth demoing. |
| V8.3 | Building it end-to-end (edited build) | 16 | Build a representative flagship agent on the framework; key moments shown live, full code in repo. |
| V8.4 | You now understand every framework + where to go next | 5 | Map the framework's pieces onto LangChain/CrewAI/AutoGen. |

---

## 3. Per-module assets & deterministic-vs-LLM classification

**Classification key.** `DETERMINISTIC` = no LLM/network needed; becomes a Udemy autograded coding exercise (`udemy_exercises/`), standard library + numpy only. `LLM` = requires a live model; lives in a notebook lab and/or a scaffolded assignment graded locally on **structural** properties (which tool was chosen, did it retry, did it cap steps), never on exact text.

> **Disambiguation rule.** Several concepts have both an LLM version (shown in the video/lab) and a mechanical version (the autograded exercise). The coding exercise always tests the **mechanical/rule-based** version. These are flagged ⚠ below.

### Module 0
- **Lab:** LAB0 — run the 20-line agent (V0.4), break it on purpose, observe failures. `LLM`
- **Assignment:** none (free-tier friction kept at zero).
- **Quiz topic (Q0):** what is / isn't an agent; the parts of the loop.
- **Cheat sheet (module_0):** the agent definition, the loop diagram, the 20-line reference agent.
- **Deterministic concepts:** none. **LLM concepts:** the hello-agent loop.

### Module 1
- **Labs:** LAB1.3 — parse intent from sample responses (V1.3) `DETERMINISTIC`; LAB1.5 — run the Agent class on a 3-step question (V1.5) `LLM`.
- **Assignment (assignment_1):** build a loop that solves a multi-step word problem. Scaffold: class skeleton given; learner writes loop body + stopping logic. Graded locally on structural completion. `LLM`
- **Quiz topic (Q1):** loop control flow, stopping conditions, provider abstraction.
- **Cheat sheet (module_1):** the Agent class API, the LLM wrapper interface (`complete` + `embed`), stopping-condition patterns.
- **Coding exercises:**
  - `EX1.1` normalize_llm_response (V1.2) `DETERMINISTIC` — operate on a provided raw-response fixture dict.
  - `EX1.2` parse_intent (V1.3) `DETERMINISTIC` — parse a provided response string.
  - `EX1.3` stopping_condition (V1.4) `DETERMINISTIC`

### Module 2
- **Labs:** LAB2.4 — add a weather tool & watch it get called (V2.4) `LLM`.
- **Assignment (assignment_2):** build 3 tools + registry + dispatch; agent must select the right tool. Scaffold: registry given; learner writes tools + dispatch + error path. Graded on correct tool selection. `LLM`
- **Quiz topic (Q2):** tool interface, parsing tool calls, registry/dispatch, failure handling. *(Plus 2 spaced-review items: M0/M1.)*
- **Cheat sheet (module_2):** tool signature, registry API, dispatch flow, native-vs-manual function calling.
- **Coding exercises:**
  - `EX2.1` parse_tool_call (V2.4) `DETERMINISTIC`
  - `EX2.2` tool_registry (V2.5) `DETERMINISTIC`
  - `EX2.3` dispatch_unknown_tool (V2.5 + V2.7) `DETERMINISTIC`

### Module 3
- **Labs:** LAB3.4 — cosine-similarity + top-k retrieval on a provided embedding fixture (V3.4/3.5) `DETERMINISTIC (math)`; optional live `embed()` demo cell `LLM`. LAB3.6 — remember a fact across two runs (V3.6) `LLM`.
- **Assignment (assignment_3):** implement semantic retrieval over a small doc set and inject top-k into context. **Grader uses a fixed embedding fixture** (no live embedding) so scoring is deterministic; relevance graded against expected top-k. `LLM` to run live, `DETERMINISTIC` to grade.
- **Quiz topic (Q3):** the three memory types, context budgeting, retrieval mechanics. *(Plus 2 spaced-review items: M1/M2.)*
- **Cheat sheet (module_3):** memory taxonomy, context-budget trimming, cosine/top-k snippet, persistence format.
- **Coding exercises:**
  - `EX3.1` cosine_similarity (V3.4) `DETERMINISTIC`
  - `EX3.2` top_k_retrieval (V3.5) `DETERMINISTIC` — input is **precomputed embedding vectors**, not text.
  - `EX3.3` context_budget_trim (V3.2) `DETERMINISTIC` — uses a **provided `count_tokens()` proxy** (word/char based); no external tokenizer, so it runs offline in the sandbox.
  - `EX3.4` episodic_serialize (V3.6) `DETERMINISTIC`

### Module 4
- **Labs:** LAB4.3 — ReAct vs naive on the same task (V4.3) `LLM`.
- **Assignment (assignment_4):** implement a reflection loop that fixes a failing output within N retries. Graded on measured improvement + retry-budget respected. `LLM` (retry-budget logic `DETERMINISTIC`)
- **Quiz topic (Q4):** ReAct trace anatomy, when to reflect, strategy selection.
- **Cheat sheet (module_4):** ReAct format, reflection loop, ToT sketch, strategy-selection table.
- **Coding exercises:**
  - `EX4.1` parse_react_trace (V4.3) `DETERMINISTIC` — parse Thought/Action/Observation from provided text.
  - `EX4.2` retry_budget (V4.4) `DETERMINISTIC`
  - `EX4.3` select_strategy (V4.6) `DETERMINISTIC` — rule-based selection from task metadata.

### Module 5
- **Labs:** LAB5.6 — add a third worker to a 2-agent system (V5.6) `LLM`.
- **Assignment (assignment_5):** build a research→write→review trio. Graded on end-to-end output + no infinite loops (delegation cap enforced). `LLM` (cap + routing `DETERMINISTIC`)
- **Quiz topic (Q5):** coordination patterns, message passing, loop-termination risk, role design. *(Plus 2 spaced-review items: M3/M4.)*
- **Cheat sheet (module_5):** coordinator/worker diagram, message schema, delegation-cap pattern, synthesis.
- **Coding exercises:**
  - `EX5.1` route_message (V5.3) `DETERMINISTIC`
  - `EX5.2` delegation_cap (V5.4) `DETERMINISTIC`
  - `EX5.3` synthesize_outputs (V5.6) `DETERMINISTIC` ⚠ — tests the **mechanical merge** (combine/dedupe/order a list of worker outputs into a structured result). The LLM-written synthesis is shown in V5.6/LAB5.6, not graded.

### Module 6
- **Labs:** LAB6.3 — run the harness over **shipped recorded traces** (V6.3) `DETERMINISTIC`.
- **Assignment (assignment_6):** write an eval suite that scores agents over a **fixed shipped trace set**. Graded on correct metric computation. `DETERMINISTIC`
- **Quiz topic (Q6):** metric definitions, failure taxonomy, regression detection.
- **Cheat sheet (module_6):** metric formulas, failure categories, regression-diff pattern, eval-harness skeleton.
- **Coding exercises:**
  - `EX6.1` success_rate (V6.4) `DETERMINISTIC`
  - `EX6.2` step_efficiency (V6.4) `DETERMINISTIC`
  - `EX6.3` cost_per_task (V6.4) `DETERMINISTIC`
  - `EX6.4` classify_failure (V6.5) `DETERMINISTIC` ⚠ — **rule-based** classification over trace fields (e.g. max-steps-hit, tool-error, no-final-answer). LLM-judged classification is discussed, not graded.
  - `EX6.5` regression_diff (V6.6) `DETERMINISTIC`

### Module 7
- **Labs:** LAB7.2 — trigger a runaway with a live loop, then cap it (V7.2). Runaway demo `LLM`; cap test uses a **mock loop** `DETERMINISTIC`.
- **Assignment (assignment_7):** harden the framework with cost/step caps + structured logging. Graded on cap enforcement + log-record shape. `DETERMINISTIC`
- **Quiz topic (Q7):** cost control, observability, guardrails, failure containment. *(Plus 2 spaced-review items: M5/M6.)*
- **Cheat sheet (module_7):** cap-enforcement pattern, log-record schema, guardrail rule format, latency notes.
- **Coding exercises:**
  - `EX7.1` enforce_caps (V7.2) `DETERMINISTIC`
  - `EX7.2` format_log_record (V7.4) `DETERMINISTIC`
  - `EX7.3` guardrail_check (V7.5) `DETERMINISTIC` ⚠ — **rule-based** allow/block (allowlist/denylist/pattern). LLM-classifier guardrails are mentioned as an extension, not graded.

### Module 8
- **Lab:** none (capstone replaces it).
- **Capstone (capstone):** build an original agent on the framework. Rubric-based self-assessment + optional community peer review. `LLM`
- **Quiz topic (Q8):** mapping the framework onto named frameworks; final synthesis. *(Plus 3 cumulative spaced-review items: M2/M3/M6.)*
- **Cheat sheet (module_8):** the full public API on one page; framework-equivalence map (our piece ↔ LangChain/CrewAI/AutoGen).
- **Coding exercises:** none.

**Coding-exercise coverage:** 24 autograded exercises spanning Modules 1–7 (≥1 per build section, satisfying Udemy's per-section guidance). Modules 0 and 8 are intentionally exercise-free (intro / open-ended capstone).

---

## 4. Naming conventions

### Repository
```
agent-from-scratch/
  COURSE_SPEC.md
  README.md                       # learner-facing
  MANIFEST.md                     # asset coverage index
  requirements.txt
  .env.example                    # LLM_API_KEY=, LLM_PROVIDER=
  src/agent/
    __init__.py                   # public API (finalised in module-8)
    llm.py                        # provider-agnostic client: complete() + embed()
    loop.py                       # Agent class + run loop + prod hardening
    tools.py                      # tool interface, registry, dispatch
    memory.py                     # working/episodic/semantic + retrieval
    planning.py                   # ReAct, reflection, tree-of-thoughts
    multiagent.py                 # coordinator/worker, routing, synthesis
    evals.py                      # harness, metrics, taxonomy, regression
  examples/
    hello_agent.py                # the 20-line Module 0 build
  notebooks/
    lab_<videoid>_clean.ipynb     # e.g. lab_v3_4_clean.ipynb
    lab_<videoid>_answers.ipynb
  assignments/
    assignment_<N>.ipynb          # N = module number, e.g. assignment_3.ipynb
    assignment_<N>_solution.ipynb
  grader/
    grade.py                      # CLI: python grader/grade.py <N>
    README.md
  udemy_exercises/
    ex_v<module>_<n>_<slug>/      # e.g. ex_v2_4_parse_tool_call/
      starter.py
      solution.py
      evaluation.py
      exercise_meta.md            # title, objective, statement, hints, explanation
  fixtures/                       # shipped, version-controlled test data
    traces/                       # recorded agent traces for Module 6 evals
    embeddings/                   # precomputed vectors for Module 3 retrieval
  quizzes/
    module_<N>.md                 # questions, answers, explanations
  cheatsheets/
    module_<N>.md
  tests/
    test_<module>.py              # smoke tests per module
```

### Identifier schemes (stable — do not renumber)
- **Video ID:** `V<module>.<n>` → `V2.3`. Path form: `v2_3`.
- **Lab ID:** `LAB<module>.<videoindex>` → `LAB3.4`. File: `notebooks/lab_v3_4_clean.ipynb` / `..._answers.ipynb`.
- **Assignment ID:** `assignment_<module>` → `assignment_3`. One per module (none for M0; M8 = `capstone`).
- **Quiz ID:** `Q<module>` for the bank; questions as `Q<module>.<n>` → `Q4.2`. Spaced-review items prefixed `SR` (e.g. `Q2.SR1`).
- **Coding-exercise ID:** `EX<module>.<n>` → `EX6.3`. Folder: `udemy_exercises/ex_v<module>_<n>_<slug>/` (slug = function name).
- **Cheat sheet:** `cheatsheets/module_<N>.md`.
- **Fixtures:** `fixtures/traces/<name>.json`, `fixtures/embeddings/<name>.npy` (+ a `fixtures/README.md` documenting schema).
- **Git tags:** `module-0` … `module-8`. Each tag = the repo state after that module's code is complete and tests pass. Learners `git checkout module-N` to jump to any point; the instructor checks out `module-N` before recording Module N so on-screen code matches.
- **Commit message convention:** `module-N: <description>` for framework commits; `assets: <type>` for asset commits (e.g. `assets: quiz banks`).

### Cross-reference rule
Every generated asset header must cite the IDs it implements (e.g. a coding-exercise folder states `Implements: EX2.1 (source V2.4)`; a slide section states `Covers: V3.4`). This makes coverage auditable from MANIFEST.md.
