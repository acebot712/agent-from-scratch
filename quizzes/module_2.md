# Quiz — Module 2: Tool use from scratch

> Covers: V2.1–V2.7 (Q2). Each block is one question: stem, four options, an
> **Answer** line, and a teaching explanation. `[Multi-select]` blocks have more
> than one correct letter. Paste each block into Udemy as a separate question.

---

**Q2.1 (Recall).** When an LLM "uses a tool", what is actually happening?

A) The model executes the tool's code inside itself
B) The model emits a request for a tool; your code runs it and feeds back the result
C) The provider runs the tool on its servers automatically
D) The tool rewrites the model's weights

**Answer:** B
**Explanation:** The model can't execute anything — it only produces text asking for a call. Your harness runs the tool and returns the observation, which is the whole trick behind tool use.

---

**Q2.2 (Recall).** A clean tool interface in this course consists of which fields?

A) name, description, args schema, run
B) prompt, temperature, top_p, seed
C) id, vector, score, payload
D) role, content, tokens, cost

**Answer:** A
**Explanation:** A consistent `(name, description, args, run)` signature is what lets the registry advertise tools to the model and dispatch calls uniformly.

---

**Q2.3 (Applied).** The model replies with `TOOL: get_weather` and `ARGS: {"city": "Paris"}`. What should `parse_tool_call` return?

A) `"get_weather Paris"`
B) `{"name": "get_weather", "args": {"city": "Paris"}}`
C) `None`
D) `{"tool": "get_weather"}` with no args

**Answer:** B
**Explanation:** Parsing converts the textual request into a structured `{name, args}` object so dispatch can look up the tool and call it with keyword arguments.

---

**Q2.4 (Applied).** The model requests a tool named `flibber` that you never registered. A well-behaved dispatcher should:

A) Raise an unhandled exception and crash the agent
B) Silently ignore the request and continue
C) Return a structured error noting the unknown tool, to feed back to the model
D) Register `flibber` automatically as an empty tool

**Answer:** C
**Explanation:** Hallucinated tools are expected; dispatch should fail gracefully into an error observation so the model can correct itself instead of crashing the run.

---

**Q2.5 (Recall).** How does native function calling relate to the from-scratch version you built?

A) It is a completely different mechanism with no overlap
B) It is the same idea (model requests a call, you run it) with a provider-managed format
C) It removes the need for a tool registry entirely
D) It lets the model run arbitrary code on your machine

**Answer:** B
**Explanation:** Native function calling is just a structured, provider-supported encoding of the same request-and-dispatch loop — understanding the manual version makes the API obvious.

---

**Q2.6 (Applied) [Multi-select].** Which situations should the dispatch error path handle gracefully? (Select all that apply.)

A) Unknown / hallucinated tool name
B) Missing or wrong arguments for a known tool
C) A tool function that raises at runtime
D) The model giving a correct final answer

**Answer:** A, B, C
**Explanation:** All three failure modes should become structured errors the loop can recover from. A correct final answer isn't an error — it's the normal exit.
