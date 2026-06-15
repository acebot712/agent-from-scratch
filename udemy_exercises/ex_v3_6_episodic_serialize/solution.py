# Reference solution
# Implements: EX3.4 (source V3.6)
# Self-contained: standard library + numpy only, no network, deterministic.

import json

def serialize_episodes(episodes):
    return json.dumps(episodes, indent=2)

def deserialize_episodes(blob):
    if not blob.strip():
        return []
    return json.loads(blob)
