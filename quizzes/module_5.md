# Quiz — Module 5: Multi-agent systems

> Covers: V5.1–V5.6 (Q5), plus **2 spaced-review** items revisiting Modules 3–4.
> Each block is one question: stem, four options, an **Answer** line, and a
> teaching explanation. `[Multi-select]` blocks have more than one correct
> letter. Paste each block into Udemy as a separate question.

---

**Q5.1 (Recall).** In the coordinator/worker pattern, the coordinator's job is to:

A) Execute every subtask itself
B) Decompose the task and delegate subtasks to workers, then combine results
C) Store embeddings for retrieval
D) Cap the token budget

**Answer:** B
**Explanation:** The coordinator plans and routes; specialised workers do the focused work, and the coordinator synthesises their outputs into one result.

---

**Q5.2 (Applied).** Routing a message to the wrong-named recipient should:

A) Silently drop the message
B) Pick the most similar role automatically
C) Raise an error (e.g. KeyError) so the misroute is visible
D) Send it to every worker

**Answer:** C
**Explanation:** An unroutable message is a bug; failing loudly surfaces it instead of letting work silently vanish.

---

**Q5.3 (Applied).** What prevents a multi-agent system from delegating forever (A→B→A→…)?

A) A larger context window
B) A delegation-depth cap that stops descending past a limit
C) A faster model
D) More workers

**Answer:** B
**Explanation:** Bounding delegation depth is the brake that guarantees termination even when agents keep handing work to each other.

---

**Q5.4 (Recall).** How are agent roles primarily defined in this course?

A) By separate fine-tuned models per role
B) By distinct system prompts that specialise each agent
C) By different temperatures only
D) By their position in the message list

**Answer:** B
**Explanation:** Role design is prompt design — a focused system prompt is what makes one worker a "researcher" and another a "reviewer."

---

**Q5.5 (Applied).** The *mechanical* (graded) synthesis of worker outputs does what?

A) Asks an LLM to write a fused summary
B) Trims, drops blanks, dedupes order-preserving, and combines into one result
C) Picks one worker's output at random
D) Returns the longest output

**Answer:** B
**Explanation:** The deterministic merge (combine/dedupe/order) is reproducible and autogradeable, unlike an LLM-written fusion.

---

**Q5.SR1 (Spaced review — Module 3).** Trimming history to a token budget keeps which messages?

A) The oldest ones
B) The system message plus the most recent messages that fit
C) A random subset
D) Only tool observations

**Answer:** B
**Explanation:** Recall from Module 3: protect the system instruction and keep the freshest context within budget — the same budgeting matters more once many agents share context.

---

**Q5.SR2 (Spaced review — Module 4).** In ReAct, what does the Observation line contain?

A) The model's internal reasoning
B) The result of the just-requested tool action, fed back in
C) The final answer
D) The system prompt

**Answer:** B
**Explanation:** Recall from Module 4: the Observation is the tool's output returned to the model, closing one Thought→Action→Observation cycle.
