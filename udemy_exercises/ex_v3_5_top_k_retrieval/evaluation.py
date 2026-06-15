# Unit tests (one assertion each)
# Implements: EX3.2 (source V3.5)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import top_k_retrieval


class Test_ex_v3_5_top_k_retrieval(unittest.TestCase):
    def test_returns_k_results(self):
        docs = [[1, 0], [0, 1], [1, 1]]
        self.assertEqual(len(top_k_retrieval([1, 0], docs, 2)), 2)

    def test_best_match_first(self):
        docs = [[0, 1], [1, 0.1], [0.9, 0]]
        self.assertEqual(top_k_retrieval([1, 0], docs, 1)[0][0], 2)

    def test_sorted_descending(self):
        docs = [[0, 1], [1, 0.1], [0.9, 0]]
        scores = [s for _, s in top_k_retrieval([1, 0], docs, 3)]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_k_zero_returns_empty(self):
        self.assertEqual(top_k_retrieval([1, 0], [[1, 0]], 0), [])


if __name__ == "__main__":
    unittest.main()
