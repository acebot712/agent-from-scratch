# Unit tests (one assertion each)
# Implements: EX4.3 (source V4.6)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import select_strategy


class Test_ex_v4_6_select_strategy(unittest.TestCase):
    def test_tools_means_react(self):
        self.assertEqual(select_strategy({'needs_tools': True}), 'react')

    def test_hard_verifiable_means_reflection(self):
        self.assertEqual(select_strategy({'verifiable': True, 'difficulty': 'hard'}), 'reflection')

    def test_open_ended_means_tot(self):
        self.assertEqual(select_strategy({'open_ended': True}), 'tot')

    def test_default_is_direct(self):
        self.assertEqual(select_strategy({}), 'direct')


if __name__ == "__main__":
    unittest.main()
