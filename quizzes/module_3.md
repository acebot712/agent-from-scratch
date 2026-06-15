# Quiz — Module 3: Memory architectures

> Covers: V3.1–V3.6 (Q3), plus **2 spaced-review** items revisiting Modules 1–2.
> Each block is one question: stem, four options, an **Answer** line, and a
> teaching explanation. `[Multi-select]` blocks have more than one correct
> letter. Paste each block into Udemy as a separate question.

---

**Q3.1 (Recall).** Match the role: which memory holds the live, in-progress message window?

A) Working memory
B) Episodic memory
C) Semantic memory
D) Procedural memory

**Answer:** A
**Explanation:** Working memory is the current context window. Episodic memory logs past events across sessions; semantic memory stores retrievable facts.

---

**Q3.2 (Applied).** Your message history exceeds the context budget. The trimming strategy taught here keeps:

A) The oldest messages, dropping the newest
B) A leading system message plus the most recent messages that fit
C) A random sample of messages
D) Only the system message

**Answer:** B
**Explanation:** You protect the system instruction and prefer the freshest turns within the budget, because recent context is usually the most relevant to the next step.

---

**Q3.3 (Recall).** Cosine similarity between two vectors measures their:

A) Euclidean distance
B) Direction (angle), independent of magnitude
C) Element-wise difference
D) Token overlap

**Answer:** B
**Explanation:** Cosine compares orientation, so two vectors pointing the same way score ~1 regardless of length — ideal for comparing embeddings.

---

**Q3.4 (Applied).** Retrieval "without a vector DB" works by:

A) Asking the model to remember everything
B) Scoring every document by similarity to the query, sorting, and taking the top-k
C) Storing documents in a SQL table and running JOINs
D) Fine-tuning the model on the documents

**Answer:** B
**Explanation:** Top-k retrieval is just score-all-then-sort; a vector database only adds speed at scale, not a different concept.

---

**Q3.5 (Applied).** Why serialise episodic memory to disk?

A) To reduce the model's token usage per call
B) So an agent can remember facts across separate runs/sessions
C) To make cosine similarity faster
D) To bypass the context budget entirely

**Answer:** B
**Explanation:** Persistence is what lets a new process reload prior episodes — memory that survives restarts is the point of the episodic store.

---

**Q3.SR1 (Spaced review — Module 1).** What two conditions should end the agent loop?

A) Completion marker present, OR step cap reached
B) Only when the user presses stop
C) When the context budget is exceeded
D) When a tool returns an error

**Answer:** A
**Explanation:** Recall from Module 1: an intentional exit (marker) plus a safety exit (step cap). Memory and tools don't change this terminal logic.

---

**Q3.SR2 (Spaced review — Module 2).** A model requests a tool you never registered. The dispatcher should:

A) Crash the agent
B) Return a structured "unknown tool" error to feed back to the model
C) Run the most similar tool instead
D) Skip the rest of the loop silently

**Answer:** B
**Explanation:** Recall from Module 2: hallucinated tools are handled gracefully as error observations so the model can recover — never by crashing.
