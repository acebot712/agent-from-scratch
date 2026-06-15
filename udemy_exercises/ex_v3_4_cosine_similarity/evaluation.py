# Unit tests (one assertion each)
# Implements: EX3.1 (source V3.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import cosine_similarity


class Test_ex_v3_4_cosine_similarity(unittest.TestCase):
    def test_identical_vectors_are_one(self):
        self.assertAlmostEqual(cosine_similarity([1, 2, 3], [1, 2, 3]), 1.0)

    def test_orthogonal_vectors_are_zero(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_opposite_vectors_are_minus_one(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [-1, 0]), -1.0)

    def test_zero_vector_guard(self):
        self.assertEqual(cosine_similarity([0, 0], [1, 1]), 0.0)


if __name__ == "__main__":
    unittest.main()
