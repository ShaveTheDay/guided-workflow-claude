#!/usr/bin/env python3
"""UserPromptSubmit hook: inject the current system time on every turn.

The audit rules need every timestamp to come from the system clock. Rather
than trusting the model to run ``date`` before each one, the harness hands
it the time at the start of each turn. If a turn runs long, the
``check_plan`` hook flags stale timestamps after the write.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import add_context, allow, now, read_input, read_text  # noqa: E402

EVENT = "UserPromptSubmit"


def main() -> None:
    read_input()
    if read_text("plans/CURRENT_PLAN") is None:
        allow()
    add_context(EVENT, f"System time at the start of this turn: {now()}. "
                "Use it for any timestamp you write in this turn. If the turn "
                "has run for more than 10 minutes, run `date '+%Y-%m-%d %H:%M:%S'` "
                "for a fresh value.")


if __name__ == "__main__":
    main()
