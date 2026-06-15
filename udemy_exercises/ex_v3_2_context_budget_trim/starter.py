# Starter — complete the stubbed function
# Implements: EX3.3 (source V3.2)
# Self-contained: standard library + numpy only, no network, deterministic.

def count_tokens(text):
    # Provided proxy: ~1 token per whitespace word (no external tokenizer).
    return len(text.split())

def context_budget_trim(messages, budget):
    # Keep the system message + the most recent messages that fit the budget.
    raise NotImplementedError
