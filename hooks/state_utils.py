import json
import os
import time
import fcntl
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def read_state(state_file):
    try:
        with open(state_file, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_state(state_file, data):
    tmp = state_file + ".tmp"
    with open(tmp, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f)
        fcntl.flock(f, fcntl.LOCK_UN)
    os.replace(tmp, state_file)

def update_session(state_file, session_id, **fields):
    data = read_state(state_file)
    if session_id not in data:
        data[session_id] = {
            "state": "WORKING ",
            "user_msg": "",
            "tokens_in": 0,
            "tokens_out": 0,
            "last_active": time.time(),
        }
    data[session_id].update(fields)
    data[session_id]["last_active"] = time.time()
    write_state(state_file, data)
