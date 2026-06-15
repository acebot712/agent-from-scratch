# Unit tests (one assertion each)
# Implements: EX6.4 (source V6.5)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import classify_failure


class Test_ex_v6_5_classify_failure(unittest.TestCase):
    def test_success_returns_none(self):
        self.assertIsNone(classify_failure({'success': True}))

    def test_max_steps_hit(self):
        self.assertEqual(classify_failure(
            {'success': False, 'stop_reason': 'max_steps', 'steps': 8, 'max_steps': 8}),
            'max_steps_hit')

    def test_tool_error(self):
        self.assertEqual(classify_failure(
            {'success': False, 'stop_reason': 'error', 'tool_errors': 1}), 'tool_error')

    def test_wrong_answer_when_answer_present(self):
        self.assertEqual(classify_failure(
            {'success': False, 'final_answer': 'nope', 'steps': 2, 'max_steps': 8}),
            'wrong_answer')


if __name__ == "__main__":
    unittest.main()
