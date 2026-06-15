# Starter — complete the stubbed function
# Implements: EX4.2 (source V4.4)
# Self-contained: standard library + numpy only, no network, deterministic.

class RetryBudget:
    def __init__(self, max_retries):
        self.max_retries = max_retries
        self.used = 0

    def can_retry(self):
        raise NotImplementedError

    def consume(self):
        raise NotImplementedError

    @property
    def remaining(self):
        raise NotImplementedError
