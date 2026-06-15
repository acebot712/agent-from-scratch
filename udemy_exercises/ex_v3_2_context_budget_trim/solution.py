# Reference solution
# Implements: EX3.3 (source V3.2)
# Self-contained: standard library + numpy only, no network, deterministic.

def count_tokens(text):
    return len(text.split())

def context_budget_trim(messages, budget):
    if budget <= 0:
        return []
    system = []
    rest = list(messages)
    if rest and rest[0].get('role') == 'system':
        system = [rest.pop(0)]
    remaining = budget - sum(count_tokens(m.get('content', '')) for m in system)
    kept = []
    for m in reversed(rest):
        cost = count_tokens(m.get('content', ''))
        if cost <= remaining:
            kept.append(m)
            remaining -= cost
        else:
            break
    return system + list(reversed(kept))
