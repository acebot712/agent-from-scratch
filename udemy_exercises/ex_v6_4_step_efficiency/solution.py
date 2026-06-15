# Reference solution
# Implements: EX6.2 (source V6.4)
# Self-contained: standard library + numpy only, no network, deterministic.

def step_efficiency(traces):
    wins = [t for t in traces if t.get('success')]
    if not wins:
        return 0.0
    return sum(t.get('steps', 0) for t in wins) / len(wins)
