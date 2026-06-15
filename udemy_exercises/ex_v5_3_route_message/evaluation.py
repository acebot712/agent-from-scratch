# Unit tests (one assertion each)
# Implements: EX5.1 (source V5.3)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import route_message


class Test_ex_v5_3_route_message(unittest.TestCase):
    def test_routes_to_recipient(self):
        self.assertEqual(route_message({'recipient': 'writer'}, {'writer': 'W'}), 'W')

    def test_unknown_recipient_raises(self):
        self.assertRaises(KeyError, route_message, {'recipient': 'ghost'}, {'writer': 'W'})

    def test_picks_correct_among_many(self):
        roles = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(route_message({'recipient': 'b'}, roles), 2)


if __name__ == "__main__":
    unittest.main()
