# Unit tests (one assertion each)
# Implements: EX2.1 (source V2.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import parse_tool_call


class Test_ex_v2_4_parse_tool_call(unittest.TestCase):
    def test_parses_name_and_args(self):
        self.assertEqual(parse_tool_call('TOOL: add\nARGS: {"a": 2, "b": 3}'),
                         {'name': 'add', 'args': {'a': 2, 'b': 3}})

    def test_none_when_no_tool_line(self):
        self.assertIsNone(parse_tool_call('The answer is 5.'))

    def test_empty_args_when_no_args_line(self):
        self.assertEqual(parse_tool_call('TOOL: now')['args'], {})

    def test_malformed_json_degrades_to_empty(self):
        self.assertEqual(parse_tool_call('TOOL: add\nARGS: {not json}')['args'], {})


if __name__ == "__main__":
    unittest.main()
