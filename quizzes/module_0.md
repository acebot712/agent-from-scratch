# Quiz — Module 0: What an agent actually is

> Covers: V0.1–V0.4 (Q0). Each block is one question: stem, four options, an
> **Answer** line marking the key, and a teaching explanation. Multi-select
> questions are tagged `[Multi-select]` and have more than one letter in
> **Answer**. Paste each block into Udemy's quiz tool as a separate question.

---

**Q0.1 (Recall).** Which statement best defines an "agent" as used in this course?

A) A fine-tuned model specialised for one task
B) An LLM running in a loop that chooses its own next action
C) A prompt template with placeholder variables
D) A vector database wired to a chatbot UI

**Answer:** B
**Explanation:** An agent is just an LLM placed in a loop where it decides what to do next; everything else (tools, memory, planning) is an addition to that core idea.

---

**Q0.2 (Recall).** What does a framework like LangChain or CrewAI fundamentally add on top of a raw LLM call?

A) A faster model than you can access directly
B) Abstraction and plumbing around one simple decide-act loop
C) The ability for the model to execute its own code natively
D) A guarantee that the agent will never make mistakes

**Answer:** B
**Explanation:** Frameworks are convenience layers over the same basic loop you can write yourself — understanding the loop is what demystifies them.

---

**Q0.3 (Applied).** You write a minimal agent loop, but it never stops — it keeps calling the model forever. Which part of the loop is missing or broken?

A) The system prompt
B) The tool registry
C) The stopping condition
D) The embedding step

**Answer:** C
**Explanation:** Without a terminal-state check (a completion marker and/or a step cap) the loop has no reason to exit, so it runs indefinitely.

---

**Q0.4 (Applied).** In the 20-line agent, after the model produces a reply that is *not* a final answer, what should happen next?

A) The loop returns the reply immediately
B) The reply is appended to the messages and the loop iterates again
C) The conversation is reset to only the system prompt
D) The model is swapped for a different provider

**Answer:** B
**Explanation:** Feeding the reply back into the message history and looping is the "feed back" step — it's what lets the model build on its own prior output.

---

**Q0.5 (Recall) [Multi-select].** Which of the following are genuine parts of the agent loop taught in Module 0? (Select all that apply.)

A) Observe / take input
B) Decide (call the model)
C) Act / feed the result back
D) Re-train the model weights

**Answer:** A, B, C
**Explanation:** The loop is observe → decide → act → feed back → stop. Updating model weights is training, not part of the runtime agent loop.
