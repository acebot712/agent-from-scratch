# Unit tests (one assertion each)
# Implements: EX1.2 (source V1.3)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import parse_intent


class Test_ex_v1_3_parse_intent(unittest.TestCase):
    def test_detects_final_answer(self):
        self.assertEqual(parse_intent('done. FINAL ANSWER: 42'),
                         {'kind': 'final', 'value': '42'})

    def test_detects_action_name(self):
        self.assertEqual(parse_intent('ACTION: get_weather("Paris")')['name'], 'get_weather')

    def test_action_captures_args_text(self):
        self.assertEqual(parse_intent('ACTION: add(2, 3)')['args_text'], '2, 3')

    def test_unknown_when_neither(self):
        self.assertEqual(parse_intent('just chatting'), {'kind': 'unknown'})


if __name__ == "__main__":
    unittest.main()
