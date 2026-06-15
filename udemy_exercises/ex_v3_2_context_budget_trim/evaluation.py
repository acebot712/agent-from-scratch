# Unit tests (one assertion each)
# Implements: EX3.3 (source V3.2)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import context_budget_trim, count_tokens


class Test_ex_v3_2_context_budget_trim(unittest.TestCase):
    def test_keeps_system_message(self):
        msgs = [{'role': 'system', 'content': 'sys'}, {'role': 'user', 'content': 'a b c'}]
        self.assertEqual(context_budget_trim(msgs, 5)[0]['role'], 'system')

    def test_prefers_recent_messages(self):
        msgs = [{'role': 'user', 'content': 'one two three'}, {'role': 'user', 'content': 'four'}]
        self.assertEqual(context_budget_trim(msgs, 1)[-1]['content'], 'four')

    def test_respects_budget(self):
        msgs = [{'role': 'user', 'content': 'a b'}, {'role': 'user', 'content': 'c d'}]
        kept = context_budget_trim(msgs, 2)
        self.assertLessEqual(sum(count_tokens(m['content']) for m in kept), 2)

    def test_zero_budget_returns_empty(self):
        self.assertEqual(context_budget_trim([{'role': 'user', 'content': 'x'}], 0), [])


if __name__ == "__main__":
    unittest.main()
