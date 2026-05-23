# Arduino LCD Claude Code Status Monitor

## Purpose
Passive real-time display of Claude Code activity on a 16×2 I2C LCD via Arduino Uno.
Observer-only — never modifies or controls Claude Code.

---

## Architecture
- **Hooks**: Claude Code fires `pre_tool`, `post_tool`, `on_stop`, `on_prompt` scripts on every event
- **Shared state**: Hooks write to `/tmp/claude-lcd-sessions.json` with file locking
- **Observer daemon**: Reads state file every 100ms, picks most recently active session
- **Serial bridge**: Sends formatted lines to Arduino via pyserial (`/dev/ttyACM0`, 9600 baud)
- **Arduino firmware**: Reads serial commands, drives 16×2 LCD via I2C (address `0x27`)

---

## File Structure
```
arduino-lcd-link/
├── config.json                  # Serial port, timing, idle dim settings
├── install.sh                   # One-command setup
├── hooks/
│   ├── state_utils.py           # Shared file I/O with fcntl locking
│   ├── pre_tool.py              # PreToolUse → sets state
│   ├── post_tool.py             # PostToolUse → token tracking (unused, see token_reader)
│   ├── on_stop.py               # Stop → sets IDLE
│   └── on_prompt.py             # UserPromptSubmit → sets WORKING
├── observer/
│   ├── main.py                  # Daemon loop, idle dim logic
│   ├── session_manager.py       # Picks session with latest last_active timestamp
│   ├── state_classifier.py      # Tool name → state key, display label, description
│   ├── lcd_formatter.py         # 16×2 formatter: ticker scroll, row2 cycling, debounce
│   ├── serial_bridge.py         # pyserial wrapper with auto-reconnect + backlight control
│   └── token_reader.py          # Reads token counts from Claude Code JSONL session logs
└── arduino/
    └── lcd_status/
        └── lcd_status.ino       # Arduino firmware: serial parser, I2C LCD, PWM dim
```

---

## LCD Layout

**Row 1** — state label + `=` + scrolling description ticker (16 chars):
```
EDITING= Modifying ex   <- scrolls left continuously, loops with gap
```

**Row 2** — token usage, cycles every 5 seconds:
```
I=8k O=3k               <- cycle 1: input / output
T=11k                   <- cycle 2: total
```

---

## Status Labels
| Tool / Event         | State key  | LCD Label  | Description                  |
|----------------------|------------|------------|------------------------------|
| `Bash`               | `RUNNING ` | `RUNNING`  | Executing shell command       |
| `Edit`               | `EDITING ` | `EDITING`  | Modifying existing file       |
| `Write`              | `WRITING ` | `WRITING`  | Creating new file             |
| `Read`               | `READING ` | `READING`  | Reading file contents         |
| `WebSearch`          | `WEBSRCH ` | `WEBSRCH`  | Searching the web             |
| `WebFetch`           | `FETCHING` | `FETCH`    | Fetching web content          |
| `Agent`              | `AGENT   ` | `AGENT`    | Delegating to subagent        |
| `Task*`              | `PLANNING` | `PLANNIN`  | Planning task structure       |
| `Grep` / `Explore`   | `SEARCH  ` | `SEARCH`   | Searching codebase            |
| `Skill`              | `SKILL   ` | `SKILL`    | Running skill module          |
| `NotebookEdit`       | `NOTEBOOK` | `NOTEBK`   | Editing notebook cells        |
| `ScheduleWakeup`     | `SCHEDULN` | `SCHEDUL`  | Scheduling a task             |
| Between tools        | `THINKING` | `THINKIN`  | Thinking it through           |
| `UserPromptSubmit`   | `WORKING ` | `WORKING`  | Processing message            |
| `Stop` hook          | `IDLE    ` | `IDLE`     | Waiting for input             |

---

## Session Tracking
- Each hook writes `{state, last_active, tokens_in, tokens_out}` keyed by `session_id`
- Observer picks session with max `last_active` timestamp
- Multiple Claude Code instances supported — most recently interacted wins automatically
- `/tmp/` storage clears on reboot; tokens reset with each new `claude` invocation

---

## Token Counting
- Source: `~/.claude/projects/*/[session-id].jsonl` — Claude Code's own session logs
- Counts: `input_tokens + cache_creation_input_tokens` (I) and `output_tokens` (O)
- Excludes `cache_read_input_tokens` — grows unboundedly with context, not a useful metric
- Deduplicates by message ID to avoid double-counting repeated JSONL entries
- Refreshed every 5 seconds in the observer loop

---

## Serial Protocol
```
L1:<16 chars>    → update row 1
L2:<16 chars>    → update row 2 and refresh LCD
BL:1             → backlight full on
BL:0             → backlight 50% (software PWM at 100Hz via millis())
```

---

## Key Rules
- Hook scripts must be fast and non-blocking — Claude Code waits for them to exit
- 300ms debounce in `lcd_formatter.py` — rapid tool sequences don't cause flicker
- Ticker scroll advances every 300ms (3 ticks × 100ms interval)
- Row 2 cycles every 5 seconds (50 ticks × 100ms interval)
- Backlight dims after 120s of IDLE, restores immediately on any activity
- Observer reconnects to Arduino silently if serial port disconnects
- `install.sh` merges hooks into `~/.claude/settings.json` without overwriting existing config

## Hard Constraints
- Do not modify Claude Code
- No internal API or reasoning access
- No verbose LCD output — status indicator only
- Do not block or slow Claude Code hook scripts
