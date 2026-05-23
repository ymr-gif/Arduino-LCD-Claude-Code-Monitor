#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS="$HOME/.claude/settings.json"
SHELL_RC="$HOME/.bashrc"
[[ "$SHELL" == */zsh ]] && SHELL_RC="$HOME/.zshrc"

echo "[1/3] Patching Claude Code hooks in $SETTINGS"

python3 - <<EOF
import json, os, sys

settings_path = "$SETTINGS"
project_dir = "$PROJECT_DIR"

os.makedirs(os.path.dirname(settings_path), exist_ok=True)

try:
    with open(settings_path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

hooks = settings.setdefault("hooks", {})

def make_hook(script):
    return {
        "matcher": "",
        "hooks": [{"type": "command", "command": f"python3 {project_dir}/hooks/{script}"}]
    }

hooks.setdefault("PreToolUse", []).append(make_hook("pre_tool.py"))
hooks.setdefault("PostToolUse", []).append(make_hook("post_tool.py"))
hooks.setdefault("Stop", []).append(make_hook("on_stop.py"))
hooks.setdefault("UserPromptSubmit", []).append(make_hook("on_prompt.py"))

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)

print(f"  hooks written to {settings_path}")
EOF

echo "[2/3] Installing pyserial"
if python3 -c "import serial" 2>/dev/null; then
  echo "  pyserial already installed"
else
  sudo apt-get install -y python3-serial
fi

echo "[3/3] Registering observer daemon in $SHELL_RC"
DAEMON_LINE="python3 $PROJECT_DIR/observer/main.py &>/tmp/claude-lcd-observer.log &"
MARKER="# claude-lcd-observer"

if ! grep -q "$MARKER" "$SHELL_RC"; then
  echo "" >> "$SHELL_RC"
  echo "$MARKER" >> "$SHELL_RC"
  echo "$DAEMON_LINE" >> "$SHELL_RC"
  echo "  added to $SHELL_RC"
else
  echo "  already registered in $SHELL_RC"
fi

echo ""
echo "Done. Next steps:"
echo "  1. Edit config.json — set serial_port to your Arduino port"
echo "  2. Flash arduino/lcd_status/lcd_status.ino via Arduino IDE"
echo "  3. Open a new terminal — observer starts automatically"
echo "  4. Run claude — LCD activates on first tool use"
