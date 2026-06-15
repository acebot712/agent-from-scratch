# Reference solution
# Implements: EX4.2 (source V4.4)
# Self-contained: standard library + numpy only, no network, deterministic.

class RetryBudget:
    def __init__(self, max_retries):
        self.max_retries = max_retries
        self.used = 0

    def can_retry(self):
        return self.used < self.max_retries

    def consume(self):
        if not self.can_retry():
            return False
        self.used += 1
        return True

    @property
    def remaining(self):
        return max(0, self.max_retries - self.used)
