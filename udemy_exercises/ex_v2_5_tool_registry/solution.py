# Reference solution
# Implements: EX2.2 (source V2.5)
# Self-contained: standard library + numpy only, no network, deterministic.

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, fn):
        if name in self._tools:
            raise ValueError('already registered: ' + name)
        self._tools[name] = fn

    def has(self, name):
        return name in self._tools

    def names(self):
        return sorted(self._tools)

    def call(self, name, **kwargs):
        if name not in self._tools:
            raise KeyError(name)
        return self._tools[name](**kwargs)
