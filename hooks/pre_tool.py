#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from state_utils import load_config, update_session

TOOL_STATES = {
    "Bash":            "RUNNING ",
    "Edit":            "EDITING ",
    "Write":           "WRITING ",
    "Read":            "READING ",
    "WebSearch":       "WEBSRCH ",
    "WebFetch":        "FETCHING",
    "Agent":           "AGENT   ",
    "TaskCreate":      "PLANNING",
    "TaskUpdate":      "PLANNING",
    "TaskGet":         "PLANNING",
    "TaskList":        "PLANNING",
    "TaskStop":        "PLANNING",
    "Grep":            "SEARCH  ",
    "Skill":           "SKILL   ",
    "NotebookEdit":    "NOTEBOOK",
    "ScheduleWakeup":  "SCHEDULN",
    "Explore":         "SEARCH  ",
}

def main():
    event = json.loads(sys.stdin.read())
    session_id = event.get("session_id", "unknown")
    tool_name = event.get("tool_name", "")
    state = TOOL_STATES.get(tool_name, "WORKING ")
    cfg = load_config()
    update_session(cfg["state_file"], session_id, state=state)

if __name__ == "__main__":
    main()
