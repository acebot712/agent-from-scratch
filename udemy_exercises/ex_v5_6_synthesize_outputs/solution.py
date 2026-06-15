# Reference solution
# Implements: EX5.3 (source V5.6)
# Self-contained: standard library + numpy only, no network, deterministic.

def synthesize_outputs(outputs, dedupe=True):
    parts = []
    seen = set()
    for o in outputs:
        o = (o or '').strip()
        if not o:
            continue
        if dedupe and o in seen:
            continue
        seen.add(o)
        parts.append(o)
    return {'parts': parts, 'combined': '\n'.join(parts), 'count': len(parts)}
