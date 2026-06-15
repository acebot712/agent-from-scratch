# Unit tests (one assertion each)
# Implements: EX6.1 (source V6.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import success_rate


class Test_ex_v6_4_success_rate(unittest.TestCase):
    def test_all_success(self):
        self.assertEqual(success_rate([{'success': True}, {'success': True}]), 1.0)

    def test_half_success(self):
        self.assertEqual(success_rate([{'success': True}, {'success': False}]), 0.5)

    def test_empty_is_zero(self):
        self.assertEqual(success_rate([]), 0.0)


if __name__ == "__main__":
    unittest.main()
