#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from state_utils import load_config, update_session

def main():
    event = json.loads(sys.stdin.read())
    session_id = event.get("session_id", "unknown")
    cfg = load_config()
    update_session(cfg["state_file"], session_id, state="IDLE    ")

if __name__ == "__main__":
    main()
