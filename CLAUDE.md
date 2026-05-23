# Arduino LCD Claude Code Status Monitor

## Purpose
Passive real-time display of Claude Code activity on a 16x2 LCD via Arduino.
Observer-only — never modifies or controls Claude Code.

---

## Architecture
- **Hooks**: Claude Code fires `pre_tool`, `post_tool`, `stop`, `on_prompt` scripts
- **Shared state**: Hooks write to `/tmp/claude-lcd-sessions.json`
- **Observer daemon**: Reads state file, picks most recently active session
- **Serial bridge**: Sends formatted lines to Arduino via pyserial
- **Arduino firmware**: Reads serial, drives 16x2 LCD

---

## File Structure
```
arduino-lcd-link/
├── config.json
├── install.sh
├── hooks/
│   ├── pre_tool.py
│   ├── post_tool.py
│   ├── on_stop.py
│   └── on_prompt.py
├── observer/
│   ├── main.py
│   ├── session_manager.py
│   ├── state_classifier.py
│   ├── lcd_formatter.py
│   └── serial_bridge.py
└── arduino/
    └── lcd_status/
        └── lcd_status.ino
```

---

## LCD Layout
```
Row 1: [STATUS  ][user msg]   <- 8 chars each, 16 total
Row 2: IN:8192 OUT:4096       <- token usage, 16 chars
```

---

## Status Labels (8 chars each)
| Tool            | Label      |
|-----------------|------------|
| `Bash`          | `RUNNING ` |
| `Edit`          | `EDITING ` |
| `Write`         | `WRITING ` |
| `Read`          | `READING ` |
| `WebSearch`     | `WEBSRCH ` |
| `WebFetch`      | `FETCHING` |
| `Agent`         | `AGENT   ` |
| `TaskCreate`    | `PLANNING` |
| `Grep`/`Find`   | `SEARCH  ` |
| Between tools   | `THINKING` |
| `Stop` hook     | `IDLE    ` |
| `UserPrompt`    | `WORKING ` |
| `Skill`         | `SKILL   ` |
| `NotebookEdit`  | `NOTEBOOK` |
| `ScheduleWakeup`| `SCHEDULN` |
| Unknown         | `......  ` |

---

## Session Tracking
- Each hook writes: `{session_id, timestamp, state, user_msg, tokens_in, tokens_out}`
- Observer always picks session with latest `timestamp`
- Multiple Claude Code instances supported — most recently interacted wins automatically

---

## Serial Protocol
Arduino receives newline-delimited commands:
```
L1:THINKING askme..
L2:IN:8192 OUT:4096
```

---

## Key Rules
- Hook scripts must be fast and non-blocking (Claude Code waits for them)
- 300ms debounce in `lcd_formatter.py` — no LCD flicker
- Observer continues silently if Arduino disconnects
- Token data comes from `PostToolUse` hook stdin JSON — no scraping
- `install.sh` patches `~/.claude/settings.json` to register hooks

## Hard Constraints
- Do not modify Claude Code
- No internal API or reasoning access
- No verbose LCD output — status indicator only
- Do not block or slow Claude Code hooks
