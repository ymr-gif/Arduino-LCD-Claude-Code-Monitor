# Arduino LCD Claude Code Status Monitor

Passive, real-time display of Claude Code activity on a 16x2 LCD via Arduino.
Observer-only — never modifies or controls Claude Code.

---

## Concept

Claude Code runs normally in a terminal.
A separate observer process watches activity through Claude Code hooks, classifies the state, and sends it over USB serial to an Arduino, which displays it on a 16x2 LCD.

The LCD acts as a physical AI activity indicator — one glance shows what Claude is doing right now.

---

## LCD Layout

```
Row 1: [STATUS  ] [user msg]     <- 16 chars total
Row 2: IN:8192 OUT:4096          <- token usage
```

- Left 8 chars of row 1: current state label
- Right 8 chars of row 1: truncated user message snippet
- Row 2: input/output token counts for the active session

---

## Status Types

| Claude Code Tool     | LCD Label  |
|----------------------|------------|
| `Bash`               | `RUNNING ` |
| `Edit`               | `EDITING ` |
| `Write`              | `WRITING ` |
| `Read`               | `READING ` |
| `WebSearch`          | `WEBSRCH ` |
| `WebFetch`           | `FETCHING` |
| `Agent`              | `AGENT   ` |
| `TaskCreate`         | `PLANNING` |
| `Grep` / `Find`      | `SEARCH  ` |
| Between tools        | `THINKING` |
| `Stop` hook          | `IDLE    ` |
| `UserPromptSubmit`   | `WORKING ` |
| `Skill`              | `SKILL   ` |
| `NotebookEdit`       | `NOTEBOOK` |
| `ScheduleWakeup`     | `SCHEDULN` |
| Unknown              | `......  ` |

---

## File Structure

```
arduino-lcd-link/
├── CLAUDE.md                    # AI instructions for this project
├── README.md                    # this file
├── config.json                  # serial port, baud rate settings
├── install.sh                   # one-time setup (hooks + daemon)
│
├── hooks/                       # scripts fired by Claude Code automatically
│   ├── pre_tool.py              # captures tool name → infers state
│   ├── post_tool.py             # captures token counts after tool use
│   ├── on_stop.py               # fires when Claude goes idle
│   └── on_prompt.py             # captures user message snippet
│
├── observer/                    # main observer daemon
│   ├── main.py                  # entry point, runs as background daemon
│   ├── session_manager.py       # tracks all sessions, picks most recently active
│   ├── state_classifier.py      # maps tool name → status label string
│   ├── lcd_formatter.py         # formats 2-line 16x2 output with debounce
│   └── serial_bridge.py         # sends formatted lines to Arduino via pyserial
│
└── arduino/
    └── lcd_status/
        └── lcd_status.ino       # Arduino firmware, reads serial, drives LCD
```

---

## Data Flow

```
User types in Claude Code terminal
  └── Claude Code hook fires (pre_tool / post_tool / stop / prompt)
        └── hook script writes to /tmp/claude-lcd-sessions.json
              └── observer daemon reads file
                    └── session_manager picks most recently active session
                          └── state_classifier maps tool → label
                                └── lcd_formatter builds 2 lines (with debounce)
                                      └── serial_bridge sends over USB serial
                                            └── Arduino updates 16x2 LCD
```

---

## Session Tracking

Each hook writes a JSON entry:
```json
{
  "session_id": "abc123",
  "timestamp": 1748000000.000,
  "state": "EDITING ",
  "user_msg": "fix the bug",
  "tokens_in": 8192,
  "tokens_out": 4096
}
```

- All sessions tracked in `/tmp/claude-lcd-sessions.json`
- If multiple Claude Code instances are running, the one with the latest `timestamp` wins
- No configuration needed — most recently interacted session is always shown

---

## Key Design Decisions

- **Hook-based**: Claude Code fires hooks on every tool use. No polling, no scraping.
- **Token source**: `PostToolUse` hook receives usage data via stdin JSON — no external API needed.
- **Debounce**: 300ms debounce in `lcd_formatter.py` prevents LCD flicker on rapid state changes.
- **Daemon**: Observer runs in background. Start via `install.sh` which adds it to shell startup.
- **Serial protocol**: Arduino receives newline-delimited commands — `L1:THINKING askme..\nL2:IN:8192 OUT:4096\n`
- **Graceful fallback**: If Arduino disconnects, observer continues silently without crashing.

---

## Setup (planned)

1. Run `install.sh` — configures Claude Code hooks in `~/.claude/settings.json` and registers daemon in shell startup
2. Edit `config.json` — set correct serial port (`/dev/ttyUSB0` or `/dev/ttyACM0`) and baud rate
3. Flash `arduino/lcd_status/lcd_status.ino` via Arduino IDE
4. Open any terminal and run `claude` — LCD activates automatically

---

## Hardware

- Arduino (Uno or compatible)
- 16x2 LCD (HD44780-compatible)
- USB cable (for serial + power)
- Optional: I2C LCD module to reduce wiring

---

## Constraints

- Claude Code must remain unmodified
- No internal API access or reasoning introspection
- External observation only via official hook system
- Must handle unknown/ambiguous states gracefully
- Display must remain stable and readable — not a log feed
