import json
import fcntl

def get_active_session(state_file: str) -> dict | None:
    try:
        with open(state_file, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    if not data:
        return None

    best_id = max(data, key=lambda sid: data[sid].get("last_active", 0))
    session = data[best_id].copy()
    session["session_id"] = best_id
    return session
