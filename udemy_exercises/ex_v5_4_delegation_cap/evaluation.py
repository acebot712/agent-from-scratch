# Unit tests (one assertion each)
# Implements: EX5.2 (source V5.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import DelegationCap, DelegationError


class Test_ex_v5_4_delegation_cap(unittest.TestCase):
    def test_enter_increments_depth(self):
        self.assertEqual(DelegationCap(3).enter().depth, 1)

    def test_enter_raises_past_cap(self):
        cap = DelegationCap(2).enter().enter()
        self.assertRaises(DelegationError, cap.enter)

    def test_allows_true_below_cap(self):
        self.assertTrue(DelegationCap(1).allows())

    def test_allows_false_at_cap(self):
        self.assertFalse(DelegationCap(2, 2).allows())


if __name__ == "__main__":
    unittest.main()
