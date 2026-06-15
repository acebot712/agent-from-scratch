# Unit tests (one assertion each)
# Implements: EX5.3 (source V5.6)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import synthesize_outputs


class Test_ex_v5_6_synthesize_outputs(unittest.TestCase):
    def test_dedupes_preserving_order(self):
        self.assertEqual(synthesize_outputs(['a', 'b', 'a'])['parts'], ['a', 'b'])

    def test_drops_blanks(self):
        self.assertEqual(synthesize_outputs(['x', '', '  '])['parts'], ['x'])

    def test_combined_is_newline_joined(self):
        self.assertEqual(synthesize_outputs(['a', 'b'])['combined'], 'a\nb')

    def test_count_matches_parts(self):
        out = synthesize_outputs(['a', 'b', 'a', 'c'])
        self.assertEqual(out['count'], 3)


if __name__ == "__main__":
    unittest.main()
