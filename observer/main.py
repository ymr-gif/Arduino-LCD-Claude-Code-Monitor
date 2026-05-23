#!/usr/bin/env python3
import sys
import time
import json
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from session_manager import get_active_session
from lcd_formatter import LCDFormatter
from serial_bridge import SerialBridge
from token_reader import read_session_tokens

CONFIG_PATH = Path(__file__).parent.parent / "config.json"
TOKEN_REFRESH_INTERVAL = 5.0

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def main():
    cfg       = load_config()
    formatter = LCDFormatter(debounce_ms=cfg.get("debounce_ms", 300))
    bridge    = SerialBridge(cfg["serial_port"], cfg["baud_rate"])
    interval  = cfg.get("observer_interval_ms", 100) / 1000
    dim_after = cfg.get("idle_dim_seconds", 120)

    last_token_refresh = 0.0
    cached_tokens: dict[str, tuple[int, int]] = {}
    idle_since   = None
    backlight_on = True

    def shutdown(sig, frame):
        bridge.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        session = get_active_session(cfg["state_file"])
        now     = time.monotonic()

        if session:
            sid   = session.get("session_id", "")
            state = (session.get("state") or "").strip()

            # refresh tokens from JSONL
            if sid and now - last_token_refresh >= TOKEN_REFRESH_INTERVAL:
                cached_tokens[sid]    = read_session_tokens(sid)
                last_token_refresh    = now
            if sid in cached_tokens:
                session["tokens_in"], session["tokens_out"] = cached_tokens[sid]

            # backlight / idle dim
            if state == "IDLE":
                if idle_since is None:
                    idle_since = now
                elif backlight_on and now - idle_since >= dim_after:
                    bridge.set_backlight(False)
                    backlight_on = False
            else:
                if not backlight_on:
                    bridge.set_backlight(True)
                    backlight_on = True
                idle_since = None

            lines = formatter.update(session)
            if lines:
                bridge.send(*lines)

        time.sleep(interval)

if __name__ == "__main__":
    main()
