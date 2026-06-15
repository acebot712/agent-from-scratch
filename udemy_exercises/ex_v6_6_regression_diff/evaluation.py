# Unit tests (one assertion each)
# Implements: EX6.5 (source V6.6)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import regression_diff


class Test_ex_v6_6_regression_diff(unittest.TestCase):
    def test_detects_regression(self):
        before = [{'task_id': 't1', 'success': True}]
        after = [{'task_id': 't1', 'success': False}]
        self.assertEqual(regression_diff(before, after)['regressions'], ['t1'])

    def test_detects_fix(self):
        before = [{'task_id': 't1', 'success': False}]
        after = [{'task_id': 't1', 'success': True}]
        self.assertEqual(regression_diff(before, after)['fixes'], ['t1'])

    def test_unchanged_has_no_diff(self):
        before = [{'task_id': 't1', 'success': True}]
        after = [{'task_id': 't1', 'success': True}]
        self.assertEqual(regression_diff(before, after), {'regressions': [], 'fixes': []})


if __name__ == "__main__":
    unittest.main()
