# Reference solution
# Implements: EX2.1 (source V2.4)
# Self-contained: standard library + numpy only, no network, deterministic.

import json
import re

def parse_tool_call(text):
    m_name = re.search(r'TOOL:\s*([A-Za-z0-9_\-]+)', text)
    if not m_name:
        return None
    m_args = re.search(r'ARGS:\s*(\{.*\})\s*$', text, re.DOTALL)
    args = {}
    if m_args:
        try:
            parsed = json.loads(m_args.group(1))
            args = parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            args = {}
    return {'name': m_name.group(1), 'args': args}
