# Quiz — Module 7: Production realities

> Covers: V7.1–V7.5 (Q7), plus **2 spaced-review** items revisiting Modules 5–6.
> Each block is one question: stem, four options, an **Answer** line, and a
> teaching explanation. `[Multi-select]` blocks have more than one correct
> letter. Paste each block into Udemy as a separate question.

---

**Q7.1 (Recall).** What is the core risk of an uncapped agent loop in production?

A) It uses too little memory
B) It can run away — burning unbounded steps and cost
C) It always returns the wrong answer
D) It cannot call tools

**Answer:** B
**Explanation:** An agent with no caps can spin indefinitely, and every step is a paid model call — runaway loops are how agents quietly run up large bills.

---

**Q7.2 (Applied).** `enforce_caps(steps, cost, max_steps=5, max_cost=0.30)` is called with `steps=3, cost=0.30`. With the step-check-first ordering, what happens?

A) Returns None (within caps)
B) Returns a max_steps reason
C) Returns a max_cost reason
D) Raises an exception

**Answer:** C
**Explanation:** Steps (3) are under the cap, but cost has reached $0.30, so the cost cap fires and the loop halts with a max_cost reason.

---

**Q7.3 (Recall).** Structured per-step logging exists primarily to provide:

A) Faster inference
B) Observability — a record you can inspect, aggregate, and alert on
C) A way to skip the stopping condition
D) Cheaper embeddings

**Answer:** B
**Explanation:** A consistent log record per step is the foundation of observability: it lets you reconstruct what the agent did and compute operational metrics.

---

**Q7.4 (Applied).** A guardrail with `block=["shell"]` and `allow=["shell", "search"]` is asked about the `shell` tool. The result is:

A) Allowed, because it's on the allowlist
B) Blocked, because the denylist takes precedence
C) Allowed, because allow and block cancel out
D) Undefined behaviour

**Answer:** B
**Explanation:** Denylist beats allowlist by design — an explicitly dangerous tool stays blocked regardless of any allow rule. That precedence is the safe default.

---

**Q7.5 (Applied).** Which is an example of applying a guardrail *before* a tool executes?

A) Logging the tool's output after it runs
B) Checking the tool name against an allow/block rule and refusing if disallowed
C) Summarising old turns
D) Computing cosine similarity

**Answer:** B
**Explanation:** Guardrails gate access at call time — you check the requested tool (and args) against your policy and refuse before any side effect happens.

---

**Q7.SR1 (Spaced review — Module 5).** What stops infinite delegation in a multi-agent system?

A) A larger model
B) A delegation-depth cap
C) More workers
D) A bigger context window

**Answer:** B
**Explanation:** Recall from Module 5: bounding delegation depth guarantees termination — the same "cap the loop" instinct as Module 7's step/cost caps.

---

**Q7.SR2 (Spaced review — Module 6).** Why diff two eval runs per task instead of comparing only aggregate success rate?

A) To reduce cost
B) Because equal aggregates can hide tasks that regressed and others that were fixed
C) To re-train the model
D) Because aggregates are always wrong

**Answer:** B
**Explanation:** Recall from Module 6: a regression diff surfaces per-task changes that an unchanged overall rate would otherwise mask — essential before shipping a prompt tweak.
