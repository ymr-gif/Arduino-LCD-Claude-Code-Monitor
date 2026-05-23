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

# natural-length labels (no padding) used in row 1 display
STATE_DISPLAY_LABELS = {
    "IDLE    ": "IDLE",
    "WORKING ": "WORKING",
    "THINKING": "THINKIN",
    "RUNNING ": "RUNNING",
    "EDITING ": "EDITING",
    "WRITING ": "WRITING",
    "READING ": "READING",
    "WEBSRCH ": "WEBSRCH",
    "FETCHING": "FETCH",
    "AGENT   ": "AGENT",
    "PLANNING": "PLANNIN",
    "SEARCH  ": "SEARCH",
    "SKILL   ": "SKILL",
    "NOTEBOOK": "NOTEBK",
    "SCHEDULN": "SCHEDUL",
}

STATE_DESCRIPTIONS = {
    "IDLE    ": "Waiting for input",
    "WORKING ": "Processing message",
    "THINKING": "Thinking it through",
    "RUNNING ": "Executing shell command",
    "EDITING ": "Modifying existing file",
    "WRITING ": "Creating new file",
    "READING ": "Reading file contents",
    "WEBSRCH ": "Searching the web",
    "FETCHING": "Fetching web content",
    "AGENT   ": "Delegating to subagent",
    "PLANNING": "Planning task structure",
    "SEARCH  ": "Searching codebase",
    "SKILL   ": "Running skill module",
    "NOTEBOOK": "Editing notebook cells",
    "SCHEDULN": "Scheduling a task",
}

DEFAULT_LABEL       = "WORKING"
DEFAULT_DESCRIPTION = "Working on it"

def classify(tool_name: str) -> str:
    return TOOL_STATES.get(tool_name, "WORKING ")

def display_label(state: str) -> str:
    return STATE_DISPLAY_LABELS.get(state, DEFAULT_LABEL)

def describe(state: str) -> str:
    return STATE_DESCRIPTIONS.get(state, DEFAULT_DESCRIPTION)
