# Starter — complete the stubbed function
# Implements: EX5.2 (source V5.4)
# Self-contained: standard library + numpy only, no network, deterministic.

class DelegationError(RuntimeError):
    pass

class DelegationCap:
    def __init__(self, max_depth, depth=0):
        self.max_depth = max_depth
        self.depth = depth

    def enter(self):
        raise NotImplementedError

    def allows(self):
        raise NotImplementedError
