# Reference solution
# Implements: EX3.1 (source V3.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import numpy as np

def cosine_similarity(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
