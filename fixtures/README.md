# Fixtures

Shipped, version-controlled test data so labs/assignments run **offline and
deterministically** (per COURSE_SPEC.md §4). Nothing here calls a live model.

## `traces/` — recorded agent traces (Module 6 evals)

- `runA.json`, `runB.json` — each is `{"run_id", "note", "traces": [...]}`.
  `runB` is `runA` after a prompt tweak (t2 regressed, t3 fixed) — used for the
  regression-diff demo (V6.6).
- `t1.json … t5.json` — the same traces split one-per-file, for
  `agent.evals.replay_runner(fixtures_dir)`.

Each trace dict:

| field | meaning |
|---|---|
| `task_id` | stable id, matched across runs for regression diffing |
| `success` | did the run succeed (ground truth) |
| `steps` / `max_steps` | steps used / the cap |
| `cost_usd` | run cost in dollars |
| `final_answer` | model's final answer (`null`/`""` if none) |
| `tool_errors` | count of tool failures during the run |
| `stop_reason` | `final_answer` \| `max_steps` \| `error` |

## `embeddings/` — precomputed vectors (Module 3 retrieval)

- `doc_vectors.npy` — `(6, 8)` float array, one row per doc in `docs.json`.
  Docs are topic-clustered (geography / biology / programming) so top-k is easy
  to eyeball.
- `docs.json` — the 6 source documents (same order as the vectors).
- `query_vectors.npy` + `queries.json` — 3 query vectors aligned to the clusters.

Load:

```python
import json, numpy as np
vecs = np.load("fixtures/embeddings/doc_vectors.npy")
docs = json.load(open("fixtures/embeddings/docs.json"))
```
