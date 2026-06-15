# Reference solution
# Implements: EX6.4 (source V6.5)
# Self-contained: standard library + numpy only, no network, deterministic.

def classify_failure(trace):
    if trace.get('success'):
        return None
    if trace.get('stop_reason') == 'max_steps' or \
            trace.get('steps', 0) >= trace.get('max_steps', float('inf')):
        return 'max_steps_hit'
    if trace.get('tool_errors', 0) > 0 or trace.get('stop_reason') == 'error':
        return 'tool_error'
    if not trace.get('final_answer'):
        return 'no_final_answer'
    return 'wrong_answer'
