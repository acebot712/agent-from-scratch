# Quiz — Module 1: The agent loop, properly

> Covers: V1.1–V1.5 (Q1). Each block is one question: stem, four options, an
> **Answer** line, and a teaching explanation. `[Multi-select]` blocks have more
> than one correct letter. Paste each block into Udemy as a separate question.

---

**Q1.1 (Recall).** The five parts of the agent loop are observe, decide, act, feed back, and ___?

A) embed
B) stop
C) fine-tune
D) cache

**Answer:** B
**Explanation:** The loop must be able to terminate; the stopping check is the fifth part and the one beginners most often forget.

---

**Q1.2 (Recall).** Why does the framework put a provider-agnostic wrapper (`complete`) in front of the LLM API?

A) To make the model respond faster
B) To normalise different providers' responses behind one interface
C) To avoid ever needing an API key
D) To train the model on your data

**Answer:** B
**Explanation:** Normalising responses means the rest of the agent works the same whether you call an OpenAI-compatible or Anthropic endpoint — provider details stop leaking into your loop.

---

**Q1.3 (Applied).** Your `Agent.run` loops up to `max_steps`, but on a hard task it returns `"[no final answer]"`. What is the most likely cause?

A) The provider wrapper is broken
B) The model never emitted the completion marker before the step cap was hit
C) The system prompt is too short
D) The embeddings are stale

**Answer:** B
**Explanation:** The step cap fired because the model didn't signal completion in time — that's the safety net working, and a sign the task may need more steps or a clearer prompt.

---

**Q1.4 (Applied).** Parsing the model's intent means doing what?

A) Re-ranking documents by similarity
B) Extracting a structured action (or final answer) from free-text output
C) Counting tokens in the prompt
D) Splitting the system prompt into chunks

**Answer:** B
**Explanation:** The model emits text; intent parsing turns that text into something structured the loop can act on, such as a tool request or a terminal answer.

---

**Q1.5 (Applied).** A correct stopping condition for the loop should return `True` when:

A) Only when the model emits the completion marker
B) Only when the step cap is reached
C) Either the completion marker appears OR the step cap is reached
D) Never — the user must stop it manually

**Answer:** C
**Explanation:** You need both an intentional exit (the marker) and a safety exit (the cap); relying on only one leaves the loop able to run forever or to stop prematurely.

---

**Q1.6 (Recall) [Multi-select].** Which responsibilities belong to the reusable `Agent` class? (Select all that apply.)

A) Hold the message history for a run
B) Call the LLM each step and append the reply
C) Decide when to stop
D) Permanently store every conversation in a database

**Answer:** A, B, C
**Explanation:** The Agent owns the loop: history, the per-step model call, and the stopping decision. Durable cross-session storage is a separate concern (episodic memory, Module 3).
