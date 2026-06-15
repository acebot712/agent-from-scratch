# Reference solution
# Implements: EX7.2 (source V7.4)
# Self-contained: standard library + numpy only, no network, deterministic.

def format_log_record(step, action, cost=0.0, cumulative=0.0):
    return {
        'step': step,
        'action': action,
        'cost_usd': round(cost, 6),
        'cumulative_cost_usd': round(cumulative, 6),
        'ok': True,
    }
