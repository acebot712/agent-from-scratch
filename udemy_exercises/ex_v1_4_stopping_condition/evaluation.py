# Unit tests (one assertion each)
# Implements: EX1.3 (source V1.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import should_stop


class Test_ex_v1_4_stopping_condition(unittest.TestCase):
    def test_stops_on_final_answer(self):
        self.assertTrue(should_stop('FINAL ANSWER: 7', 1, 6))

    def test_stops_at_step_cap(self):
        self.assertTrue(should_stop('still going', 6, 6))

    def test_continues_midway(self):
        self.assertFalse(should_stop('thinking', 2, 6))

    def test_step_cap_takes_priority_over_text(self):
        self.assertTrue(should_stop('no marker here', 10, 6))


if __name__ == "__main__":
    unittest.main()
