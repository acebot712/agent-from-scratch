# EX3.1 — Cosine similarity in numpy

**Implements:** EX3.1 (source V3.4)

## Learning objective
Compute cosine similarity between two vectors from scratch in numpy.

## Problem statement
Write `cosine_similarity(a, b)` returning the cosine of the angle between two vectors as a float: dot(a, b) / (||a|| * ||b||). If either vector has zero magnitude, return `0.0` (avoid dividing by zero).

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. `np.dot` gives the numerator; `np.linalg.norm` gives each magnitude.
2. Guard the denominator: if it's 0, return 0.0 before dividing.

## Solution explanation
Cosine similarity measures direction, not magnitude — it's the workhorse of semantic retrieval. Casting to float arrays and guarding the zero vector keeps it robust on real (and degenerate) embeddings.
