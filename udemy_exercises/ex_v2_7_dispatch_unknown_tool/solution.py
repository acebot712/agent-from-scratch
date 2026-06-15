# Reference solution
# Implements: EX2.3 (source V2.5 + V2.7)
# Self-contained: standard library + numpy only, no network, deterministic.

def dispatch(registry, name, args):
    if name not in registry:
        return {'ok': False, 'error': "unknown tool '" + name + "'"}
    try:
        output = registry[name](**args)
    except TypeError as exc:
        return {'ok': False, 'error': 'bad arguments: ' + str(exc)}
    return {'ok': True, 'output': output}
