# Reference solution
# Implements: EX6.5 (source V6.6)
# Self-contained: standard library + numpy only, no network, deterministic.

def regression_diff(before, after):
    b = {t['task_id']: bool(t.get('success')) for t in before}
    a = {t['task_id']: bool(t.get('success')) for t in after}
    common = b.keys() & a.keys()
    regressions = sorted(tid for tid in common if b[tid] and not a[tid])
    fixes = sorted(tid for tid in common if not b[tid] and a[tid])
    return {'regressions': regressions, 'fixes': fixes}
