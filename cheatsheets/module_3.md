# Cheat Sheet — Module 3: Memory architectures

**Three memories:** *working* (live window, budget-bound) · *episodic* (event log, persisted) · *semantic* (facts retrieved by similarity).

## Context budget (working memory)

```python
from agent.memory import count_tokens, context_budget_trim, WorkingMemory

count_tokens("a b c")             # 3   (tokenizer-free proxy: word count)
kept = context_budget_trim(messages, budget=2000)   # keep system + most-recent-that-fit

wm = WorkingMemory(budget=2000)
wm.add("user", "hello"); wm.tokens(); wm.window()
wm.compress_overflow(summarizer=lambda msgs: my_llm_summary(msgs))  # fold old turns -> summary
```

## Similarity + retrieval (from scratch, numpy)

```python
from agent.memory import cosine_similarity, top_k_retrieval

cosine_similarity([1,0], [1,0])   # 1.0   (zero-vector -> 0.0, no divide-by-zero)
cosine_similarity([1,0], [0,1])   # 0.0

top_k_retrieval(query_vec, doc_vecs, k=3)   # -> [(index, score), ...] best first
```

```python
# cosine in one line:  dot(a,b) / (||a|| * ||b||)
import numpy as np
d = np.linalg.norm(a) * np.linalg.norm(b)
sim = 0.0 if d == 0 else float(np.dot(a, b) / d)
```

## Semantic memory (embed → store → retrieve)

```python
from agent import SemanticMemory
mem = SemanticMemory()                    # uses agent.llm.embed() by default
mem.add("Cats are mammals.")              # or mem.add(text, vector=[...]) to skip embedding
mem.retrieve("animals", k=2)              # -> top-k docs (strings)
```

## Episodic memory (persist across sessions)

```python
from agent import EpisodicMemory
m = EpisodicMemory()
m.record("user", "my favorite color is teal", step=1)
m.save("mem.json")                        # JSON on disk
m2 = EpisodicMemory.load("mem.json")      # new session remembers
m.to_json() / EpisodicMemory.from_json(s) # string form
```

## Gotchas

- **Cosine = direction, not distance.** Magnitude is ignored — that's why it's robust for embeddings.
- **Always guard the zero vector** or you'll divide by zero.
- **Budget keeps recent, protects system.** Oldest turns are dropped first; summarise them if they matter.
- **Retrieval ≠ vector DB.** Score-all-then-sort is the concept; a DB only adds speed at scale.
- **Empty memory file → `[]`**, not a crash (`load`/`from_json` handle blank input).
