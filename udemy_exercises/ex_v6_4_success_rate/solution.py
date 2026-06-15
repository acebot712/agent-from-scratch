# Reference solution
# Implements: EX6.1 (source V6.4)
# Self-contained: standard library + numpy only, no network, deterministic.

def success_rate(traces):
    if not traces:
        return 0.0
    return sum(1 for t in traces if t.get('success')) / len(traces)
