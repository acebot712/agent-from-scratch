# Reference solution
# Implements: EX7.3 (source V7.5)
# Self-contained: standard library + numpy only, no network, deterministic.

def guardrail_check(tool_name, allow=None, block=None):
    if block and tool_name in block:
        return False, "'" + tool_name + "' is on the denylist"
    if allow is not None and tool_name not in allow:
        return False, "'" + tool_name + "' is not on the allowlist"
    return True, 'allowed'
