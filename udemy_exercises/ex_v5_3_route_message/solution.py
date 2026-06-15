# Reference solution
# Implements: EX5.1 (source V5.3)
# Self-contained: standard library + numpy only, no network, deterministic.

def route_message(message, roles):
    recipient = message['recipient']
    if recipient not in roles:
        raise KeyError("no agent for role '" + str(recipient) + "'")
    return roles[recipient]
