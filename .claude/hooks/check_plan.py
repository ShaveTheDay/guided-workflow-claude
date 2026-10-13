#!/usr/bin/env python3
"""PostToolUse hook for Edit and Write on ``plans/*.md``: audit checks.

Runs after a plan file changes and reports problems back to Claude as
context it must act on. It never blocks (the write has already happened);
it makes the model fix what it got wrong while the step is still open.

Checks:
- Status is one of the five allowed values.
- ``Last updated`` is not the placeholder and parses as
  ``YYYY-MM-DD HH:MM:SS``; date-only values anywhere are flagged.
- ``Last updated`` is within 15 minutes of now (it was just changed).
- ``plans/CURRENT_PLAN`` names a file that exists.
- The ``## Approved Plan`` section is present in step plans and is last.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    PLACEHOLDER,
    STATUSES,
    TIMESTAMP_FORMAT,
    TIMESTAMP_RE,
    add_context,
    allow,
    current_plan,
    plan_status,
    read_input,
    read_text,
    relative_path,
)

EVENT = "PostToolUse"
TEMPLATE_SECTIONS = (
    "Meta", "Changes from Previous Plan", "Plan Revision History", "Objective",
    "Project Goal", "Discovery Summary", "High-Level Project Plan",
    "User Inputs & Decisions", "Model Reasoning & Decisions", "Blockers & Unknowns",
    "Tasks — Prioritised", "Tasks for Step 001", "Implementation Notes", "Code Plan",
    "Verification Criteria", "Session State (Handoff Context)",
)
# A timestamp field: a Meta/notes label, a Session State marker, a revision or
# approval heading, or the last cell of a decision/reasoning table row.
FIELD_DATE = re.compile(
    r"(?:\|\s*(?:Created|Last updated)\s*\|\s*"
    r"|###\s*Last Updated:\s*_?\[?"
    r"|(?:Session Timestamp|Snapshot timestamp|Timestamp):\*{0,2}\s*_?"
    r"|###\s*(?:Plan Revision|Approved)\s*—\s*)"
    r"(?P<value>\d{4}-\d{2}-\d{2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?)"
)


def main() -> None:
    data = read_input()
    rel = relative_path((data.get("tool_input") or {}).get("file_path"))
    if not rel or not (rel.startswith("plans/") and rel.endswith(".md")):
        allow()
    text = read_text(rel)
    if text is None:
        allow()

    problems: list[str] = []
    is_step = Path(rel).name.startswith("step-")

    if is_step:
        status = plan_status(text)
        if status not in STATUSES:
            problems.append(f"Status `{status}` is not one of {', '.join(STATUSES)}.")
        if not re.search(r"^## Approved Plan\s*$", text, re.MULTILINE):
            problems.append("The `## Approved Plan` section is missing.")
        elif status and not re.sub(
            r"<!--.*?-->", "", re.split(r"^## Approved Plan\s*$", text, flags=re.M)[-1], flags=re.S
        ).strip():
            problems.append("The `## Approved Plan` section is empty; paste the "
                            "approved plan there now, before any other change.")
        # The pasted plan may contain its own "## " headings, so "last section"
        # means: no template section heading appears after Approved Plan.
        parts = re.split(r"^## Approved Plan\s*$", text, flags=re.M)
        if len(parts) > 1:
            tail = parts[-1]
            stray = [h for h in TEMPLATE_SECTIONS
                     if re.search(rf"^## {re.escape(h)}\s*$", tail, re.M)]
            if stray:
                problems.append("`## Approved Plan` must be the last template section; "
                                f"found after it: {', '.join(stray)}.")

        meta = re.search(r"\|\s*Last updated\s*\|\s*([^|]+)\|", text)
        if meta:
            value = meta.group(1).strip().strip("`")
            if value == PLACEHOLDER:
                problems.append("`Last updated` still holds the placeholder.")
            else:
                try:
                    when = datetime.strptime(value, TIMESTAMP_FORMAT)
                    age = (datetime.now() - when).total_seconds() / 60
                    if age > 15:
                        problems.append(f"`Last updated` is {age:.0f} minutes old; refresh it "
                                        "to the current system time for this change.")
                    elif age < -5:
                        problems.append("`Last updated` is in the future; use the system time.")
                except ValueError:
                    problems.append(f"`Last updated` value `{value}` is not YYYY-MM-DD HH:MM:SS.")

    # Date-only values in timestamp FIELDS only (a date inside prose or a
    # filename such as "2026-10-20 Holiday.md" is not a timestamp).
    for m in FIELD_DATE.finditer(text):
        s = m.group("value").strip()
        if s and s != PLACEHOLDER and not TIMESTAMP_RE.fullmatch(s):
            problems.append(f"`{s}` in a timestamp field is not YYYY-MM-DD HH:MM:SS.")
            break

    active = current_plan()
    if active and read_text(f"plans/{active}") is None:
        problems.append(f"plans/CURRENT_PLAN names `{active}`, which does not exist.")

    if problems:
        add_context(EVENT, "[Plan audit — fix these in the same turn]\n- " + "\n- ".join(problems))
    allow()


if __name__ == "__main__":
    main()
