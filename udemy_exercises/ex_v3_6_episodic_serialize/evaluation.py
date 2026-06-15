# Unit tests (one assertion each)
# Implements: EX3.4 (source V3.6)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import serialize_episodes, deserialize_episodes


class Test_ex_v3_6_episodic_serialize(unittest.TestCase):
    def test_round_trip_preserves_data(self):
        eps = [{'role': 'user', 'content': 'hi', 'meta': {'step': 1}}]
        self.assertEqual(deserialize_episodes(serialize_episodes(eps)), eps)

    def test_serialize_returns_string(self):
        self.assertIsInstance(serialize_episodes([]), str)

    def test_empty_string_deserialises_to_empty_list(self):
        self.assertEqual(deserialize_episodes('   '), [])

    def test_output_is_valid_json(self):
        import json as _j
        self.assertEqual(_j.loads(serialize_episodes([{'a': 1}])), [{'a': 1}])


if __name__ == "__main__":
    unittest.main()
