# Unit tests (one assertion each)
# Implements: EX4.1 (source V4.3)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import parse_react_trace


class Test_ex_v4_3_parse_react_trace(unittest.TestCase):
    def test_parses_action_name(self):
        steps = parse_react_trace('Thought: add them\nAction: add[2, 3]\nObservation: 5')
        self.assertEqual(steps[0]['action'], 'add')

    def test_parses_action_input(self):
        steps = parse_react_trace('Action: add[2, 3]\nObservation: 5')
        self.assertEqual(steps[0]['action_input'], '2, 3')

    def test_observation_closes_step(self):
        steps = parse_react_trace('Thought: a\nAction: x[1]\nObservation: ok')
        self.assertEqual(steps[0]['observation'], 'ok')

    def test_two_steps(self):
        text = 'Thought: a\nAction: x[1]\nObservation: o1\nThought: b\nAction: y[2]\nObservation: o2'
        self.assertEqual(len(parse_react_trace(text)), 2)


if __name__ == "__main__":
    unittest.main()
