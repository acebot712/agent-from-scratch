# Starter — complete the stubbed function
# Implements: EX3.2 (source V3.5)
# Self-contained: standard library + numpy only, no network, deterministic.

import numpy as np

def cosine(a, b):
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if d == 0 else float(np.dot(a, b) / d)

def top_k_retrieval(query_vec, doc_vecs, k):
    # Return [(index, score), ...] for the top-k docs, best first.
    raise NotImplementedError
