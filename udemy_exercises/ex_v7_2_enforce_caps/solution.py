# Reference solution
# Implements: EX7.1 (source V7.2)
# Self-contained: standard library + numpy only, no network, deterministic.

def enforce_caps(steps, cost, max_steps=None, max_cost=None):
    if max_steps is not None and steps >= max_steps:
        return 'max_steps (' + str(max_steps) + ') reached'
    if max_cost is not None and cost >= max_cost:
        return 'max_cost ($' + str(max_cost) + ') reached'
    return None
