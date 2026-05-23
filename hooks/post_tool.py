#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from state_utils import load_config, read_state, update_session

def extract_tokens(event):
    usage = event.get("usage") or {}
    if not usage:
        resp = event.get("tool_response") or {}
        usage = resp.get("usage") or {}
    tokens_in = usage.get("input_tokens") or usage.get("cache_read_input_tokens", 0)
    tokens_out = usage.get("output_tokens", 0)
    return tokens_in, tokens_out

def main():
    event = json.loads(sys.stdin.read())
    session_id = event.get("session_id", "unknown")
    cfg = load_config()
    tokens_in, tokens_out = extract_tokens(event)

    if tokens_in or tokens_out:
        data = read_state(cfg["state_file"])
        existing = data.get(session_id, {})
        update_session(
            cfg["state_file"],
            session_id,
            tokens_in=existing.get("tokens_in", 0) + tokens_in,
            tokens_out=existing.get("tokens_out", 0) + tokens_out,
        )

if __name__ == "__main__":
    main()
