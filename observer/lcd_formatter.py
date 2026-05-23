import time
from state_classifier import display_label, describe

SCROLL_TICKS = 3   # ticks per scroll step (300ms at 100ms interval)
CYCLE_TICKS  = 50  # ticks per row2 cycle switch (5s at 100ms interval)
TICKER_GAP   = "    "  # space between description loops

class LCDFormatter:
    def __init__(self, debounce_ms: int = 300):
        self._debounce_s    = debounce_ms / 1000
        self._confirmed     = None
        self._pending       = None
        self._pending_since = None
        self._scroll_pos    = 0
        self._scroll_tick   = 0
        self._cycle_phase   = 0  # 0 = I+O, 1 = T
        self._cycle_tick    = 0
        self._last_lines    = None

    def update(self, session: dict) -> tuple[str, str] | None:
        state = (session.get("state") or "THINKING")[:8].ljust(8)
        now   = time.monotonic()

        if state != self._confirmed:
            if state != self._pending:
                self._pending       = state
                self._pending_since = now
            elif now - self._pending_since >= self._debounce_s:
                self._confirmed   = state
                self._scroll_pos  = 0
                self._scroll_tick = 0
                self._pending     = None

        display_state = self._confirmed or state
        self._advance_scroll(display_state)
        self._advance_cycle()

        lines = self._format(display_state, session)
        if lines == self._last_lines:
            return None
        self._last_lines = lines
        return lines

    def _advance_scroll(self, state: str):
        self._scroll_tick += 1
        if self._scroll_tick < SCROLL_TICKS:
            return
        self._scroll_tick = 0

        label    = display_label(state)
        window   = 16 - len(label) - 2
        desc     = describe(state)
        loop_len = len(desc) + len(TICKER_GAP)

        if len(desc) <= window:
            self._scroll_pos = 0
        else:
            self._scroll_pos = (self._scroll_pos + 1) % loop_len

    def _advance_cycle(self):
        self._cycle_tick += 1
        if self._cycle_tick >= CYCLE_TICKS:
            self._cycle_tick  = 0
            self._cycle_phase = 1 - self._cycle_phase

    def _format(self, state: str, session: dict) -> tuple[str, str]:
        label    = display_label(state)
        window   = 16 - len(label) - 2
        desc     = describe(state)
        loop_str = desc + TICKER_GAP
        doubled  = loop_str * 2
        pos      = self._scroll_pos % len(loop_str)
        view     = doubled[pos: pos + window]
        row1     = f"{label}= {view}"

        i    = session.get("tokens_in",  0)
        o    = session.get("tokens_out", 0)
        row2 = self._row2(i, o).ljust(16)[:16]

        return row1, row2

    def _row2(self, i: int, o: int) -> str:
        t = i + o
        if self._cycle_phase == 0:
            return f"I={self._fmt(i)} O={self._fmt(o)}"
        return f"T={self._fmt(t)}"

    def _fmt(self, n: int) -> str:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        if n >= 1_000:
            return f"{round(n / 1000)}k"
        return str(n)
