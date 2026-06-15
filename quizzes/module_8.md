# Quiz — Module 8: Capstone

> Covers: V8.1–V8.4 (Q8) — consolidation and mapping the framework onto named
> tools. Because the capstone is synthesis, several questions are inherently
> cross-module. Each block is one question: stem, four options, an **Answer**
> line, and a teaching explanation. `[Multi-select]` blocks have more than one
> correct letter. Paste each block into Udemy as a separate question.

---

**Q8.1 (Recall).** "Consolidating into a coherent framework" (V8.1) mainly means:

A) Rewriting everything in a faster language
B) Exposing all modules through one clean, consistent public API
C) Deleting the earlier modules
D) Adding LangChain as a dependency

**Answer:** B
**Explanation:** The capstone unifies the per-module pieces behind a single import surface so the whole thing reads as one framework, not seven scripts.

---

**Q8.2 (Applied).** In the framework-equivalence map, our `SemanticMemory` corresponds most closely to which LangChain concept?

A) AgentExecutor
B) A VectorStore retriever
C) A PromptTemplate
D) A CallbackHandler

**Answer:** B
**Explanation:** Similarity-based retrieval over stored vectors is exactly what a vector-store retriever provides — same idea, different packaging.

---

**Q8.3 (Applied).** Our coordinator/worker pattern maps onto which CrewAI/AutoGen concept?

A) A single tool definition
B) A Crew / GroupChat of multiple agents
C) An embedding model
D) A token counter

**Answer:** B
**Explanation:** Multiple role-specialised agents coordinated toward one goal is precisely what CrewAI's Crew and AutoGen's GroupChat express.

---

**Q8.4 (Applied) [Multi-select].** A solid flagship agent built on this framework should combine which pieces? (Select all that apply.)

A) The agent loop with at least one tool
B) Some memory (working/episodic/semantic)
C) A production cap and a guardrail
D) A guarantee of zero mistakes

**Answer:** A, B, C
**Explanation:** A real agent ties together the loop, tools, memory, and hardening. No agent can guarantee zero mistakes — which is exactly why evals and caps exist.

---

**Q8.5 (Recall — cumulative, Module 2).** Native function calling is best understood as:

A) A different mechanism unrelated to your manual tool loop
B) A provider-managed encoding of the same request-then-dispatch loop you built
C) A way to fine-tune the model
D) A replacement for the agent loop

**Answer:** B
**Explanation:** Cumulative recall: once you've built tools from scratch, the native API is just a tidy wire format for the same idea — no magic.

---

**Q8.6 (Applied — cumulative, Modules 3 & 6).** You ship a prompt change. Which two practices best protect quality? (Select all that apply.) `[Multi-select]`

A) Keep the system message and recent turns within the context budget
B) Run a regression diff between the old and new eval runs
C) Remove the stopping condition to let the agent think longer
D) Disable all guardrails for speed

**Answer:** A, B
**Explanation:** Cumulative recall: sound context budgeting (M3) keeps the agent focused, and a per-task regression diff (M6) catches silent breakage — removing the stop check or guardrails would do the opposite.
