# Cheat Sheet — Module 6: Evaluating agents

You can't ship what you can't measure. Module 6 runs on **recorded trace fixtures**, so it works standalone.

## Trace schema (one run)

```json
{ "task_id": "t3", "success": false, "steps": 8, "max_steps": 8,
  "cost_usd": 0.040, "final_answer": null, "tool_errors": 1,
  "stop_reason": "max_steps" }
```

## Metrics (`agent.evals`)

```python
from agent.evals import success_rate, step_efficiency, cost_per_task, summarize

success_rate(traces)      # wins / total                       (0.0 if empty)
step_efficiency(traces)   # mean steps over SUCCESSFUL runs     (lower = better)
cost_per_task(traces)     # mean cost_usd over ALL runs
summarize(traces)         # {n, success_rate, step_efficiency, cost_per_task}
```

| Metric | Formula | Averaged over |
|---|---|---|
| success rate | `wins / total` | all runs |
| step efficiency | `mean(steps)` | **successful** runs only |
| cost per task | `mean(cost_usd)` | all runs |

## Failure taxonomy (rule-based, V6.5)

```python
from agent.evals import classify_failure, failure_breakdown
classify_failure(trace)        # None if success, else a category
failure_breakdown(traces)      # {"max_steps_hit": 1, "tool_error": 1}
```

Rule order (first match wins): `max_steps_hit` → `tool_error` → `no_final_answer` → `wrong_answer`.

## Regression diff (V6.6)

```python
from agent.evals import regression_diff
d = regression_diff(before, after)   # match by task_id
d["regressions"]   # success -> fail   (sorted task ids)
d["fixes"]         # fail -> success
d["delta"]         # success_rate_after - before
```

## Eval harness

```python
from agent.evals import run_eval, load_traces, replay_runner
traces = load_traces("fixtures/traces/runA.json")

report = run_eval(tasks, runner, predicate=None)   # runner(task) -> trace
report = run_eval([{"task_id": "t1"}], replay_runner("fixtures/traces"))  # offline replay
```

## Gotchas

- **Step efficiency excludes failures** — they often hit the cap and would distort the mean.
- **Equal success rate can hide regressions.** Always diff per `task_id`, not just aggregates.
- **Failure classification is rule-based** (deterministic, gradeable) — not an LLM judge.
- **Empty trace list → 0.0**, never a divide-by-zero.
