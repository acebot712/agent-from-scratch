# Starter — complete the stubbed function
# Implements: EX2.2 (source V2.5)
# Self-contained: standard library + numpy only, no network, deterministic.

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, fn):
        raise NotImplementedError

    def has(self, name):
        raise NotImplementedError

    def names(self):
        raise NotImplementedError

    def call(self, name, **kwargs):
        raise NotImplementedError
