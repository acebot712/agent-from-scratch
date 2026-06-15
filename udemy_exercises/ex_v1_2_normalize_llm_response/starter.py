# Starter — complete the stubbed function
# Implements: EX1.1 (source V1.2)
# Self-contained: standard library + numpy only, no network, deterministic.

import json

def normalize_llm_response(raw):
    # raw is an OpenAI-style dict: {'choices': [{'message': {...}, 'finish_reason': ...}]}
    # Return {'text': str, 'tool_calls': [{'name','args'}], 'stop_reason': ...}.
    raise NotImplementedError
