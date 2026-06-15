# Local autograder

Grade your assignment notebooks on your own machine — no submission server, no
API key required.

## Setup (once)

```bash
# from the repo root
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# copy the env template (only needed for the OPTIONAL live cells, not for grading)
cp .env.example .env
```

The grader itself never calls a model or the network — see "How grading works".

## Grade an assignment

```bash
python grader/grade.py 3          # grade assignments/assignment_3.ipynb
```

You'll get one `PASS`/`FAIL` line per check and a final score, e.g.:

```
== Grading assignment 3 ==

  [PASS] defines retrieve()
  [PASS] defines build_context()
  [PASS] retrieves the right top-2
  [PASS] build_context injects the top-k docs

Score: 4/4  (100%)
```

Want to see what a full score looks like? Grade the reference solution:

```bash
python grader/grade.py 3 --solution
```

## How grading works (and why it's stable)

Each assignment notebook defines a few **named functions** (the grader tells you
which in each notebook's intro). `grade.py`:

1. reads `assignments/assignment_N.ipynb`,
2. exec's its code cells to import your functions (cells that error — e.g. a demo
   that calls a function you haven't finished — are skipped, so partial work
   still grades),
3. runs assertion-based checks against your functions.

For LLM-dependent assignments (1, 4, 5) grading is **structural**: instead of a
real model, the grader injects a scripted fake (`llm(messages) -> str`), fake
workers, or fixed embedding/trace fixtures. So checks verify *behaviour you
control* — did the loop stop on the marker, did reflection respect the retry
budget, did delegation hit the cap, did you compute the metric right — never
exact model wording. That keeps scores deterministic and key-free.

Any cell that does hit a real provider is wrapped in
`if os.environ.get('RUN_LIVE') == '1':`, and the grader clears `RUN_LIVE`, so
grading does no network I/O. To run those demo cells yourself, open the notebook
in Jupyter with `RUN_LIVE=1` and your `.env` configured.

## Assignment map

| N | topic | graded on |
|---|---|---|
| 1 | agent loop | stops on marker, respects `max_steps` |
| 2 | tools/registry/dispatch | 3 tools, correct dispatch, unknown-tool handling |
| 3 | semantic retrieval | top-k correctness on a fixed embedding fixture |
| 4 | reflection/retry | improves within, and respects, the retry budget |
| 5 | multi-agent crew | routing, delegation cap, 3-way synthesis |
| 6 | eval suite | success rate / steps / cost / failure breakdown |
| 7 | hardening | cap enforcement + log-record shape |
| 8 | capstone | rubric checklist (no automated score) |

Run `python grader/grade.py 8` to print the capstone rubric.
