# Unit tests (one assertion each)
# Implements: EX7.1 (source V7.2)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import enforce_caps


class Test_ex_v7_2_enforce_caps(unittest.TestCase):
    def test_step_cap_fires(self):
        self.assertIn('max_steps', enforce_caps(5, 0.0, max_steps=5))

    def test_cost_cap_fires(self):
        self.assertIn('max_cost', enforce_caps(1, 0.51, max_cost=0.50))

    def test_within_caps_returns_none(self):
        self.assertIsNone(enforce_caps(4, 0.10, max_steps=5, max_cost=0.50))

    def test_no_caps_set_never_halts(self):
        self.assertIsNone(enforce_caps(999, 999.0))


if __name__ == "__main__":
    unittest.main()
