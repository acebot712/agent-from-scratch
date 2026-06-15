"""Generate the 24 Udemy DETERMINISTIC coding exercises.

Run:  python udemy_exercises/_build_exercises.py

Each exercise folder (ex_v<m>_<n>_<slug>/) gets exactly:
    starter.py        framing code the learner sees, target function stubbed
    solution.py       reference solution (self-contained)
    evaluation.py     unit tests (one assertion each) that `from solution import ...`
    exercise_meta.md  title / objective / statement / 2 hints / explanation

Constraints (Udemy sandbox): Python 3.10, stdlib + numpy only, no network, fully
deterministic, self-contained (NO import from the `agent` framework). Generated
code uses only `#` comments (no docstrings) so this generator's strings don't
collide with triple quotes.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

EXERCISES = []


def ex(folder, exid, source, imports, title, objective, statement,
       starter, solution, tests, hints, explanation):
    EXERCISES.append(dict(
        folder=folder, exid=exid, source=source, imports=imports, title=title,
        objective=objective, statement=statement, starter=starter,
        solution=solution, tests=tests, hints=hints, explanation=explanation))


# ============================ MODULE 1 ====================================

ex("ex_v1_2_normalize_llm_response", "EX1.1", "V1.2", "normalize_llm_response",
   "Normalise an LLM response",
   "Normalise a raw OpenAI-style response dict into one standard shape.",
   "Different providers return different JSON. Write `normalize_llm_response(raw)` "
   "that maps an OpenAI-style raw dict to a normalised dict with keys `text` "
   "(str, '' if null), `tool_calls` (list of `{'name', 'args'}` with `args` parsed "
   "from the JSON `arguments` string), and `stop_reason` (the `finish_reason`).",
   # starter
   "import json\n\n"
   "def normalize_llm_response(raw):\n"
   "    # raw is an OpenAI-style dict: {'choices': [{'message': {...}, 'finish_reason': ...}]}\n"
   "    # Return {'text': str, 'tool_calls': [{'name','args'}], 'stop_reason': ...}.\n"
   "    raise NotImplementedError\n",
   # solution
   "import json\n\n"
   "def normalize_llm_response(raw):\n"
   "    choice = raw['choices'][0]\n"
   "    msg = choice.get('message', {})\n"
   "    tool_calls = []\n"
   "    for tc in msg.get('tool_calls') or []:\n"
   "        fn = tc.get('function', {})\n"
   "        args = fn.get('arguments') or '{}'\n"
   "        try:\n"
   "            args = json.loads(args)\n"
   "        except (json.JSONDecodeError, TypeError):\n"
   "            args = {}\n"
   "        tool_calls.append({'name': fn.get('name', ''), 'args': args})\n"
   "    return {\n"
   "        'text': msg.get('content') or '',\n"
   "        'tool_calls': tool_calls,\n"
   "        'stop_reason': choice.get('finish_reason'),\n"
   "    }\n",
   # tests
   [("test_extracts_text",
     "raw = {'choices': [{'message': {'content': 'hello'}, 'finish_reason': 'stop'}]}\n"
     "self.assertEqual(normalize_llm_response(raw)['text'], 'hello')"),
    ("test_null_content_becomes_empty_string",
     "raw = {'choices': [{'message': {'content': None}, 'finish_reason': 'stop'}]}\n"
     "self.assertEqual(normalize_llm_response(raw)['text'], '')"),
    ("test_maps_stop_reason",
     "raw = {'choices': [{'message': {'content': 'x'}, 'finish_reason': 'length'}]}\n"
     "self.assertEqual(normalize_llm_response(raw)['stop_reason'], 'length')"),
    ("test_parses_tool_call_arguments_to_dict",
     "raw = {'choices': [{'message': {'content': None, 'tool_calls': [\n"
     "    {'function': {'name': 'add', 'arguments': '{\"a\": 1, \"b\": 2}'}}]},\n"
     "    'finish_reason': 'tool_calls'}]}\n"
     "out = normalize_llm_response(raw)\n"
     "self.assertEqual(out['tool_calls'], [{'name': 'add', 'args': {'a': 1, 'b': 2}}])")],
   ["The raw shape is `raw['choices'][0]['message']` for content/tool_calls and "
    "`raw['choices'][0]['finish_reason']` for the stop reason.",
    "Tool-call `arguments` arrives as a JSON *string* — `json.loads` it into a dict."],
   "We dig into the first choice, coerce a missing/None `content` to `''`, and parse "
   "each tool call's `arguments` JSON string into a real dict. Normalising here means "
   "the rest of the agent never has to know which provider produced the response.")

ex("ex_v1_3_parse_intent", "EX1.2", "V1.3", "parse_intent",
   "Parse the model's intent",
   "Extract a structured action or final answer from a free-text response.",
   "Write `parse_intent(text)` returning a dict: if `text` contains "
   "`FINAL ANSWER:` return `{'kind': 'final', 'value': <text after the marker, "
   "stripped>}`; else if it matches `ACTION: name(args)` return "
   "`{'kind': 'action', 'name': name, 'args_text': args}`; otherwise "
   "`{'kind': 'unknown'}`.",
   "import re\n\n"
   "def parse_intent(text):\n"
   "    # Return a 'final', 'action', or 'unknown' intent dict (see the statement).\n"
   "    raise NotImplementedError\n",
   "import re\n\n"
   "def parse_intent(text):\n"
   "    if 'FINAL ANSWER:' in text:\n"
   "        return {'kind': 'final', 'value': text.split('FINAL ANSWER:', 1)[1].strip()}\n"
   "    m = re.search(r'ACTION:\\s*([A-Za-z0-9_]+)\\((.*)\\)', text)\n"
   "    if m:\n"
   "        return {'kind': 'action', 'name': m.group(1), 'args_text': m.group(2).strip()}\n"
   "    return {'kind': 'unknown'}\n",
   [("test_detects_final_answer",
     "self.assertEqual(parse_intent('done. FINAL ANSWER: 42'),\n"
     "                 {'kind': 'final', 'value': '42'})"),
    ("test_detects_action_name",
     "self.assertEqual(parse_intent('ACTION: get_weather(\"Paris\")')['name'], 'get_weather')"),
    ("test_action_captures_args_text",
     "self.assertEqual(parse_intent('ACTION: add(2, 3)')['args_text'], '2, 3')"),
    ("test_unknown_when_neither",
     "self.assertEqual(parse_intent('just chatting'), {'kind': 'unknown'})")],
   ["Check for the `FINAL ANSWER:` marker first; `str.split(marker, 1)[1]` gives you "
    "everything after it.",
    "For actions use a regex like `ACTION:\\s*(\\w+)\\((.*)\\)` and read groups 1 and 2."],
   "Intent parsing turns free text into a decision the loop can act on. We check the "
   "terminal marker first (so a response that both reasons and concludes is treated as "
   "final), then fall back to an `ACTION:` regex, then to `unknown`.")

ex("ex_v1_4_stopping_condition", "EX1.3", "V1.4", "should_stop",
   "The stopping condition",
   "Implement a terminal-state check that ends the agent loop correctly.",
   "Write `should_stop(text, step, max_steps)` returning `True` when the loop should "
   "end: either `step >= max_steps` (safety cap) OR `text` contains `FINAL ANSWER:`. "
   "Otherwise `False`.",
   "def should_stop(text, step, max_steps):\n"
   "    # Return True if the loop should terminate this step.\n"
   "    raise NotImplementedError\n",
   "def should_stop(text, step, max_steps):\n"
   "    if step >= max_steps:\n"
   "        return True\n"
   "    if 'FINAL ANSWER:' in text:\n"
   "        return True\n"
   "    return False\n",
   [("test_stops_on_final_answer",
     "self.assertTrue(should_stop('FINAL ANSWER: 7', 1, 6))"),
    ("test_stops_at_step_cap",
     "self.assertTrue(should_stop('still going', 6, 6))"),
    ("test_continues_midway",
     "self.assertFalse(should_stop('thinking', 2, 6))"),
    ("test_step_cap_takes_priority_over_text",
     "self.assertTrue(should_stop('no marker here', 10, 6))")],
   ["Two independent reasons to stop — combine them with `or` (or two `if` returns).",
    "Use `>=` for the step cap so the loop can never run past `max_steps`."],
   "A loop without a correct terminal check either stops too early or never stops. We "
   "stop on the explicit completion marker, and always stop at the step cap as a "
   "safety net against a model that never signals done.")

# ============================ MODULE 2 ====================================

ex("ex_v2_4_parse_tool_call", "EX2.1", "V2.4", "parse_tool_call",
   "Parse a tool call",
   "Parse a hand-rolled tool request into a structured {name, args} object.",
   "Write `parse_tool_call(text)`. A tool request looks like two lines:\n\n"
   "    TOOL: <name>\n    ARGS: {\"json\": \"object\"}\n\n"
   "Return `{'name': name, 'args': <parsed dict>}`. If there is no `ARGS:` line, "
   "use `{}`. If the args JSON is malformed, use `{}`. Return `None` when there is "
   "no `TOOL:` line at all.",
   "import json\nimport re\n\n"
   "def parse_tool_call(text):\n"
   "    # Return {'name', 'args'} or None if there is no TOOL: line.\n"
   "    raise NotImplementedError\n",
   "import json\nimport re\n\n"
   "def parse_tool_call(text):\n"
   "    m_name = re.search(r'TOOL:\\s*([A-Za-z0-9_\\-]+)', text)\n"
   "    if not m_name:\n"
   "        return None\n"
   "    m_args = re.search(r'ARGS:\\s*(\\{.*\\})\\s*$', text, re.DOTALL)\n"
   "    args = {}\n"
   "    if m_args:\n"
   "        try:\n"
   "            parsed = json.loads(m_args.group(1))\n"
   "            args = parsed if isinstance(parsed, dict) else {}\n"
   "        except json.JSONDecodeError:\n"
   "            args = {}\n"
   "    return {'name': m_name.group(1), 'args': args}\n",
   [("test_parses_name_and_args",
     "self.assertEqual(parse_tool_call('TOOL: add\\nARGS: {\"a\": 2, \"b\": 3}'),\n"
     "                 {'name': 'add', 'args': {'a': 2, 'b': 3}})"),
    ("test_none_when_no_tool_line",
     "self.assertIsNone(parse_tool_call('The answer is 5.'))"),
    ("test_empty_args_when_no_args_line",
     "self.assertEqual(parse_tool_call('TOOL: now')['args'], {})"),
    ("test_malformed_json_degrades_to_empty",
     "self.assertEqual(parse_tool_call('TOOL: add\\nARGS: {not json}')['args'], {})")],
   ["Search for the `TOOL:` name first; return `None` immediately if it's absent.",
    "Wrap `json.loads` in try/except so malformed args fall back to `{}` instead of "
    "raising."],
   "This is native function calling, done by hand. We extract the tool name with one "
   "regex and the JSON args with another, parsing defensively so a model that emits "
   "broken JSON gives us an empty-args call rather than a crash.")

ex("ex_v2_5_tool_registry", "EX2.2", "V2.5", "ToolRegistry",
   "A tool registry",
   "Register tools by name and call the right one by name.",
   "Implement a `ToolRegistry` class with: `register(name, fn)` (raise `ValueError` "
   "on a duplicate name), `has(name) -> bool`, `names() -> sorted list`, and "
   "`call(name, **kwargs)` which runs the registered function (raise `KeyError` for "
   "an unknown name).",
   "class ToolRegistry:\n"
   "    def __init__(self):\n"
   "        self._tools = {}\n\n"
   "    def register(self, name, fn):\n"
   "        raise NotImplementedError\n\n"
   "    def has(self, name):\n"
   "        raise NotImplementedError\n\n"
   "    def names(self):\n"
   "        raise NotImplementedError\n\n"
   "    def call(self, name, **kwargs):\n"
   "        raise NotImplementedError\n",
   "class ToolRegistry:\n"
   "    def __init__(self):\n"
   "        self._tools = {}\n\n"
   "    def register(self, name, fn):\n"
   "        if name in self._tools:\n"
   "            raise ValueError('already registered: ' + name)\n"
   "        self._tools[name] = fn\n\n"
   "    def has(self, name):\n"
   "        return name in self._tools\n\n"
   "    def names(self):\n"
   "        return sorted(self._tools)\n\n"
   "    def call(self, name, **kwargs):\n"
   "        if name not in self._tools:\n"
   "            raise KeyError(name)\n"
   "        return self._tools[name](**kwargs)\n",
   [("test_register_then_call",
     "reg = ToolRegistry(); reg.register('add', lambda a, b: a + b)\n"
     "self.assertEqual(reg.call('add', a=2, b=3), 5)"),
    ("test_names_are_sorted",
     "reg = ToolRegistry(); reg.register('b', lambda: 1); reg.register('a', lambda: 2)\n"
     "self.assertEqual(reg.names(), ['a', 'b'])"),
    ("test_duplicate_registration_raises",
     "reg = ToolRegistry(); reg.register('x', lambda: 1)\n"
     "self.assertRaises(ValueError, reg.register, 'x', lambda: 2)"),
    ("test_unknown_call_raises_keyerror",
     "reg = ToolRegistry()\n"
     "self.assertRaises(KeyError, reg.call, 'ghost')")],
   ["Back the registry with a plain dict: name -> function.",
    "`call` should look the name up, raise `KeyError` if missing, else invoke "
    "`fn(**kwargs)`."],
   "The registry is the lookup table that turns a parsed tool name into an actual "
   "callable. Guarding duplicate registration and unknown calls keeps dispatch "
   "predictable as the toolset grows.")

ex("ex_v2_7_dispatch_unknown_tool", "EX2.3", "V2.5 + V2.7", "dispatch",
   "Dispatch with graceful failure",
   "Dispatch a parsed call and handle unknown tools and bad args gracefully.",
   "Write `dispatch(registry, name, args)` where `registry` is a dict of "
   "`name -> callable`. Return `{'ok': True, 'output': <result>}` on success. For an "
   "unknown tool return `{'ok': False, 'error': <message containing 'unknown'>}`. If "
   "the call raises `TypeError` (wrong/missing args) return "
   "`{'ok': False, 'error': <message containing 'bad arguments'>}`.",
   "def dispatch(registry, name, args):\n"
   "    # registry: {name: callable}. Never raise — return an ok/error dict.\n"
   "    raise NotImplementedError\n",
   "def dispatch(registry, name, args):\n"
   "    if name not in registry:\n"
   "        return {'ok': False, 'error': \"unknown tool '\" + name + \"'\"}\n"
   "    try:\n"
   "        output = registry[name](**args)\n"
   "    except TypeError as exc:\n"
   "        return {'ok': False, 'error': 'bad arguments: ' + str(exc)}\n"
   "    return {'ok': True, 'output': output}\n",
   [("test_runs_known_tool",
     "reg = {'add': lambda a, b: a + b}\n"
     "self.assertEqual(dispatch(reg, 'add', {'a': 2, 'b': 3}), {'ok': True, 'output': 5})"),
    ("test_unknown_tool_is_not_ok",
     "self.assertFalse(dispatch({}, 'ghost', {})['ok'])"),
    ("test_unknown_tool_error_mentions_unknown",
     "self.assertIn('unknown', dispatch({}, 'ghost', {})['error'])"),
    ("test_bad_arguments_handled",
     "reg = {'add': lambda a, b: a + b}\n"
     "self.assertIn('bad arguments', dispatch(reg, 'add', {'a': 1})['error'])")],
   ["Check membership before calling; an unknown name should never reach the "
    "function.",
    "Wrap the `fn(**args)` call in try/except TypeError to catch wrong/missing "
    "keyword arguments."],
   "Models hallucinate tool names and emit wrong arguments. Dispatch converts both "
   "failure modes into a structured error dict the loop can feed back to the model, "
   "instead of crashing the agent.")

# ============================ MODULE 3 ====================================

ex("ex_v3_2_context_budget_trim", "EX3.3", "V3.2", "context_budget_trim, count_tokens",
   "Trim history to a token budget",
   "Trim a message history to fit a token budget, keeping the most recent turns.",
   "Using the provided `count_tokens` proxy (word count), write "
   "`context_budget_trim(messages, budget)`. Keep a leading `system` message if "
   "present, then keep the most recent messages whose combined token count fits "
   "within `budget`. Return the kept messages in original order. Return `[]` if "
   "`budget <= 0`.",
   "def count_tokens(text):\n"
   "    # Provided proxy: ~1 token per whitespace word (no external tokenizer).\n"
   "    return len(text.split())\n\n"
   "def context_budget_trim(messages, budget):\n"
   "    # Keep the system message + the most recent messages that fit the budget.\n"
   "    raise NotImplementedError\n",
   "def count_tokens(text):\n"
   "    return len(text.split())\n\n"
   "def context_budget_trim(messages, budget):\n"
   "    if budget <= 0:\n"
   "        return []\n"
   "    system = []\n"
   "    rest = list(messages)\n"
   "    if rest and rest[0].get('role') == 'system':\n"
   "        system = [rest.pop(0)]\n"
   "    remaining = budget - sum(count_tokens(m.get('content', '')) for m in system)\n"
   "    kept = []\n"
   "    for m in reversed(rest):\n"
   "        cost = count_tokens(m.get('content', ''))\n"
   "        if cost <= remaining:\n"
   "            kept.append(m)\n"
   "            remaining -= cost\n"
   "        else:\n"
   "            break\n"
   "    return system + list(reversed(kept))\n",
   [("test_keeps_system_message",
     "msgs = [{'role': 'system', 'content': 'sys'}, {'role': 'user', 'content': 'a b c'}]\n"
     "self.assertEqual(context_budget_trim(msgs, 5)[0]['role'], 'system')"),
    ("test_prefers_recent_messages",
     "msgs = [{'role': 'user', 'content': 'one two three'}, {'role': 'user', 'content': 'four'}]\n"
     "self.assertEqual(context_budget_trim(msgs, 1)[-1]['content'], 'four')"),
    ("test_respects_budget",
     "msgs = [{'role': 'user', 'content': 'a b'}, {'role': 'user', 'content': 'c d'}]\n"
     "kept = context_budget_trim(msgs, 2)\n"
     "self.assertLessEqual(sum(count_tokens(m['content']) for m in kept), 2)"),
    ("test_zero_budget_returns_empty",
     "self.assertEqual(context_budget_trim([{'role': 'user', 'content': 'x'}], 0), [])")],
   ["Pop the system message aside first, then iterate the rest in reverse so you add "
    "the newest messages until the budget runs out.",
    "Accumulate kept messages while a running `remaining` counter stays >= each "
    "message's cost; reverse them back at the end to restore order."],
   "The context window is a budget. We protect the system instruction, then greedily "
   "keep the freshest turns that fit — older context is the first to go, which is "
   "usually what you want.")

ex("ex_v3_4_cosine_similarity", "EX3.1", "V3.4", "cosine_similarity",
   "Cosine similarity in numpy",
   "Compute cosine similarity between two vectors from scratch in numpy.",
   "Write `cosine_similarity(a, b)` returning the cosine of the angle between two "
   "vectors as a float: dot(a, b) / (||a|| * ||b||). If either vector has zero "
   "magnitude, return `0.0` (avoid dividing by zero).",
   "import numpy as np\n\n"
   "def cosine_similarity(a, b):\n"
   "    # dot(a, b) / (norm(a) * norm(b)), with a zero-vector guard returning 0.0\n"
   "    raise NotImplementedError\n",
   "import numpy as np\n\n"
   "def cosine_similarity(a, b):\n"
   "    a = np.asarray(a, dtype=float)\n"
   "    b = np.asarray(b, dtype=float)\n"
   "    denom = np.linalg.norm(a) * np.linalg.norm(b)\n"
   "    if denom == 0:\n"
   "        return 0.0\n"
   "    return float(np.dot(a, b) / denom)\n",
   [("test_identical_vectors_are_one",
     "self.assertAlmostEqual(cosine_similarity([1, 2, 3], [1, 2, 3]), 1.0)"),
    ("test_orthogonal_vectors_are_zero",
     "self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)"),
    ("test_opposite_vectors_are_minus_one",
     "self.assertAlmostEqual(cosine_similarity([1, 0], [-1, 0]), -1.0)"),
    ("test_zero_vector_guard",
     "self.assertEqual(cosine_similarity([0, 0], [1, 1]), 0.0)")],
   ["`np.dot` gives the numerator; `np.linalg.norm` gives each magnitude.",
    "Guard the denominator: if it's 0, return 0.0 before dividing."],
   "Cosine similarity measures direction, not magnitude — it's the workhorse of "
   "semantic retrieval. Casting to float arrays and guarding the zero vector keeps it "
   "robust on real (and degenerate) embeddings.")

ex("ex_v3_5_top_k_retrieval", "EX3.2", "V3.5", "top_k_retrieval",
   "Top-k retrieval",
   "Rank document vectors by similarity to a query and return the top-k.",
   "Given a `query_vec` and a list of precomputed `doc_vecs`, write "
   "`top_k_retrieval(query_vec, doc_vecs, k)` returning a list of `(index, score)` "
   "tuples for the `k` most similar docs, sorted by score descending. Use cosine "
   "similarity. Input is **vectors**, not text.",
   "import numpy as np\n\n"
   "def cosine(a, b):\n"
   "    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)\n"
   "    d = np.linalg.norm(a) * np.linalg.norm(b)\n"
   "    return 0.0 if d == 0 else float(np.dot(a, b) / d)\n\n"
   "def top_k_retrieval(query_vec, doc_vecs, k):\n"
   "    # Return [(index, score), ...] for the top-k docs, best first.\n"
   "    raise NotImplementedError\n",
   "import numpy as np\n\n"
   "def cosine(a, b):\n"
   "    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)\n"
   "    d = np.linalg.norm(a) * np.linalg.norm(b)\n"
   "    return 0.0 if d == 0 else float(np.dot(a, b) / d)\n\n"
   "def top_k_retrieval(query_vec, doc_vecs, k):\n"
   "    scored = [(i, cosine(query_vec, v)) for i, v in enumerate(doc_vecs)]\n"
   "    scored.sort(key=lambda t: t[1], reverse=True)\n"
   "    return scored[:max(0, k)]\n",
   [("test_returns_k_results",
     "docs = [[1, 0], [0, 1], [1, 1]]\n"
     "self.assertEqual(len(top_k_retrieval([1, 0], docs, 2)), 2)"),
    ("test_best_match_first",
     "docs = [[0, 1], [1, 0.1], [0.9, 0]]\n"
     "self.assertEqual(top_k_retrieval([1, 0], docs, 1)[0][0], 2)"),
    ("test_sorted_descending",
     "docs = [[0, 1], [1, 0.1], [0.9, 0]]\n"
     "scores = [s for _, s in top_k_retrieval([1, 0], docs, 3)]\n"
     "self.assertEqual(scores, sorted(scores, reverse=True))"),
    ("test_k_zero_returns_empty",
     "self.assertEqual(top_k_retrieval([1, 0], [[1, 0]], 0), [])")],
   ["Score every doc with the provided `cosine`, keeping its index alongside the "
    "score.",
    "Sort the `(index, score)` pairs by score descending, then slice `[:k]`."],
   "Retrieval without a vector DB is just: score all candidates, sort, take the top "
   "few. Keeping the index lets the caller map a hit back to its source document.")

ex("ex_v3_6_episodic_serialize", "EX3.4", "V3.6", "serialize_episodes, deserialize_episodes",
   "Serialise episodic memory",
   "Serialise and reload a list of episodes so memory survives across sessions.",
   "Write `serialize_episodes(episodes)` returning a JSON string, and "
   "`deserialize_episodes(blob)` returning the list back. An episode is a dict like "
   "`{'role': ..., 'content': ..., 'meta': {...}}`. The round-trip must preserve the "
   "data, and `deserialize_episodes` must accept an empty/whitespace string and "
   "return `[]`.",
   "import json\n\n"
   "def serialize_episodes(episodes):\n"
   "    # Return a JSON string for the list of episode dicts.\n"
   "    raise NotImplementedError\n\n"
   "def deserialize_episodes(blob):\n"
   "    # Inverse of serialize_episodes; '' or whitespace -> [].\n"
   "    raise NotImplementedError\n",
   "import json\n\n"
   "def serialize_episodes(episodes):\n"
   "    return json.dumps(episodes, indent=2)\n\n"
   "def deserialize_episodes(blob):\n"
   "    if not blob.strip():\n"
   "        return []\n"
   "    return json.loads(blob)\n",
   [("test_round_trip_preserves_data",
     "eps = [{'role': 'user', 'content': 'hi', 'meta': {'step': 1}}]\n"
     "self.assertEqual(deserialize_episodes(serialize_episodes(eps)), eps)"),
    ("test_serialize_returns_string",
     "self.assertIsInstance(serialize_episodes([]), str)"),
    ("test_empty_string_deserialises_to_empty_list",
     "self.assertEqual(deserialize_episodes('   '), [])"),
    ("test_output_is_valid_json",
     "import json as _j\n"
     "self.assertEqual(_j.loads(serialize_episodes([{'a': 1}])), [{'a': 1}])")],
   ["`json.dumps` / `json.loads` handle the whole list at once — no need to walk "
    "fields.",
    "Guard the empty case in `deserialize_episodes` before calling `json.loads`, "
    "since `json.loads('')` raises."],
   "Persistence is what lets an agent remember across runs. JSON is enough for a list "
   "of plain dicts; the only sharp edge is an empty file, which we map to an empty "
   "list instead of letting it raise.")

# ============================ MODULE 4 ====================================

ex("ex_v4_3_parse_react_trace", "EX4.1", "V4.3", "parse_react_trace",
   "Parse a ReAct trace",
   "Parse Thought / Action / Observation lines into structured steps.",
   "Write `parse_react_trace(text)` returning a list of step dicts. A step may have "
   "`thought`, `action`, `action_input`, `observation`. Actions look like "
   "`Action: name[input]`. An `Observation:` line closes the current step; a new "
   "`Thought:` also starts a new step if the current one already has content.",
   "import re\n\n"
   "def parse_react_trace(text):\n"
   "    # Return a list of {thought?, action?, action_input?, observation?} dicts.\n"
   "    raise NotImplementedError\n",
   "import re\n\n"
   "_THOUGHT = re.compile(r'Thought:\\s*(.+)')\n"
   "_ACTION = re.compile(r'Action:\\s*([A-Za-z0-9_\\-]+)\\s*\\[(.*?)\\]')\n"
   "_OBS = re.compile(r'Observation:\\s*(.+)')\n\n"
   "def parse_react_trace(text):\n"
   "    steps = []\n"
   "    cur = {}\n"
   "    for line in text.splitlines():\n"
   "        line = line.strip()\n"
   "        if not line:\n"
   "            continue\n"
   "        m = _THOUGHT.match(line)\n"
   "        if m:\n"
   "            if cur.get('thought') or cur.get('action'):\n"
   "                steps.append(cur); cur = {}\n"
   "            cur['thought'] = m.group(1).strip(); continue\n"
   "        m = _ACTION.match(line)\n"
   "        if m:\n"
   "            cur['action'] = m.group(1).strip()\n"
   "            cur['action_input'] = m.group(2).strip(); continue\n"
   "        m = _OBS.match(line)\n"
   "        if m:\n"
   "            cur['observation'] = m.group(1).strip()\n"
   "            steps.append(cur); cur = {}\n"
   "    if cur.get('thought') or cur.get('action'):\n"
   "        steps.append(cur)\n"
   "    return steps\n",
   [("test_parses_action_name",
     "steps = parse_react_trace('Thought: add them\\nAction: add[2, 3]\\nObservation: 5')\n"
     "self.assertEqual(steps[0]['action'], 'add')"),
    ("test_parses_action_input",
     "steps = parse_react_trace('Action: add[2, 3]\\nObservation: 5')\n"
     "self.assertEqual(steps[0]['action_input'], '2, 3')"),
    ("test_observation_closes_step",
     "steps = parse_react_trace('Thought: a\\nAction: x[1]\\nObservation: ok')\n"
     "self.assertEqual(steps[0]['observation'], 'ok')"),
    ("test_two_steps",
     "text = 'Thought: a\\nAction: x[1]\\nObservation: o1\\nThought: b\\nAction: y[2]\\nObservation: o2'\n"
     "self.assertEqual(len(parse_react_trace(text)), 2)")],
   ["Match each line type with its own regex; the action regex needs two groups: "
    "name and the text inside `[...]`.",
    "Accumulate into a `cur` dict; push it to the list and reset on `Observation:` "
    "(and when a new `Thought:` begins a non-empty step)."],
   "ReAct interleaves reasoning and acting. Parsing the trace into discrete steps is "
   "what lets the loop pull out the next action to run and attach the observation back "
   "to the right place.")

ex("ex_v4_4_retry_budget", "EX4.2", "V4.4", "RetryBudget",
   "A retry budget",
   "Implement the bounded retry counter at the core of a reflection loop.",
   "Implement a `RetryBudget` class constructed with `max_retries`. Provide "
   "`can_retry() -> bool` (True while fewer than `max_retries` have been used), "
   "`consume() -> bool` (use one retry; return True if one was available, else "
   "False), and a `remaining` property.",
   "class RetryBudget:\n"
   "    def __init__(self, max_retries):\n"
   "        self.max_retries = max_retries\n"
   "        self.used = 0\n\n"
   "    def can_retry(self):\n"
   "        raise NotImplementedError\n\n"
   "    def consume(self):\n"
   "        raise NotImplementedError\n\n"
   "    @property\n"
   "    def remaining(self):\n"
   "        raise NotImplementedError\n",
   "class RetryBudget:\n"
   "    def __init__(self, max_retries):\n"
   "        self.max_retries = max_retries\n"
   "        self.used = 0\n\n"
   "    def can_retry(self):\n"
   "        return self.used < self.max_retries\n\n"
   "    def consume(self):\n"
   "        if not self.can_retry():\n"
   "            return False\n"
   "        self.used += 1\n"
   "        return True\n\n"
   "    @property\n"
   "    def remaining(self):\n"
   "        return max(0, self.max_retries - self.used)\n",
   [("test_can_retry_initially",
     "self.assertTrue(RetryBudget(2).can_retry())"),
    ("test_consume_returns_true_while_available",
     "b = RetryBudget(2)\n"
     "self.assertTrue(b.consume() and b.consume())"),
    ("test_consume_false_past_budget",
     "b = RetryBudget(1); b.consume()\n"
     "self.assertFalse(b.consume())"),
    ("test_remaining_counts_down",
     "b = RetryBudget(3); b.consume()\n"
     "self.assertEqual(b.remaining, 2)")],
   ["Track a `used` counter; `can_retry` compares it to `max_retries`.",
    "`consume` should refuse (return False) once the budget is exhausted, without "
    "incrementing past the cap."],
   "Reflection means critique-and-retry, but only within a budget — otherwise a model "
   "that can't fix its output loops forever. This counter is the deterministic core "
   "the rest of the reflection loop is built on.")

ex("ex_v4_6_select_strategy", "EX4.3", "V4.6", "select_strategy",
   "Select a reasoning strategy",
   "Pick a reasoning strategy from task metadata with rule-based logic.",
   "Write `select_strategy(meta)` (a dict) returning one of `'react'`, "
   "`'reflection'`, `'tot'`, `'direct'`. Rules, in order: if `meta['needs_tools']` "
   "-> `'react'`; elif `meta['verifiable']` and `meta['difficulty'] == 'hard'` -> "
   "`'reflection'`; elif `meta['open_ended']` or `meta['branching']` -> `'tot'`; "
   "else `'direct'`. Missing keys are falsy.",
   "def select_strategy(meta):\n"
   "    # Return 'react' | 'reflection' | 'tot' | 'direct' per the rules.\n"
   "    raise NotImplementedError\n",
   "def select_strategy(meta):\n"
   "    if meta.get('needs_tools'):\n"
   "        return 'react'\n"
   "    if meta.get('verifiable') and meta.get('difficulty') == 'hard':\n"
   "        return 'reflection'\n"
   "    if meta.get('open_ended') or meta.get('branching'):\n"
   "        return 'tot'\n"
   "    return 'direct'\n",
   [("test_tools_means_react",
     "self.assertEqual(select_strategy({'needs_tools': True}), 'react')"),
    ("test_hard_verifiable_means_reflection",
     "self.assertEqual(select_strategy({'verifiable': True, 'difficulty': 'hard'}), 'reflection')"),
    ("test_open_ended_means_tot",
     "self.assertEqual(select_strategy({'open_ended': True}), 'tot')"),
    ("test_default_is_direct",
     "self.assertEqual(select_strategy({}), 'direct')")],
   ["Use `meta.get(key)` so missing keys read as falsy instead of raising "
    "`KeyError`.",
    "Order matters — check the rules top to bottom and return on the first match."],
   "Not every task needs the heaviest reasoning. A cheap rule-based router sends "
   "tool tasks to ReAct, hard verifiable tasks to reflection, branching tasks to "
   "tree-of-thoughts, and everything else to a single direct call.")

# ============================ MODULE 5 ====================================

ex("ex_v5_3_route_message", "EX5.1", "V5.3", "route_message",
   "Route a message",
   "Route a structured message to the agent named as its recipient.",
   "Write `route_message(message, roles)` where `message` is a dict with a "
   "`recipient` key and `roles` maps role name -> handler. Return the handler for "
   "the recipient. Raise `KeyError` if no such role exists.",
   "def route_message(message, roles):\n"
   "    # Return roles[message['recipient']]; raise KeyError if absent.\n"
   "    raise NotImplementedError\n",
   "def route_message(message, roles):\n"
   "    recipient = message['recipient']\n"
   "    if recipient not in roles:\n"
   "        raise KeyError(\"no agent for role '\" + str(recipient) + \"'\")\n"
   "    return roles[recipient]\n",
   [("test_routes_to_recipient",
     "self.assertEqual(route_message({'recipient': 'writer'}, {'writer': 'W'}), 'W')"),
    ("test_unknown_recipient_raises",
     "self.assertRaises(KeyError, route_message, {'recipient': 'ghost'}, {'writer': 'W'})"),
    ("test_picks_correct_among_many",
     "roles = {'a': 1, 'b': 2, 'c': 3}\n"
     "self.assertEqual(route_message({'recipient': 'b'}, roles), 2)")],
   ["Read `message['recipient']`, then look it up in `roles`.",
    "Check membership first so a missing recipient raises a clear `KeyError` rather "
    "than returning `None`."],
   "Message passing is how agents coordinate. Routing is deliberately strict — an "
   "unroutable message is a bug, so we surface it loudly instead of silently dropping "
   "the message.")

ex("ex_v5_4_delegation_cap", "EX5.2", "V5.4", "DelegationCap, DelegationError",
   "Cap delegation depth",
   "Enforce a delegation-depth cap to prevent runaway agent loops.",
   "Implement `DelegationError(RuntimeError)` and a `DelegationCap` class "
   "constructed with `max_depth` (and optional `depth=0`). `enter()` returns a NEW "
   "`DelegationCap` one level deeper, but raises `DelegationError` if the current "
   "depth is already at `max_depth`. `allows()` returns whether another level is "
   "permitted.",
   "class DelegationError(RuntimeError):\n"
   "    pass\n\n"
   "class DelegationCap:\n"
   "    def __init__(self, max_depth, depth=0):\n"
   "        self.max_depth = max_depth\n"
   "        self.depth = depth\n\n"
   "    def enter(self):\n"
   "        raise NotImplementedError\n\n"
   "    def allows(self):\n"
   "        raise NotImplementedError\n",
   "class DelegationError(RuntimeError):\n"
   "    pass\n\n"
   "class DelegationCap:\n"
   "    def __init__(self, max_depth, depth=0):\n"
   "        self.max_depth = max_depth\n"
   "        self.depth = depth\n\n"
   "    def enter(self):\n"
   "        if self.depth >= self.max_depth:\n"
   "            raise DelegationError('delegation depth cap exceeded')\n"
   "        return DelegationCap(self.max_depth, self.depth + 1)\n\n"
   "    def allows(self):\n"
   "        return self.depth < self.max_depth\n",
   [("test_enter_increments_depth",
     "self.assertEqual(DelegationCap(3).enter().depth, 1)"),
    ("test_enter_raises_past_cap",
     "cap = DelegationCap(2).enter().enter()\n"
     "self.assertRaises(DelegationError, cap.enter)"),
    ("test_allows_true_below_cap",
     "self.assertTrue(DelegationCap(1).allows())"),
    ("test_allows_false_at_cap",
     "self.assertFalse(DelegationCap(2, 2).allows())")],
   ["`enter` should return a fresh `DelegationCap` with `depth + 1`, not mutate "
    "`self` — that makes each delegation branch independent.",
    "Raise `DelegationError` when `depth >= max_depth` before descending."],
   "Multi-agent systems can recurse forever (A delegates to B delegates to A...). A "
   "depth cap that raises on the (max+1)th `enter` is the simplest reliable brake.")

ex("ex_v5_6_synthesize_outputs", "EX5.3", "V5.6", "synthesize_outputs",
   "Synthesise worker outputs",
   "Mechanically merge multiple worker outputs into one structured result.",
   "Write `synthesize_outputs(outputs, dedupe=True)`. Strip each output, drop "
   "blanks, and (when `dedupe`) remove duplicates while preserving first-seen order. "
   "Return `{'parts': [...], 'combined': '<newline-joined parts>', "
   "'count': <len(parts)>}`.",
   "def synthesize_outputs(outputs, dedupe=True):\n"
   "    # Trim, drop blanks, optionally dedupe (order-preserving), then combine.\n"
   "    raise NotImplementedError\n",
   "def synthesize_outputs(outputs, dedupe=True):\n"
   "    parts = []\n"
   "    seen = set()\n"
   "    for o in outputs:\n"
   "        o = (o or '').strip()\n"
   "        if not o:\n"
   "            continue\n"
   "        if dedupe and o in seen:\n"
   "            continue\n"
   "        seen.add(o)\n"
   "        parts.append(o)\n"
   "    return {'parts': parts, 'combined': '\\n'.join(parts), 'count': len(parts)}\n",
   [("test_dedupes_preserving_order",
     "self.assertEqual(synthesize_outputs(['a', 'b', 'a'])['parts'], ['a', 'b'])"),
    ("test_drops_blanks",
     "self.assertEqual(synthesize_outputs(['x', '', '  '])['parts'], ['x'])"),
    ("test_combined_is_newline_joined",
     "self.assertEqual(synthesize_outputs(['a', 'b'])['combined'], 'a\\nb')"),
    ("test_count_matches_parts",
     "out = synthesize_outputs(['a', 'b', 'a', 'c'])\n"
     "self.assertEqual(out['count'], 3)")],
   ["Track a `seen` set for dedupe, but still append to a list so order is "
    "preserved.",
    "Strip each output before the blank check so whitespace-only strings are "
    "dropped."],
   "This is the mechanical (graded) synthesis: deterministic combine/dedupe/order. "
   "It contrasts with an LLM writing a fused summary — useful, but not reproducible "
   "enough to autograde.")

# ============================ MODULE 6 ====================================

ex("ex_v6_4_success_rate", "EX6.1", "V6.4", "success_rate",
   "Success rate",
   "Compute the fraction of traces that succeeded.",
   "Write `success_rate(traces)` returning the fraction of traces whose `success` "
   "field is truthy, as a float. Return `0.0` for an empty list.",
   "def success_rate(traces):\n"
   "    # Fraction of traces with a truthy 'success' field; 0.0 if empty.\n"
   "    raise NotImplementedError\n",
   "def success_rate(traces):\n"
   "    if not traces:\n"
   "        return 0.0\n"
   "    return sum(1 for t in traces if t.get('success')) / len(traces)\n",
   [("test_all_success",
     "self.assertEqual(success_rate([{'success': True}, {'success': True}]), 1.0)"),
    ("test_half_success",
     "self.assertEqual(success_rate([{'success': True}, {'success': False}]), 0.5)"),
    ("test_empty_is_zero",
     "self.assertEqual(success_rate([]), 0.0)")],
   ["Count truthy `success` fields with a generator expression.",
    "Guard the empty list before dividing to avoid `ZeroDivisionError`."],
   "Success rate is the headline eval metric. The only edge case is the empty set, "
   "which we define as 0.0 rather than letting the division blow up.")

ex("ex_v6_4_step_efficiency", "EX6.2", "V6.4", "step_efficiency",
   "Step efficiency",
   "Compute the average number of steps taken by successful traces.",
   "Write `step_efficiency(traces)` returning the mean `steps` over the "
   "**successful** traces only (lower is better). Return `0.0` if there are no "
   "successful traces.",
   "def step_efficiency(traces):\n"
   "    # Mean 'steps' over successful traces; 0.0 if none succeeded.\n"
   "    raise NotImplementedError\n",
   "def step_efficiency(traces):\n"
   "    wins = [t for t in traces if t.get('success')]\n"
   "    if not wins:\n"
   "        return 0.0\n"
   "    return sum(t.get('steps', 0) for t in wins) / len(wins)\n",
   [("test_averages_successful_only",
     "traces = [{'success': True, 'steps': 2}, {'success': True, 'steps': 4},\n"
     "          {'success': False, 'steps': 99}]\n"
     "self.assertEqual(step_efficiency(traces), 3.0)"),
    ("test_no_success_is_zero",
     "self.assertEqual(step_efficiency([{'success': False, 'steps': 5}]), 0.0)"),
    ("test_single_success",
     "self.assertEqual(step_efficiency([{'success': True, 'steps': 7}]), 7.0)")],
   ["Filter to successful traces first; a failed run's step count would skew the "
    "measure.",
    "Average `steps` over that filtered list, guarding the empty case."],
   "Counting steps only on successes answers 'when it works, how efficiently?' — "
   "averaging in failures (which often hit the step cap) would muddy that signal.")

ex("ex_v6_4_cost_per_task", "EX6.3", "V6.4", "cost_per_task",
   "Cost per task",
   "Compute the average cost in dollars across all traces.",
   "Write `cost_per_task(traces)` returning the mean of the `cost_usd` field across "
   "all traces, as a float. Return `0.0` for an empty list.",
   "def cost_per_task(traces):\n"
   "    # Mean 'cost_usd' across all traces; 0.0 if empty.\n"
   "    raise NotImplementedError\n",
   "def cost_per_task(traces):\n"
   "    if not traces:\n"
   "        return 0.0\n"
   "    return sum(float(t.get('cost_usd', 0.0)) for t in traces) / len(traces)\n",
   [("test_averages_cost",
     "self.assertAlmostEqual(cost_per_task([{'cost_usd': 0.02}, {'cost_usd': 0.04}]), 0.03)"),
    ("test_empty_is_zero",
     "self.assertEqual(cost_per_task([]), 0.0)"),
    ("test_missing_cost_treated_as_zero",
     "self.assertAlmostEqual(cost_per_task([{'cost_usd': 0.10}, {}]), 0.05)")],
   ["Sum `cost_usd` over all traces, then divide by the count.",
    "Use `t.get('cost_usd', 0.0)` so a trace missing the field counts as zero rather "
    "than raising."],
   "Cost per task is averaged over every run, success or not — you pay for failures "
   "too. Defaulting a missing cost to zero keeps the metric robust to incomplete "
   "traces.")

ex("ex_v6_5_classify_failure", "EX6.4", "V6.5", "classify_failure",
   "Classify a failure",
   "Classify a failed run into a failure category from its trace, rule-based.",
   "Write `classify_failure(trace)`. If the run succeeded (`success` truthy) return "
   "`None`. Otherwise classify in this order: `'max_steps_hit'` if "
   "`stop_reason == 'max_steps'` or `steps >= max_steps`; `'tool_error'` if "
   "`tool_errors > 0` or `stop_reason == 'error'`; `'no_final_answer'` if "
   "`final_answer` is missing/empty; else `'wrong_answer'`.",
   "def classify_failure(trace):\n"
   "    # Return None for a success, else one failure category (see the order above).\n"
   "    raise NotImplementedError\n",
   "def classify_failure(trace):\n"
   "    if trace.get('success'):\n"
   "        return None\n"
   "    if trace.get('stop_reason') == 'max_steps' or \\\n"
   "            trace.get('steps', 0) >= trace.get('max_steps', float('inf')):\n"
   "        return 'max_steps_hit'\n"
   "    if trace.get('tool_errors', 0) > 0 or trace.get('stop_reason') == 'error':\n"
   "        return 'tool_error'\n"
   "    if not trace.get('final_answer'):\n"
   "        return 'no_final_answer'\n"
   "    return 'wrong_answer'\n",
   [("test_success_returns_none",
     "self.assertIsNone(classify_failure({'success': True}))"),
    ("test_max_steps_hit",
     "self.assertEqual(classify_failure(\n"
     "    {'success': False, 'stop_reason': 'max_steps', 'steps': 8, 'max_steps': 8}),\n"
     "    'max_steps_hit')"),
    ("test_tool_error",
     "self.assertEqual(classify_failure(\n"
     "    {'success': False, 'stop_reason': 'error', 'tool_errors': 1}), 'tool_error')"),
    ("test_wrong_answer_when_answer_present",
     "self.assertEqual(classify_failure(\n"
     "    {'success': False, 'final_answer': 'nope', 'steps': 2, 'max_steps': 8}),\n"
     "    'wrong_answer')")],
   ["Return `None` for successes first, so the rest of the function only deals with "
    "failures.",
    "Order matters: check the step cap, then tool errors, then a missing answer, then "
    "fall through to 'wrong_answer'."],
   "A rule-based taxonomy turns a pile of failing traces into actionable buckets "
   "(ran out of steps vs tool broke vs never answered) — deterministic and "
   "autogradeable, unlike an LLM judge.")

ex("ex_v6_6_regression_diff", "EX6.5", "V6.6", "regression_diff",
   "Detect regressions between runs",
   "Diff two eval runs to find tasks that regressed and tasks that got fixed.",
   "Write `regression_diff(before, after)`. Match traces by `task_id`. Return "
   "`{'regressions': [...], 'fixes': [...]}` where regressions are task ids that "
   "were successful in `before` but not in `after`, and fixes are the reverse. Both "
   "lists sorted; only consider task ids present in both runs.",
   "def regression_diff(before, after):\n"
   "    # Return {'regressions': sorted ids, 'fixes': sorted ids} over common task_ids.\n"
   "    raise NotImplementedError\n",
   "def regression_diff(before, after):\n"
   "    b = {t['task_id']: bool(t.get('success')) for t in before}\n"
   "    a = {t['task_id']: bool(t.get('success')) for t in after}\n"
   "    common = b.keys() & a.keys()\n"
   "    regressions = sorted(tid for tid in common if b[tid] and not a[tid])\n"
   "    fixes = sorted(tid for tid in common if not b[tid] and a[tid])\n"
   "    return {'regressions': regressions, 'fixes': fixes}\n",
   [("test_detects_regression",
     "before = [{'task_id': 't1', 'success': True}]\n"
     "after = [{'task_id': 't1', 'success': False}]\n"
     "self.assertEqual(regression_diff(before, after)['regressions'], ['t1'])"),
    ("test_detects_fix",
     "before = [{'task_id': 't1', 'success': False}]\n"
     "after = [{'task_id': 't1', 'success': True}]\n"
     "self.assertEqual(regression_diff(before, after)['fixes'], ['t1'])"),
    ("test_unchanged_has_no_diff",
     "before = [{'task_id': 't1', 'success': True}]\n"
     "after = [{'task_id': 't1', 'success': True}]\n"
     "self.assertEqual(regression_diff(before, after), {'regressions': [], 'fixes': []})")],
   ["Build a `task_id -> success` dict for each run; the intersection of their keys "
    "is the comparable set.",
    "A regression is `before True and after False`; a fix is the mirror image."],
   "When you tweak a prompt, aggregate success rate can hide that you fixed two tasks "
   "and broke two others. Diffing per task surfaces exactly which ids moved, which is "
   "what catches silent regressions.")

# ============================ MODULE 7 ====================================

ex("ex_v7_2_enforce_caps", "EX7.1", "V7.2", "enforce_caps",
   "Enforce cost and step caps",
   "Enforce a max-step and max-cost cap that halts the loop.",
   "Write `enforce_caps(steps, cost, max_steps=None, max_cost=None)` returning a "
   "halt-reason string if a cap is exceeded, else `None`. Check steps first: if "
   "`max_steps` is set and `steps >= max_steps`, return a message containing "
   "`max_steps`; then if `max_cost` is set and `cost >= max_cost`, return a message "
   "containing `max_cost`. An unset cap (None) is never enforced.",
   "def enforce_caps(steps, cost, max_steps=None, max_cost=None):\n"
   "    # Return a halt-reason string if a cap is exceeded, else None.\n"
   "    raise NotImplementedError\n",
   "def enforce_caps(steps, cost, max_steps=None, max_cost=None):\n"
   "    if max_steps is not None and steps >= max_steps:\n"
   "        return 'max_steps (' + str(max_steps) + ') reached'\n"
   "    if max_cost is not None and cost >= max_cost:\n"
   "        return 'max_cost ($' + str(max_cost) + ') reached'\n"
   "    return None\n",
   [("test_step_cap_fires",
     "self.assertIn('max_steps', enforce_caps(5, 0.0, max_steps=5))"),
    ("test_cost_cap_fires",
     "self.assertIn('max_cost', enforce_caps(1, 0.51, max_cost=0.50))"),
    ("test_within_caps_returns_none",
     "self.assertIsNone(enforce_caps(4, 0.10, max_steps=5, max_cost=0.50))"),
    ("test_no_caps_set_never_halts",
     "self.assertIsNone(enforce_caps(999, 999.0))")],
   ["Guard each cap with an `is not None` check so an unset cap is ignored.",
    "Use `>=` so the loop halts exactly at the cap, and check steps before cost."],
   "Caps are the difference between a bug and a bill. A pure function that returns the "
   "halt reason (or None) is trivial to call once per loop iteration and trivial to "
   "test.")

ex("ex_v7_4_format_log_record", "EX7.2", "V7.4", "format_log_record",
   "Format a structured log record",
   "Emit one flat, structured log record per agent step.",
   "Write `format_log_record(step, action, cost=0.0, cumulative=0.0)` returning a "
   "flat dict with exactly these keys: `step`, `action`, `cost_usd` (rounded to 6 "
   "places), `cumulative_cost_usd` (rounded to 6 places), and `ok` (always `True`).",
   "def format_log_record(step, action, cost=0.0, cumulative=0.0):\n"
   "    # Return a flat dict: step, action, cost_usd, cumulative_cost_usd, ok.\n"
   "    raise NotImplementedError\n",
   "def format_log_record(step, action, cost=0.0, cumulative=0.0):\n"
   "    return {\n"
   "        'step': step,\n"
   "        'action': action,\n"
   "        'cost_usd': round(cost, 6),\n"
   "        'cumulative_cost_usd': round(cumulative, 6),\n"
   "        'ok': True,\n"
   "    }\n",
   [("test_has_exact_keys",
     "rec = format_log_record(1, 'llm_call')\n"
     "self.assertEqual(set(rec), {'step', 'action', 'cost_usd', 'cumulative_cost_usd', 'ok'})"),
    ("test_carries_step_and_action",
     "rec = format_log_record(3, 'tool_call')\n"
     "self.assertEqual((rec['step'], rec['action']), (3, 'tool_call'))"),
    ("test_rounds_cost",
     "rec = format_log_record(1, 'x', cost=0.123456789)\n"
     "self.assertEqual(rec['cost_usd'], 0.123457)"),
    ("test_ok_defaults_true",
     "self.assertTrue(format_log_record(1, 'x')['ok'])")],
   ["Return a literal dict — a stable, flat schema is exactly what a log aggregator "
    "wants.",
    "`round(value, 6)` keeps the cost fields tidy and comparable."],
   "Observability starts with a consistent record per step. A flat dict with a fixed "
   "key set serialises cleanly to JSON lines and makes later filtering and metrics "
   "straightforward.")

ex("ex_v7_5_guardrail_check", "EX7.3", "V7.5", "guardrail_check",
   "A tool-access guardrail",
   "Apply an allow/block rule to a tool call before it executes.",
   "Write `guardrail_check(tool_name, allow=None, block=None)` returning "
   "`(allowed, reason)`. Precedence: if `block` is given and `tool_name` is in it, "
   "deny (reason mentions `denylist`). Else if `allow` is given and `tool_name` is "
   "NOT in it, deny (reason mentions `allowlist`). Otherwise allow with reason "
   "`'allowed'`.",
   "def guardrail_check(tool_name, allow=None, block=None):\n"
   "    # Return (allowed: bool, reason: str). Denylist wins over allowlist.\n"
   "    raise NotImplementedError\n",
   "def guardrail_check(tool_name, allow=None, block=None):\n"
   "    if block and tool_name in block:\n"
   "        return False, \"'\" + tool_name + \"' is on the denylist\"\n"
   "    if allow is not None and tool_name not in allow:\n"
   "        return False, \"'\" + tool_name + \"' is not on the allowlist\"\n"
   "    return True, 'allowed'\n",
   [("test_denylist_blocks",
     "ok, reason = guardrail_check('rm', block=['rm'])\n"
     "self.assertFalse(ok)"),
    ("test_denylist_wins_over_allowlist",
     "ok, reason = guardrail_check('rm', allow=['rm'], block=['rm'])\n"
     "self.assertIn('denylist', reason)"),
    ("test_allowlist_permits_listed",
     "self.assertTrue(guardrail_check('search', allow=['search'])[0])"),
    ("test_allowlist_blocks_unlisted",
     "self.assertFalse(guardrail_check('delete', allow=['search'])[0])")],
   ["Check the denylist first so a blocked tool is denied even if it's also "
    "allowlisted.",
    "An allowlist denies anything not on it; if no `allow` is given, don't enforce "
    "it."],
   "Guardrails gate tool access before execution. Denylist-beats-allowlist precedence "
   "means an explicitly dangerous tool stays blocked regardless of other rules — the "
   "safe default.")


# ---------------------------------------------------------------------------
def header(exid, source, kind):
    return f"# {kind}\n# Implements: {exid} (source {source})\n# Self-contained: standard library + numpy only, no network, deterministic.\n\n"


def build_eval(exc):
    imports = exc["imports"]
    cls = "Test_" + exc["folder"]
    lines = [header(exc["exid"], exc["source"], "Unit tests (one assertion each)")]
    lines.append("import unittest\n")
    lines.append(f"from solution import {imports}\n\n\n")
    lines.append(f"class {cls}(unittest.TestCase):\n")
    for name, body in exc["tests"]:
        lines.append(f"    def {name}(self):\n")
        for bl in body.split("\n"):
            lines.append(f"        {bl}\n" if bl else "\n")
        lines.append("\n")
    lines.append('\nif __name__ == "__main__":\n    unittest.main()\n')
    return "".join(lines)


def build_meta(exc):
    hints = "\n".join(f"{i+1}. {h}" for i, h in enumerate(exc["hints"]))
    return (
        f"# {exc['exid']} — {exc['title']}\n\n"
        f"**Implements:** {exc['exid']} (source {exc['source']})\n\n"
        f"## Learning objective\n{exc['objective']}\n\n"
        f"## Problem statement\n{exc['statement']}\n\n"
        f"Edit `starter.py` so the target function works; the file you submit is "
        f"imported by the tests as `solution`. Standard library + numpy only.\n\n"
        f"## Hints\n{hints}\n\n"
        f"## Solution explanation\n{exc['explanation']}\n"
    )


def main():
    written = 0
    for exc in EXERCISES:
        d = os.path.join(HERE, exc["folder"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "starter.py"), "w") as f:
            f.write(header(exc["exid"], exc["source"], "Starter — complete the stubbed function") + exc["starter"])
        with open(os.path.join(d, "solution.py"), "w") as f:
            f.write(header(exc["exid"], exc["source"], "Reference solution") + exc["solution"])
        with open(os.path.join(d, "evaluation.py"), "w") as f:
            f.write(build_eval(exc))
        with open(os.path.join(d, "exercise_meta.md"), "w") as f:
            f.write(build_meta(exc))
        written += 1
        print("wrote", exc["folder"])
    print(f"\n{written} exercises ({written * 4} files)")


if __name__ == "__main__":
    main()
