# Quiz — Module 6: Evaluating agents

> Covers: V6.1–V6.6 (Q6). Each block is one question: stem, four options, an
> **Answer** line, and a teaching explanation. `[Multi-select]` blocks have more
> than one correct letter. Paste each block into Udemy as a separate question.

---

**Q6.1 (Recall).** Why evaluate agents with a harness instead of "vibes"?

A) Vibes are illegal
B) You can't reliably improve or ship what you can't measure
C) Evals make the model faster
D) It removes the need for prompts

**Answer:** B
**Explanation:** Systematic evals turn subjective impressions into numbers you can compare across changes — the basis for catching regressions and proving improvement.

---

**Q6.2 (Recall).** Success rate is computed as:

A) Average steps over all runs
B) Fraction of tasks whose run satisfied the success predicate
C) Total cost divided by step count
D) Number of tools called

**Answer:** B
**Explanation:** Success rate is wins ÷ total — the headline measure of whether the agent actually solves the tasks.

---

**Q6.3 (Applied).** Step efficiency is averaged over which runs?

A) All runs, successful or not
B) Only the successful runs
C) Only the failed runs
D) Only runs that hit the step cap

**Answer:** B
**Explanation:** Counting steps only on successes answers "when it works, how efficiently?" — including failures (which often max out steps) would distort the signal.

---

**Q6.4 (Applied).** A failed trace has `stop_reason="max_steps"` and `steps == max_steps`. The rule-based taxonomy classifies it as:

A) tool_error
B) no_final_answer
C) max_steps_hit
D) wrong_answer

**Answer:** C
**Explanation:** Hitting the step cap is its own category; the rule order checks the cap first because that failure mode masks whatever else might be wrong.

---

**Q6.5 (Applied).** You tweak a prompt and overall success rate is unchanged. Why still run a regression diff per task?

A) It's required by the provider
B) Aggregate parity can hide that some tasks broke while others were fixed
C) It lowers cost
D) It re-trains the model

**Answer:** B
**Explanation:** A flat aggregate can mask offsetting changes; diffing by `task_id` reveals exactly which tasks regressed or were fixed.

---

**Q6.6 (Recall) [Multi-select].** Which are standard agent eval metrics from this module? (Select all that apply.)

A) Success rate
B) Step efficiency
C) Cost per task
D) Model parameter count

**Answer:** A, B, C
**Explanation:** Success, steps, and cost are the three headline metrics. Parameter count is a property of the model, not a measure of agent performance on your tasks.
