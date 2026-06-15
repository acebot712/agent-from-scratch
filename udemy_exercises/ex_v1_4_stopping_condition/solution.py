# Reference solution
# Implements: EX1.3 (source V1.4)
# Self-contained: standard library + numpy only, no network, deterministic.

def should_stop(text, step, max_steps):
    if step >= max_steps:
        return True
    if 'FINAL ANSWER:' in text:
        return True
    return False
