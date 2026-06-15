# EX3.2 — Top-k retrieval

**Implements:** EX3.2 (source V3.5)

## Learning objective
Rank document vectors by similarity to a query and return the top-k.

## Problem statement
Given a `query_vec` and a list of precomputed `doc_vecs`, write `top_k_retrieval(query_vec, doc_vecs, k)` returning a list of `(index, score)` tuples for the `k` most similar docs, sorted by score descending. Use cosine similarity. Input is **vectors**, not text.

Edit `starter.py` so the target function works; the file you submit is imported by the tests as `solution`. Standard library + numpy only.

## Hints
1. Score every doc with the provided `cosine`, keeping its index alongside the score.
2. Sort the `(index, score)` pairs by score descending, then slice `[:k]`.

## Solution explanation
Retrieval without a vector DB is just: score all candidates, sort, take the top few. Keeping the index lets the caller map a hit back to its source document.
