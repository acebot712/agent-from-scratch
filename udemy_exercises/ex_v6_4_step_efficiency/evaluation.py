# Unit tests (one assertion each)
# Implements: EX6.2 (source V6.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import step_efficiency


class Test_ex_v6_4_step_efficiency(unittest.TestCase):
    def test_averages_successful_only(self):
        traces = [{'success': True, 'steps': 2}, {'success': True, 'steps': 4},
                  {'success': False, 'steps': 99}]
        self.assertEqual(step_efficiency(traces), 3.0)

    def test_no_success_is_zero(self):
        self.assertEqual(step_efficiency([{'success': False, 'steps': 5}]), 0.0)

    def test_single_success(self):
        self.assertEqual(step_efficiency([{'success': True, 'steps': 7}]), 7.0)


if __name__ == "__main__":
    unittest.main()
