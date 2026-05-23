import json
import glob
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude" / "projects"

def read_session_tokens(session_id: str) -> tuple[int, int]:
    matches = glob.glob(str(CLAUDE_DIR / "*" / f"{session_id}.jsonl"))
    if not matches:
        return 0, 0

    seen = set()
    tokens_in = tokens_out = 0

    try:
        with open(matches[0]) as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    msg = obj.get("message", {})
                    if not isinstance(msg, dict) or msg.get("role") != "assistant":
                        continue
                    msg_id = msg.get("id")
                    if not msg_id or msg_id in seen:
                        continue
                    seen.add(msg_id)
                    usage = msg.get("usage", {})
                    # exclude cache_read_input_tokens — grows unboundedly with context
                    tokens_in += (
                        usage.get("input_tokens", 0)
                        + usage.get("cache_creation_input_tokens", 0)
                    )
                    tokens_out += usage.get("output_tokens", 0)
                except (json.JSONDecodeError, AttributeError):
                    continue
    except (IOError, OSError):
        pass

    return tokens_in, tokens_out
