"""Generate the guided lab notebooks (clean + answers) from a compact spec.

Run:  python notebooks/_build_labs.py
Produces, per lab:  notebooks/lab_v<m>_<n>_clean.ipynb  and  ..._answers.ipynb

Each notebook:
  * opens with a markdown cell stating the single learning objective,
  * is mostly-complete code the learner runs cell by cell,
  * has 2-3 "👉 Your turn" cells (TODO in *_clean, solved in *_answers),
  * ends with an informal "eyeball your output" check,
  * imports from ``src/agent`` so it stays in sync with the framework.

The spec is a list of cells. A cell is one of:
  ("md",   "markdown source")
  ("code", "always-the-same code")
  ("turn", "clean version (TODO)", "answer version (solution)")
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Boilerplate every notebook starts its code with.
BOOT = (
    "import os, sys\n"
    "# Prefer your working copy (my_agent/, from `python setup_module.py N`);\n"
    "# fall back to the reference framework in src/.\n"
    "for _p in ('../my_agent', '../src'):\n"
    "    if os.path.isdir(os.path.join(_p, 'agent')):\n"
    "        sys.path.insert(0, os.path.abspath(_p)); break"
)


def md(s):
    return ("md", s)


def code(s):
    return ("code", s)


def turn(clean, answer):
    return ("turn", clean, answer)


# ---------------------------------------------------------------------------
# Lab specs.  Key = (module, n, lab_id, is_llm); value = (title, objective, cells)
# ---------------------------------------------------------------------------
LABS = {}


def lab(vid, lab_id, llm, title, objective, cells):
    LABS[vid] = dict(lab_id=lab_id, llm=llm, title=title, objective=objective, cells=cells)


# --- LAB0 / V0.4 -----------------------------------------------------------
lab("v0_4", "LAB0", True,
    "The 20-line agent — and how to break it",
    "Write a minimal agent loop that calls an LLM and acts (V0.4); then break it "
    "on purpose to *feel* why each part of the loop exists.",
    [
        md("## LAB0 — the 20-line agent  \nImplements: **LAB0 (source V0.4)**\n\n"
           "**Learning objective:** write a minimal agent loop that calls an LLM and "
           "acts, then break it to understand each part.\n\n"
           "> Needs a key: `LLM_PROVIDER` and `LLM_API_KEY` in your environment."),
        code(BOOT),
        code("from agent.llm import complete\n\n"
             "DONE = 'FINAL ANSWER:'\n\n"
             "def run(task, system, max_steps=5):\n"
             "    messages = [\n"
             "        {'role': 'system', 'content': system},\n"
             "        {'role': 'user', 'content': task},\n"
             "    ]\n"
             "    for _ in range(max_steps):\n"
             "        reply = complete(messages).text          # the LLM decides\n"
             "        messages.append({'role': 'assistant', 'content': reply})\n"
             "        if DONE in reply:                         # the stopping condition\n"
             "            return reply.split(DONE, 1)[1].strip()\n"
             "        messages.append({'role': 'user', 'content': 'Continue.'})\n"
             "    return '[no final answer — hit max_steps]'"),
        code("good_system = f\"Reason step by step. End with '{DONE} <answer>'.\"\n"
             "print(run('What is 17 * 23?', good_system))"),
        turn(
            "# 👉 Your turn (1): BREAK THE STOP CONDITION.\n"
            "# Write a system prompt that never tells the model to emit 'FINAL ANSWER:'.\n"
            "# Predict what happens, then run it.\n"
            "broken_system = ...  # TODO\n"
            "print(run('What is 17 * 23?', broken_system))",
            "# 👉 Your turn (1): BREAK THE STOP CONDITION.\n"
            "broken_system = 'Just chat. Never say the words FINAL ANSWER.'\n"
            "print(run('What is 17 * 23?', broken_system))  # -> hits max_steps"),
        turn(
            "# 👉 Your turn (2): make it stop too early.\n"
            "# Call run(...) with max_steps=1 and the GOOD prompt on a hard multi-step task.\n"
            "print(run('List the first 5 primes one per step, then FINAL ANSWER.', good_system, max_steps=...))",
            "# 👉 Your turn (2): make it stop too early.\n"
            "print(run('List the first 5 primes one per step, then FINAL ANSWER.', good_system, max_steps=1))"),
        md("### 🔎 Eyeball your output\n"
           "- With the **good** prompt you should see a clean numeric answer (391).\n"
           "- With the **broken** prompt it should run to `max_steps` and return the "
           "`[no final answer]` sentinel — that's the stopping condition earning its keep.\n"
           "- With `max_steps=1` it gets cut off mid-task. Three knobs, three failure modes."),
    ])

# --- LAB1.3 / V1.3  (DETERMINISTIC) ---------------------------------------
lab("v1_3", "LAB1.3", False,
    "Parsing the model's intent",
    "Extract a structured action from a free-text model response (V1.3) — no "
    "network, pure parsing.",
    [
        md("## LAB1.3 — parsing intent  \nImplements: **LAB1.3 (source V1.3)** · `DETERMINISTIC`\n\n"
           "**Learning objective:** extract a structured action from a free-text "
           "model response. Runs fully offline."),
        code(BOOT),
        code("# Sample model responses — some call a tool, some answer directly.\n"
             "samples = [\n"
             "    'Thought: I need the weather.\\nACTION: get_weather(\"Paris\")',\n"
             "    'ACTION: add(2, 3)',\n"
             "    'The answer is 5. FINAL ANSWER: 5',\n"
             "]"),
        turn(
            "import re\n"
            "def parse_intent(text):\n"
            "    \"\"\"Return {'kind':'final','value':..} or {'kind':'action','name':..,'raw_args':..}.\"\"\"\n"
            "    # 👉 Your turn (1): if 'FINAL ANSWER:' is present, return a 'final' intent.\n"
            "    # 👉 Your turn (2): else match  NAME(args)  after 'ACTION:' and return an 'action' intent.\n"
            "    ...  # TODO\n",
            "import re\n"
            "def parse_intent(text):\n"
            "    if 'FINAL ANSWER:' in text:\n"
            "        return {'kind': 'final', 'value': text.split('FINAL ANSWER:', 1)[1].strip()}\n"
            "    m = re.search(r'ACTION:\\s*([A-Za-z0-9_]+)\\((.*)\\)', text)\n"
            "    if m:\n"
            "        return {'kind': 'action', 'name': m.group(1), 'raw_args': m.group(2).strip()}\n"
            "    return {'kind': 'unknown'}\n"),
        code("for s in samples:\n    print(parse_intent(s))"),
        code("# Cross-check against the framework's own parser (different format, same idea):\n"
             "from agent.tools import parse_tool_call\n"
             "print(parse_tool_call('TOOL: add\\nARGS: {\"a\": 2, \"b\": 3}'))"),
        md("### 🔎 Eyeball your output\n"
           "You should see: an `action` intent for the first two samples (with the right "
           "`name`) and a `final` intent for the third. If everything comes back "
           "`unknown`, your regex isn't matching — print the text and check the format."),
    ])

# --- LAB1.5 / V1.5  (LLM) --------------------------------------------------
lab("v1_5", "LAB1.5", True,
    "Running the reusable Agent class",
    "Assemble the pieces into an Agent.run(task) call on a 3-step question (V1.5).",
    [
        md("## LAB1.5 — the Agent class  \nImplements: **LAB1.5 (source V1.5)**\n\n"
           "**Learning objective:** run the reusable `Agent` on a multi-step question.\n\n"
           "> Needs a key."),
        code(BOOT),
        code("from agent import Agent"),
        turn(
            "# 👉 Your turn (1): construct an Agent with a step-by-step system prompt\n"
            "# and max_steps=5.\n"
            "agent = Agent(system_prompt=..., max_steps=...)  # TODO",
            "agent = Agent(system_prompt='Solve step by step. End with FINAL ANSWER: <x>.',\n"
            "              max_steps=5)"),
        turn(
            "# 👉 Your turn (2): run it on a question that needs a few steps.\n"
            "answer = agent.run(...)  # TODO\n"
            "print(answer)",
            "answer = agent.run('A train travels 60 km in 1.5 hours. What is its average speed in km/h?')\n"
            "print(answer)"),
        code("# Inspect the loop's trace:\n"
             "for m in agent.history:\n    print(m['role'], '·', m['content'][:80])"),
        md("### 🔎 Eyeball your output\n"
           "The answer should be **40** (km/h). Scroll the history: you should see "
           "alternating assistant/user turns ending when the model emits FINAL ANSWER. "
           "If `history` is just two messages, it stopped on the first turn — fine if the "
           "model one-shotted it."),
    ])

# --- LAB2.4 / V2.4 (LLM) ---------------------------------------------------
lab("v2_4", "LAB2.4", True,
    "Add a weather tool and watch it get called",
    "Parse a tool request and dispatch it (V2.4): give the agent a tool and watch "
    "the loop call it.",
    [
        md("## LAB2.4 — a weather tool  \nImplements: **LAB2.4 (source V2.4)**\n\n"
           "**Learning objective:** register a tool and watch the agent request and "
           "use it.\n\n> Needs a key."),
        code(BOOT),
        code("from agent import Tool, ToolRegistry, ToolAgent\n\n"
             "# A fake weather service so the lab is reproducible.\n"
             "_WEATHER = {'Paris': '18C, cloudy', 'Cairo': '34C, sunny'}"),
        turn(
            "# 👉 Your turn (1): write the tool function. It takes `city` and returns a string.\n"
            "def get_weather(city):\n"
            "    ...  # TODO: look up _WEATHER, default to 'unknown'\n",
            "def get_weather(city):\n"
            "    return _WEATHER.get(city, f'no data for {city}')\n"),
        code("registry = ToolRegistry()\n"
             "registry.register(Tool(\n"
             "    name='get_weather', description='current weather for a city; arg: city',\n"
             "    run=get_weather,\n"
             "    parameters={'type': 'object', 'properties': {'city': {'type': 'string'}}},\n"
             "))\n"
             "print(registry.describe())"),
        turn(
            "# 👉 Your turn (2): build a ToolAgent over the registry and ask a weather question.\n"
            "agent = ToolAgent(registry, max_steps=...)  # TODO\n"
            "print(agent.run(...))  # TODO",
            "agent = ToolAgent(registry, max_steps=5)\n"
            "print(agent.run('What is the weather in Paris right now?'))"),
        code("# Did it actually call the tool? Look for an Observation turn:\n"
             "for m in agent.history:\n    print(m['role'], '·', m['content'][:80])"),
        md("### 🔎 Eyeball your output\n"
           "You want to see an `Observation: get_weather -> 18C, cloudy` turn in the "
           "history, and a final answer that mentions cloudy/18C. If there's no "
           "Observation line, the model answered from memory instead of calling the "
           "tool — try making the question more clearly tool-requiring."),
    ])

# --- LAB3.4 / V3.4-3.5 (DETERMINISTIC) ------------------------------------
lab("v3_4", "LAB3.4", False,
    "Cosine similarity + top-k retrieval from scratch",
    "Compute cosine similarity in numpy and rank documents by it (V3.4/V3.5), on a "
    "shipped embedding fixture.",
    [
        md("## LAB3.4 — cosine + top-k  \nImplements: **LAB3.4 (source V3.4/V3.5)** · "
           "`DETERMINISTIC (math)`\n\n**Learning objective:** compute cosine similarity "
           "and return the top-k most similar docs. Runs offline on the shipped "
           "embedding fixture."),
        code(BOOT),
        code("import json, numpy as np\n"
             "FIX = os.path.abspath(os.path.join('..', 'fixtures', 'embeddings'))\n"
             "vecs = np.load(os.path.join(FIX, 'doc_vectors.npy'))\n"
             "docs = json.load(open(os.path.join(FIX, 'docs.json')))\n"
             "print(vecs.shape)\n"
             "for d in docs: print('-', d)"),
        turn(
            "# 👉 Your turn (1): implement cosine similarity in numpy (guard the zero vector).\n"
            "def cosine(a, b):\n"
            "    a, b = np.asarray(a, float), np.asarray(b, float)\n"
            "    ...  # TODO: dot / (||a|| ||b||), return 0.0 if a denom is 0\n",
            "def cosine(a, b):\n"
            "    a, b = np.asarray(a, float), np.asarray(b, float)\n"
            "    denom = np.linalg.norm(a) * np.linalg.norm(b)\n"
            "    return 0.0 if denom == 0 else float(np.dot(a, b) / denom)\n"),
        turn(
            "# 👉 Your turn (2): rank all docs against a query vector and take the top-k.\n"
            "def top_k(query_vec, doc_vecs, k=2):\n"
            "    ...  # TODO: return list of (index, score) sorted desc by score\n",
            "def top_k(query_vec, doc_vecs, k=2):\n"
            "    scored = [(i, cosine(query_vec, v)) for i, v in enumerate(doc_vecs)]\n"
            "    scored.sort(key=lambda t: t[1], reverse=True)\n"
            "    return scored[:k]\n"),
        code("query = vecs[0]  # 'capital of France' — geography cluster\n"
             "for i, s in top_k(query, vecs, k=2):\n"
             "    print(round(s, 3), docs[i])"),
        code("# Cross-check against the framework implementation:\n"
             "from agent.memory import cosine_similarity, top_k_retrieval\n"
             "assert abs(cosine(vecs[0], vecs[1]) - cosine_similarity(vecs[0], vecs[1])) < 1e-9\n"
             "print('matches framework:', top_k_retrieval(query, vecs, 2))"),
        md("### 🔎 Eyeball your output\n"
           "The top-2 for the geography query should be the **two France/Paris** "
           "sentences (scores near 1.0), not the biology or programming ones. The "
           "assert against the framework should pass silently."),
    ])

# --- LAB3.6 / V3.6 (LLM / persistence) ------------------------------------
lab("v3_6", "LAB3.6", True,
    "Remember a fact across two sessions",
    "Serialise and reload memory so an agent remembers across runs (V3.6).",
    [
        md("## LAB3.6 — persistence across sessions  \nImplements: **LAB3.6 (source V3.6)**\n\n"
           "**Learning objective:** save episodic memory to disk and reload it in a "
           "fresh 'session'. The persistence itself is deterministic; using it to "
           "answer is the LLM part."),
        code(BOOT),
        code("from agent.memory import EpisodicMemory\n"
             "PATH = 'lab_memory.json'"),
        turn(
            "# 👉 Your turn (1): SESSION 1 — record a fact the agent should remember, then save.\n"
            "mem = EpisodicMemory()\n"
            "mem.record('user', ...)  # TODO: e.g. 'My favorite color is teal.'\n"
            "mem.save(PATH)",
            "mem = EpisodicMemory()\n"
            "mem.record('user', 'My favorite color is teal.')\n"
            "mem.save(PATH)"),
        turn(
            "# 👉 Your turn (2): SESSION 2 — load from disk (simulating a new process).\n"
            "reloaded = EpisodicMemory.load(...)  # TODO\n"
            "for e in reloaded.episodes:\n    print(e.role, '·', e.content)",
            "reloaded = EpisodicMemory.load(PATH)\n"
            "for e in reloaded.episodes:\n    print(e.role, '·', e.content)"),
        code("# (Optional, needs a key) feed the remembered fact into a fresh agent:\n"
             "# from agent import Agent\n"
             "# context = '\\n'.join(e.content for e in reloaded.episodes)\n"
             "# print(Agent().run('Given: ' + context + '\\nWhat is my favorite color?'))\n"
             "import os; print('memory file exists:', os.path.exists(PATH))"),
        md("### 🔎 Eyeball your output\n"
           "Session 2 should print the fact you recorded in session 1, even though it "
           "built a brand-new `EpisodicMemory` — it came back from `lab_memory.json`. "
           "That round-trip is the whole point. (Delete the file to reset.)"),
    ])

# --- LAB4.3 / V4.3 (LLM) ---------------------------------------------------
lab("v4_3", "LAB4.3", True,
    "ReAct vs naive on the same task",
    "Implement and parse a ReAct loop (V4.3) and compare it to a single naive call.",
    [
        md("## LAB4.3 — ReAct vs naive  \nImplements: **LAB4.3 (source V4.3)**\n\n"
           "**Learning objective:** see why interleaving reasoning with tool actions "
           "(ReAct) beats a single call on a task that needs a tool.\n\n> Needs a key."),
        code(BOOT),
        code("from agent import Tool, ToolRegistry, run_react, complete\n\n"
             "def calc(x):\n"
             "    \"\"\"Evaluate a simple arithmetic string, e.g. '128*47'.\"\"\"\n"
             "    return str(eval(x, {'__builtins__': {}}, {}))\n\n"
             "reg = ToolRegistry()\n"
             "reg.register(Tool(name='calc', description='evaluate arithmetic; arg is the expression',\n"
             "                  run=calc, parameters={'type':'object','properties':{'x':{'type':'string'}}}))"),
        code("TASK = 'What is 128 * 47, then add 19? Reason carefully.'\n\n"
             "# Naive: one call, no tools.\n"
             "naive = complete([{'role':'user','content': TASK}]).text\n"
             "print('NAIVE:\\n', naive)"),
        turn(
            "# 👉 Your turn (1): solve the same task with the ReAct loop + the calc tool.\n"
            "react = run_react(TASK, reg, max_steps=...)  # TODO\n"
            "print('REACT:\\n', react)",
            "react = run_react(TASK, reg, max_steps=6)\n"
            "print('REACT:\\n', react)"),
        turn(
            "# 👉 Your turn (2): the correct answer is 128*47+19. Compute it locally to compare.\n"
            "expected = ...  # TODO\n"
            "print('expected:', expected, '| react correct:', str(expected) in react)",
            "expected = 128 * 47 + 19\n"
            "print('expected:', expected, '| react correct:', str(expected) in react)"),
        md("### 🔎 Eyeball your output\n"
           "Expected is **6035**. The ReAct run should hit it via a `calc` Observation; "
           "the naive run often slips on the arithmetic. If ReAct didn't call the tool, "
           "check that the action format matched `Action: calc[...]`."),
    ])

# --- LAB5.6 / V5.6 (LLM) ---------------------------------------------------
lab("v5_6", "LAB5.6", True,
    "Add a third worker to a multi-agent system",
    "Merge multiple worker outputs into one result (V5.6); extend a 2-agent system "
    "to three.",
    [
        md("## LAB5.6 — add a third worker  \nImplements: **LAB5.6 (source V5.6)**\n\n"
           "**Learning objective:** extend a research→write crew with a reviewer and "
           "synthesize all three outputs.\n\n> Needs a key (or use the offline stub below)."),
        code(BOOT),
        code("from agent import Coordinator, Worker, DelegationCap, synthesize_outputs\n\n"
             "researcher = Worker('research', 'You research facts. Reply with 2 bullet facts.')\n"
             "writer = Worker('write', 'You write a one-sentence summary from the input.')"),
        turn(
            "# 👉 Your turn (1): add a reviewer worker with its own role/system prompt.\n"
            "reviewer = Worker(..., ...)  # TODO",
            "reviewer = Worker('review', 'You critique the summary in one short sentence.')"),
        turn(
            "# 👉 Your turn (2): wire all THREE into the coordinator and the decomposition.\n"
            "coord = Coordinator(\n"
            "    workers={'research': researcher, 'write': writer, ...},  # TODO add reviewer\n"
            "    cap=DelegationCap(max_depth=3),\n"
            "    decompose=lambda task: [('research', task), ('write', task), ...],  # TODO\n"
            ")",
            "coord = Coordinator(\n"
            "    workers={'research': researcher, 'write': writer, 'review': reviewer},\n"
            "    cap=DelegationCap(max_depth=3),\n"
            "    decompose=lambda task: [('research', task), ('write', task), ('review', task)],\n"
            ")"),
        code("# Run it (needs a key). Offline? Skip this and run the stub cell below.\n"
             "result = coord.run('the benefits of cycling to work')\n"
             "print(result['synthesis']['combined'])"),
        code("# Offline stub: prove the mechanical synthesis merges 3 outputs deterministically.\n"
             "print(synthesize_outputs(['fact A', 'a summary', 'a critique', 'fact A']))"),
        md("### 🔎 Eyeball your output\n"
           "`result['results']` should have **three** entries (research, write, review) "
           "and the synthesis `count` should be 3 (the stub shows the dedupe: the "
           "repeated 'fact A' collapses). If you see only two, the reviewer didn't make "
           "it into both `workers` and `decompose`."),
    ])

# --- LAB6.3 / V6.3 (DETERMINISTIC) ----------------------------------------
lab("v6_3", "LAB6.3", False,
    "Run the eval harness over shipped traces",
    "Run an agent over a task set and collect results (V6.3) — here, over recorded "
    "trace fixtures, fully offline.",
    [
        md("## LAB6.3 — the eval harness  \nImplements: **LAB6.3 (source V6.3)** · "
           "`DETERMINISTIC`\n\n**Learning objective:** run the harness over the shipped "
           "trace fixtures and read the metrics. No key needed — Module 6 runs on "
           "fixtures."),
        code(BOOT),
        code("from agent.evals import load_traces, success_rate, step_efficiency, \\\n"
             "    cost_per_task, failure_breakdown\n"
             "FIX = os.path.abspath(os.path.join('..', 'fixtures', 'traces'))\n"
             "traces = load_traces(os.path.join(FIX, 'runA.json'))\n"
             "print(len(traces), 'traces loaded')"),
        turn(
            "# 👉 Your turn (1): compute the three headline metrics.\n"
            "print('success rate :', ...)   # TODO success_rate(...)\n"
            "print('avg steps    :', ...)   # TODO step_efficiency(...)\n"
            "print('cost / task  :', ...)   # TODO cost_per_task(...)",
            "print('success rate :', success_rate(traces))\n"
            "print('avg steps    :', step_efficiency(traces))\n"
            "print('cost / task  :', round(cost_per_task(traces), 4))"),
        turn(
            "# 👉 Your turn (2): break down the failures by category.\n"
            "print(...)  # TODO failure_breakdown(traces)",
            "print(failure_breakdown(traces))"),
        md("### 🔎 Eyeball your output\n"
           "For `runA` you should see success rate **0.6**, avg steps **4.0**, and a "
           "failure breakdown of `{'max_steps_hit': 1, 'tool_error': 1}`. Those two "
           "failing tasks are exactly t3 (ran out of steps) and t4 (tool error)."),
    ])

# --- LAB7.2 / V7.2 (mixed) -------------------------------------------------
lab("v7_2", "LAB7.2", False,
    "Trigger a runaway loop, then cap it",
    "Enforce a max-step and max-cost cap that halts the loop (V7.2). The runaway is "
    "shown with a mock loop so it's safe and offline.",
    [
        md("## LAB7.2 — runaway, then cap  \nImplements: **LAB7.2 (source V7.2)**\n\n"
           "**Learning objective:** see an uncapped loop run forever, then halt it with "
           "`enforce_caps`. Uses a mock loop, so it's deterministic and free."),
        code(BOOT),
        code("from agent.loop import enforce_caps\n\n"
             "# A mock 'agent step' that always wants to keep going and costs $0.10 each.\n"
             "def mock_step():\n    return {'wants_more': True, 'cost': 0.10}"),
        code("# The RUNAWAY (bounded here only by range() so the notebook returns!).\n"
             "steps, cost = 0, 0.0\n"
             "for _ in range(1000):\n"
             "    s = mock_step(); steps += 1; cost += s['cost']\n"
             "    if not s['wants_more']:\n        break\n"
             "print(f'runaway ran {steps} steps, ${cost:.2f} — it never stops on its own')"),
        turn(
            "# 👉 Your turn (1): add enforce_caps so the loop HALTS at 5 steps OR $0.30.\n"
            "steps, cost = 0, 0.0\n"
            "for _ in range(1000):\n"
            "    s = mock_step(); steps += 1; cost += s['cost']\n"
            "    reason = ...  # TODO call enforce_caps(steps, cost, max_steps=5, max_cost_usd=0.30)\n"
            "    if reason:\n        print('HALTED:', reason); break",
            "steps, cost = 0, 0.0\n"
            "for _ in range(1000):\n"
            "    s = mock_step(); steps += 1; cost += s['cost']\n"
            "    reason = enforce_caps(steps, cost, max_steps=5, max_cost_usd=0.30)\n"
            "    if reason:\n        print('HALTED:', reason); break"),
        turn(
            "# 👉 Your turn (2): which cap fired first — steps or cost? Lower max_cost to 0.20 and rerun.\n"
            "# What halts it now? (predict before running)\n"
            "reason = enforce_caps(5, 0.50, max_steps=5, max_cost_usd=0.20)\n"
            "print(reason)  # 👉 is it the step cap or the cost cap?",
            "# cost cap is checked after step cap in enforce_caps, so at (5, 0.50) the STEP cap fires first.\n"
            "print(enforce_caps(5, 0.50, max_steps=5, max_cost_usd=0.20))      # max_steps\n"
            "print(enforce_caps(3, 0.50, max_steps=5, max_cost_usd=0.20))      # max_cost"),
        md("### 🔎 Eyeball your output\n"
           "The runaway prints ~1000 steps. The capped loop should print "
           "`HALTED: max_cost ($0.3) reached` at step 3 (3 × $0.10 = $0.30) — the cost "
           "cap bites before the step cap here. That's the safety net that keeps a stuck "
           "agent from burning your budget."),
    ])


# ---------------------------------------------------------------------------
# Notebook assembly
# ---------------------------------------------------------------------------
def make_cell(cell_type, source):
    cell = {"cell_type": cell_type, "metadata": {}, "source": source.splitlines(keepends=True)}
    if cell_type == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    return cell


def build(vid, spec, answers):
    cells = []
    for c in spec["cells"]:
        if c[0] == "md":
            cells.append(make_cell("markdown", c[1]))
        elif c[0] == "code":
            cells.append(make_cell("code", c[1]))
        elif c[0] == "turn":
            cells.append(make_cell("code", c[2] if answers else c[1]))
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
            "lab_id": spec["lab_id"],
            "variant": "answers" if answers else "clean",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    suffix = "answers" if answers else "clean"
    path = os.path.join(HERE, f"lab_{vid}_{suffix}.ipynb")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(nb, fh, indent=1)
    return path


def main():
    written = []
    for vid, spec in LABS.items():
        written.append(build(vid, spec, answers=False))
        written.append(build(vid, spec, answers=True))
    for p in written:
        print("wrote", os.path.basename(p))
    print(f"\n{len(written)} notebooks ({len(LABS)} labs x 2 variants)")


if __name__ == "__main__":
    main()
