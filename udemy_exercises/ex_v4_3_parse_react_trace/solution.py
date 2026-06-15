# Reference solution
# Implements: EX4.1 (source V4.3)
# Self-contained: standard library + numpy only, no network, deterministic.

import re

_THOUGHT = re.compile(r'Thought:\s*(.+)')
_ACTION = re.compile(r'Action:\s*([A-Za-z0-9_\-]+)\s*\[(.*?)\]')
_OBS = re.compile(r'Observation:\s*(.+)')

def parse_react_trace(text):
    steps = []
    cur = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _THOUGHT.match(line)
        if m:
            if cur.get('thought') or cur.get('action'):
                steps.append(cur); cur = {}
            cur['thought'] = m.group(1).strip(); continue
        m = _ACTION.match(line)
        if m:
            cur['action'] = m.group(1).strip()
            cur['action_input'] = m.group(2).strip(); continue
        m = _OBS.match(line)
        if m:
            cur['observation'] = m.group(1).strip()
            steps.append(cur); cur = {}
    if cur.get('thought') or cur.get('action'):
        steps.append(cur)
    return steps
