# Unit tests (one assertion each)
# Implements: EX7.2 (source V7.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import format_log_record


class Test_ex_v7_4_format_log_record(unittest.TestCase):
    def test_has_exact_keys(self):
        rec = format_log_record(1, 'llm_call')
        self.assertEqual(set(rec), {'step', 'action', 'cost_usd', 'cumulative_cost_usd', 'ok'})

    def test_carries_step_and_action(self):
        rec = format_log_record(3, 'tool_call')
        self.assertEqual((rec['step'], rec['action']), (3, 'tool_call'))

    def test_rounds_cost(self):
        rec = format_log_record(1, 'x', cost=0.123456789)
        self.assertEqual(rec['cost_usd'], 0.123457)

    def test_ok_defaults_true(self):
        self.assertTrue(format_log_record(1, 'x')['ok'])


if __name__ == "__main__":
    unittest.main()
