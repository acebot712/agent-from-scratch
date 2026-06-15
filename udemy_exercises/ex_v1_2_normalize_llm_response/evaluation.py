# Unit tests (one assertion each)
# Implements: EX1.1 (source V1.2)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import normalize_llm_response


class Test_ex_v1_2_normalize_llm_response(unittest.TestCase):
    def test_extracts_text(self):
        raw = {'choices': [{'message': {'content': 'hello'}, 'finish_reason': 'stop'}]}
        self.assertEqual(normalize_llm_response(raw)['text'], 'hello')

    def test_null_content_becomes_empty_string(self):
        raw = {'choices': [{'message': {'content': None}, 'finish_reason': 'stop'}]}
        self.assertEqual(normalize_llm_response(raw)['text'], '')

    def test_maps_stop_reason(self):
        raw = {'choices': [{'message': {'content': 'x'}, 'finish_reason': 'length'}]}
        self.assertEqual(normalize_llm_response(raw)['stop_reason'], 'length')

    def test_parses_tool_call_arguments_to_dict(self):
        raw = {'choices': [{'message': {'content': None, 'tool_calls': [
            {'function': {'name': 'add', 'arguments': '{"a": 1, "b": 2}'}}]},
            'finish_reason': 'tool_calls'}]}
        out = normalize_llm_response(raw)
        self.assertEqual(out['tool_calls'], [{'name': 'add', 'args': {'a': 1, 'b': 2}}])


if __name__ == "__main__":
    unittest.main()
