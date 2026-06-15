# Reference solution
# Implements: EX1.1 (source V1.2)
# Self-contained: standard library + numpy only, no network, deterministic.

import json

def normalize_llm_response(raw):
    choice = raw['choices'][0]
    msg = choice.get('message', {})
    tool_calls = []
    for tc in msg.get('tool_calls') or []:
        fn = tc.get('function', {})
        args = fn.get('arguments') or '{}'
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            args = {}
        tool_calls.append({'name': fn.get('name', ''), 'args': args})
    return {
        'text': msg.get('content') or '',
        'tool_calls': tool_calls,
        'stop_reason': choice.get('finish_reason'),
    }
