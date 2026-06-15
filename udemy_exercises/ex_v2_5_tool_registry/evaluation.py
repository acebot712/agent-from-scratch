# Unit tests (one assertion each)
# Implements: EX2.2 (source V2.5)
# Self-contained: standard library + numpy only, no network, deterministic.

import unittest
from solution import ToolRegistry


class Test_ex_v2_5_tool_registry(unittest.TestCase):
    def test_register_then_call(self):
        reg = ToolRegistry(); reg.register('add', lambda a, b: a + b)
        self.assertEqual(reg.call('add', a=2, b=3), 5)

    def test_names_are_sorted(self):
        reg = ToolRegistry(); reg.register('b', lambda: 1); reg.register('a', lambda: 2)
        self.assertEqual(reg.names(), ['a', 'b'])

    def test_duplicate_registration_raises(self):
        reg = ToolRegistry(); reg.register('x', lambda: 1)
        self.assertRaises(ValueError, reg.register, 'x', lambda: 2)

    def test_unknown_call_raises_keyerror(self):
        reg = ToolRegistry()
        self.assertRaises(KeyError, reg.call, 'ghost')


if __name__ == "__main__":
    unittest.main()
