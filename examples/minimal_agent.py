"""The whole idea, on one screen.

A complete tool-using agent in ~120 lines of pure standard library — no numpy,
no framework import, no SDK. This is the irreducible core that the full
`src/agent/` framework expands into: an LLM in a loop that chooses its next
action, calls a tool, feeds the result back, and stops.

Read this top to bottom once and you understand every agent framework on the
market. The framework adds structure (memory, planning, multi-agent, evals,
caps); the beating heart is right here.

Run:
    LLM_PROVIDER=openai LLM_API_KEY=sk-... python examples/minimal_agent.py
"""
import json
import os
import re
import urllib.request

# --- 1. the LLM call: one function, provider-agnostic ------------------------

def complete(messages):
    """Call an OpenAI-compatible chat endpoint; return the assistant text."""
    base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    payload = {"model": os.environ.get("LLM_MODEL", "gpt-4o-mini"), "messages": messages}
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode())
    return body["choices"][0]["message"]["content"] or ""


# --- 2. tools: just named Python functions -----------------------------------

def calculator(expression):
    """Evaluate arithmetic, e.g. '12 * 9'."""
    return str(eval(expression, {"__builtins__": {}}, {}))  # demo only

def word_count(text):
    """Count words in a string."""
    return str(len(text.split()))

TOOLS = {"calculator": calculator, "word_count": word_count}


# --- 3. parse the model's tool request out of free text ----------------------

DONE = "FINAL ANSWER:"
_CALL = re.compile(r"TOOL:\s*(\w+)\s*ARGS:\s*(\{.*\})", re.DOTALL)

def parse_call(text):
    """Return {'name', 'args'} if the model asked for a tool, else None."""
    m = _CALL.search(text)
    if not m:
        return None
    try:
        args = json.loads(m.group(2))
    except json.JSONDecodeError:
        args = {}
    return {"name": m.group(1), "args": args if isinstance(args, dict) else {}}


def run_tool(call):
    """Dispatch a parsed call to the right function — gracefully."""
    name = call["name"]
    if name not in TOOLS:
        return f"ERROR: unknown tool '{name}' (have: {list(TOOLS)})"
    try:
        return TOOLS[name](**call["args"])
    except Exception as exc:                      # bad args / tool blew up
        return f"ERROR: {type(exc).__name__}: {exc}"


# --- 4. the loop: observe -> decide -> act -> feed back -> stop ---------------

SYSTEM = f"""You are an agent that can call tools.
To call one, reply EXACTLY:
TOOL: <name> ARGS: {{"arg": "value"}}
Tools:
- calculator(expression): evaluate arithmetic
- word_count(text): count words
When done, reply: {DONE} <answer>"""

def run(task, max_steps=6):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": task}]
    for step in range(1, max_steps + 1):          # step cap = the safety stop
        reply = complete(messages)                # decide
        messages.append({"role": "assistant", "content": reply})

        if DONE in reply:                         # intentional stop
            return reply.split(DONE, 1)[1].strip()

        call = parse_call(reply)                  # act?
        if call is None:
            messages.append({"role": "user", "content": "Call a tool or give FINAL ANSWER."})
            continue
        observation = run_tool(call)              # run it; feed the result back
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    return "[no final answer — hit max_steps]"


if __name__ == "__main__":
    print(run("What is 128 * 47, and how many words are in this question?"))
