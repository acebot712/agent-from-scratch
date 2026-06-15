# Unit tests (one assertion each)
# Implements: EX4.2 (source V4.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import RetryBudget


class Test_ex_v4_4_retry_budget(unittest.TestCase):
    def test_can_retry_initially(self):
        self.assertTrue(RetryBudget(2).can_retry())

    def test_consume_returns_true_while_available(self):
        b = RetryBudget(2)
        self.assertTrue(b.consume() and b.consume())

    def test_consume_false_past_budget(self):
        b = RetryBudget(1); b.consume()
        self.assertFalse(b.consume())

    def test_remaining_counts_down(self):
        b = RetryBudget(3); b.consume()
        self.assertEqual(b.remaining, 2)


if __name__ == "__main__":
    unittest.main()
