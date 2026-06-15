# Unit tests (one assertion each)
# Implements: EX6.3 (source V6.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import cost_per_task


class Test_ex_v6_4_cost_per_task(unittest.TestCase):
    def test_averages_cost(self):
        self.assertAlmostEqual(cost_per_task([{'cost_usd': 0.02}, {'cost_usd': 0.04}]), 0.03)

    def test_empty_is_zero(self):
        self.assertEqual(cost_per_task([]), 0.0)

    def test_missing_cost_treated_as_zero(self):
        self.assertAlmostEqual(cost_per_task([{'cost_usd': 0.10}, {}]), 0.05)


if __name__ == "__main__":
    unittest.main()
