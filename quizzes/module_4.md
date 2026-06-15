# Quiz — Module 4: Planning & reasoning

> Covers: V4.1–V4.6 (Q4). Each block is one question: stem, four options, an
> **Answer** line, and a teaching explanation. `[Multi-select]` blocks have more
> than one correct letter. Paste each block into Udemy as a separate question.

---

**Q4.1 (Recall).** ReAct interleaves which two things?

A) Retrieval and ranking
B) Reasoning (Thought) and acting (Action/Observation)
C) Training and inference
D) Embedding and trimming

**Answer:** B
**Explanation:** ReAct alternates a Thought with an Action and its Observation, so the model reasons about each tool result before its next move.

---

**Q4.2 (Recall).** In a ReAct trace, what closes a single step?

A) A Thought line
B) An Action line
C) An Observation line
D) A blank line

**Answer:** C
**Explanation:** The Observation is the tool's result fed back in; once it arrives, that Thought→Action→Observation cycle is complete and a new step can begin.

---

**Q4.3 (Applied).** A model produces a wrong answer, but the task is verifiable (you can check correctness). The fitting strategy is:

A) Tree-of-thoughts with 50 branches
B) A reflection loop: critique the output and retry within a budget
C) Skip straight to a final answer
D) Switch providers

**Answer:** B
**Explanation:** When you can detect failure, reflection (critique + bounded retry) lets the agent self-correct without exploring the whole solution space.

---

**Q4.4 (Applied).** Why must a reflection loop have a retry budget?

A) To make the model answer faster
B) So an agent that can't fix its output doesn't retry forever
C) To increase the temperature each retry
D) To store more episodes

**Answer:** B
**Explanation:** Without a cap, a model that keeps producing bad output would loop indefinitely; the budget bounds the cost of self-correction.

---

**Q4.5 (Applied).** Tree-of-thoughts differs from a single reasoning chain because it:

A) Uses no LLM calls
B) Explores multiple candidate paths and selects the best
C) Always returns the first idea
D) Requires a vector database

**Answer:** B
**Explanation:** ToT generates several candidate continuations and scores them, trading more compute for better coverage on branching problems.

---

**Q4.6 (Applied).** Given task metadata `{"needs_tools": true}`, a rule-based strategy selector should choose:

A) direct
B) react
C) reflection
D) tot

**Answer:** B
**Explanation:** Tasks that need tools map to ReAct, whose actions *are* tool calls; the selector routes by metadata so you don't pay for heavy reasoning when it isn't needed.
