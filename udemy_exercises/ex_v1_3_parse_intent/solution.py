# Reference solution
# Implements: EX1.2 (source V1.3)
# Self-contained: standard library + numpy only, no network, deterministic.

import re

def parse_intent(text):
    if 'FINAL ANSWER:' in text:
        return {'kind': 'final', 'value': text.split('FINAL ANSWER:', 1)[1].strip()}
    m = re.search(r'ACTION:\s*([A-Za-z0-9_]+)\((.*)\)', text)
    if m:
        return {'kind': 'action', 'name': m.group(1), 'args_text': m.group(2).strip()}
    return {'kind': 'unknown'}
