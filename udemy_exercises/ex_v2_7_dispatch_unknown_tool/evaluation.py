# Unit tests (one assertion each)
# Implements: EX2.3 (source V2.5 + V2.7)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import dispatch


class Test_ex_v2_7_dispatch_unknown_tool(unittest.TestCase):
    def test_runs_known_tool(self):
        reg = {'add': lambda a, b: a + b}
        self.assertEqual(dispatch(reg, 'add', {'a': 2, 'b': 3}), {'ok': True, 'output': 5})

    def test_unknown_tool_is_not_ok(self):
        self.assertFalse(dispatch({}, 'ghost', {})['ok'])

    def test_unknown_tool_error_mentions_unknown(self):
        self.assertIn('unknown', dispatch({}, 'ghost', {})['error'])

    def test_bad_arguments_handled(self):
        reg = {'add': lambda a, b: a + b}
        self.assertIn('bad arguments', dispatch(reg, 'add', {'a': 1})['error'])


if __name__ == "__main__":
    unittest.main()
