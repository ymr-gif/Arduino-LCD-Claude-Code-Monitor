# Arduino LCD Claude Code Monitor

A real-time physical status display for [Claude Code](https://claude.ai/code) — an Arduino-driven 16×2 LCD that shows what the AI is doing at a glance, without modifying or interfering with Claude Code in any way.

> Think of it as a live activity indicator light for AI computation.

---

## Preview

> *(Add a photo or GIF of the LCD in action here)*

```
RUNNING= Executing she   <- Row 1: state + scrolling description
I=8k O=3k               <- Row 2: token usage (cycles with total)
```

---

## Features

- **Real-time status** — reflects Claude Code's current activity via its hook system
- **15 distinct states** — from `RUNNING` to `EDITING` to `PLANNING` and more
- **Scrolling ticker** — description text scrolls continuously across the display
- **Token tracking** — live input/output token counts read directly from session logs
- **Multi-session support** — automatically tracks the most recently active Claude Code instance
- **Idle dimming** — backlight turns off after 2 minutes of inactivity, restores instantly on activity
- **Zero intrusion** — Claude Code is completely unmodified; observation is external only

---

## How It Works

Claude Code exposes a hook system that fires shell scripts before/after tool use. This project uses those hooks to write session state to a shared JSON file. A background observer daemon reads that file, formats a 2-line display, and sends it to the Arduino over USB serial.

```
Claude Code (unmodified)
  └── Hook fires on every tool use
        └── Hook script writes state → /tmp/claude-lcd-sessions.json
              └── Observer daemon reads state (100ms poll)
                    └── Picks most recently active session
                          └── Formats 16×2 output
                                └── Sends over USB serial
                                      └── Arduino updates LCD
```

---

## Status Types

| LCD Label  | Trigger                        | Description               |
|------------|--------------------------------|---------------------------|
| `IDLE`     | Claude finishes responding     | Waiting for input         |
| `WORKING`  | User submits a message         | Processing message        |
| `THINKIN`  | Between tool calls             | Thinking it through       |
| `RUNNING`  | `Bash` tool                    | Executing shell command   |
| `EDITING`  | `Edit` tool                    | Modifying existing file   |
| `WRITING`  | `Write` tool                   | Creating new file         |
| `READING`  | `Read` tool                    | Reading file contents     |
| `WEBSRCH`  | `WebSearch` tool               | Searching the web         |
| `FETCH`    | `WebFetch` tool                | Fetching web content      |
| `AGENT`    | `Agent` tool                   | Delegating to subagent    |
| `PLANNIN`  | `Task*` tools                  | Planning task structure   |
| `SEARCH`   | `Grep` / `Explore` tool        | Searching codebase        |
| `SKILL`    | `Skill` tool                   | Running skill module      |
| `NOTEBK`   | `NotebookEdit` tool            | Editing notebook cells    |
| `SCHEDUL`  | `ScheduleWakeup` tool          | Scheduling a task         |

---

## Hardware

| Component | Details |
|---|---|
| Arduino Uno | Or any compatible board |
| 16×2 LCD with I2C backpack | HD44780-compatible, PCF8574 I2C module |
| USB cable | For serial communication + power |

### Wiring (I2C — only 4 wires)

| LCD Pin | Arduino Pin |
|---|---|
| `VCC` | `5V` |
| `GND` | `GND` |
| `SDA` | `A4` |
| `SCL` | `A5` |

---

## Installation

### 1. Clone the repo

```bash
git clone <repo-url>
cd arduino-lcd-link
```

### 2. Flash the Arduino

1. Open `arduino/lcd_status/lcd_status.ino` in Arduino IDE
2. Install the **LiquidCrystal I2C** library (by Frank de Brabander) via Library Manager
3. Select **Tools → Board → Arduino Uno** and the correct port
4. Click **Upload**

> If the display stays blank after flashing, open the `.ino` file and change `0x27` to `0x3F` on line 5, then re-upload.

### 3. Configure

Find your Arduino's serial port:
```bash
ls /dev/tty{USB,ACM}*
```

Edit `config.json`:
```json
{
  "serial_port": "/dev/ttyACM0",
  "baud_rate": 9600,
  "debounce_ms": 300,
  "observer_interval_ms": 100,
  "idle_dim_seconds": 120
}
```

### 4. Run the installer

```bash
chmod +x install.sh && ./install.sh
```

This will:
- Register Claude Code hooks in `~/.claude/settings.json`
- Install `python3-serial` via apt
- Add the observer daemon to your shell startup (`~/.bashrc` / `~/.zshrc`)
- Add your user to the `dialout` group for serial port access

> **Note:** Run `newgrp dialout` or open a new terminal after install for group changes to apply.

### 5. Start using it

Open a new terminal (so the observer daemon starts), then:

```bash
claude
```

The LCD activates the moment Claude Code uses its first tool.

---

## Display Layout

**Row 1** — State + scrolling description (16 chars total):
```
EDITING= Modifying ex   (scrolls left continuously)
```

**Row 2** — Token usage, cycles every 5 seconds:
```
I=8k O=3k               (input / output tokens)
T=11k                   (total tokens)
```

Token counts reflect `input_tokens + cache_creation_input_tokens` and `output_tokens` per session, read directly from Claude Code's session logs. Resets with each new `claude` invocation.

---

## Project Structure

```
arduino-lcd-link/
├── config.json                  # Serial port, timing, and behavior settings
├── install.sh                   # One-command setup script
│
├── hooks/                       # Scripts fired automatically by Claude Code
│   ├── state_utils.py           # Shared file I/O with locking
│   ├── pre_tool.py              # Fires before each tool → sets state
│   ├── post_tool.py             # Fires after each tool → captures tokens
│   ├── on_stop.py               # Fires when Claude stops → sets IDLE
│   └── on_prompt.py             # Fires on user message → sets WORKING
│
├── observer/                    # Background daemon
│   ├── main.py                  # Entry point and main loop
│   ├── session_manager.py       # Picks most recently active session
│   ├── state_classifier.py      # Maps tool names to state labels
│   ├── lcd_formatter.py         # Formats 16×2 output with scroll and cycling
│   ├── serial_bridge.py         # Sends data to Arduino via pyserial
│   └── token_reader.py          # Reads token counts from Claude Code JSONL logs
│
└── arduino/
    └── lcd_status/
        └── lcd_status.ino       # Arduino firmware (I2C LCD + serial protocol)
```

---

## Serial Protocol

The observer sends newline-delimited commands to the Arduino:

| Command | Effect |
|---|---|
| `L1:<text>` | Update row 1 |
| `L2:<text>` | Update row 2 (triggers LCD refresh) |
| `BL:1` | Backlight fully on |
| `BL:0` | Backlight off |

---

## Requirements

- Python 3.10+
- `python3-serial` (`sudo apt install python3-serial`)
- Claude Code CLI
- Arduino IDE (for firmware upload)

---

## License

MIT
