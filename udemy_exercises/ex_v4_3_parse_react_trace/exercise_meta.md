# EX4.1 — Parse a ReAct trace

**Implements:** EX4.1 (source V4.3)

## Learning objective
Parse Thought / Action / Observation lines into structured steps.

## Problem statement
Write `parse_react_trace(text)` returning a list of step dicts. A step may have `thought`, `action`, `action_input`, `observation`. Actions look like `Action: name[input]`. An `Observation:` line closes the current step; a new `Thought:` also starts a new step if the current one already has content.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Match each line type with its own regex; the action regex needs two groups: name and the text inside `[...]`.
2. Accumulate into a `cur` dict; push it to the list and reset on `Observation:` (and when a new `Thought:` begins a non-empty step).

## Solution explanation
ReAct interleaves reasoning and acting. Parsing the trace into discrete steps is what lets the loop pull out the next action to run and attach the observation back to the right place.
