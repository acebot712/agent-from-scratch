# Reference solution
# Implements: EX4.3 (source V4.6)
# Self-contained: standard library + numpy only, no network, deterministic.

def select_strategy(meta):
    if meta.get('needs_tools'):
        return 'react'
    if meta.get('verifiable') and meta.get('difficulty') == 'hard':
        return 'reflection'
    if meta.get('open_ended') or meta.get('branching'):
        return 'tot'
    return 'direct'
