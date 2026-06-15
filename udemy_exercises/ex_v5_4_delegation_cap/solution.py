# Reference solution
# Implements: EX5.2 (source V5.4)
# Self-contained: standard library + numpy only, no network, deterministic.

class DelegationError(RuntimeError):
    pass

class DelegationCap:
    def __init__(self, max_depth, depth=0):
        self.max_depth = max_depth
        self.depth = depth

    def enter(self):
        if self.depth >= self.max_depth:
            raise DelegationError('delegation depth cap exceeded')
        return DelegationCap(self.max_depth, self.depth + 1)

    def allows(self):
        return self.depth < self.max_depth
