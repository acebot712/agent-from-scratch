"""Hello, agent — the 20-line Module 0 live build (V0.4).

An agent is just an LLM in a loop that decides its own next step. That's it.
Run it:  LLM_PROVIDER=openai LLM_API_KEY=sk-... python examples/hello_agent.py
"""
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agent.llm import complete  # noqa: E402

DONE = "FINAL ANSWER:"


def run(task, max_steps=5):
    messages = [
        {"role": "system", "content": f"Reason step by step. End with '{DONE} <answer>'."},
        {"role": "user", "content": task},
    ]
    for _ in range(max_steps):                       # the loop
        reply = complete(messages).text              # the LLM decides
        messages.append({"role": "assistant", "content": reply})
        if DONE in reply:                            # the stopping condition
            return reply.split(DONE, 1)[1].strip()
        messages.append({"role": "user", "content": "Continue."})
    return reply


if __name__ == "__main__":
    print(run("What is 17 * 23? Show your reasoning."))
