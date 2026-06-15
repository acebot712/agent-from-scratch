# Unit tests (one assertion each)
# Implements: EX7.3 (source V7.5)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import guardrail_check


class Test_ex_v7_5_guardrail_check(unittest.TestCase):
    def test_denylist_blocks(self):
        ok, reason = guardrail_check('rm', block=['rm'])
        self.assertFalse(ok)

    def test_denylist_wins_over_allowlist(self):
        ok, reason = guardrail_check('rm', allow=['rm'], block=['rm'])
        self.assertIn('denylist', reason)

    def test_allowlist_permits_listed(self):
        self.assertTrue(guardrail_check('search', allow=['search'])[0])

    def test_allowlist_blocks_unlisted(self):
        self.assertFalse(guardrail_check('delete', allow=['search'])[0])


if __name__ == "__main__":
    unittest.main()
