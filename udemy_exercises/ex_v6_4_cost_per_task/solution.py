# Reference solution
# Implements: EX6.3 (source V6.4)
# Self-contained: standard library + numpy only, no network, deterministic.

def cost_per_task(traces):
    if not traces:
        return 0.0
    return sum(float(t.get('cost_usd', 0.0)) for t in traces) / len(traces)
