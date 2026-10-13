#!/usr/bin/env python3
"""PreToolUse hook for Edit, Write, MultiEdit and NotebookEdit.

Enforces the file rules that the instructions used to rely on the model to
remember. A denied call is reported back to Claude with the reason, so it
can choose a permitted route.

Rules, in order:

1. ``baseline/`` is read-only once ``Onboarded`` is true (the snapshot is
   taken during onboarding, while it is still false).
2. ``.claude/hooks/`` and ``.claude/settings.json`` are not editable by
   Claude (the guard cannot be edited by the thing it guards).
3. In ``plans/``:
   a. (planning session) only plans/ (any file, including CURRENT_PLAN) and
      .claude/CLAUDE.md may change,
      and status may not become in-progress; implementation needs /clear.
   b. An existing plan file is never overwritten whole (``Write``); use
      ``Edit`` so history is preserved. Template placeholders (files that
      still contain ``YYYY-MM-DD HH:MM:SS``) may be overwritten once.
   c. A step plan whose status is ``completed`` or ``rolled-back`` is frozen,
      except for an edit that sets its status to ``rolled-back``.
   d. The ``## Approved Plan`` section is append-only: an edit inside it is
      allowed only when it adds text at the end of the file and keeps the
      existing text intact.

Everything else falls through to the normal permission flow.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    PLACEHOLDER,
    allow,
    deny,
    onboarded,
    plan_status,
    read_input,
    read_text,
    relative_path,
    session_kind,
)

EVENT = "PreToolUse"
APPROVED_HEADING = re.compile(r"^## Approved Plan\s*$", re.MULTILINE)


def main() -> None:
    data = read_input()
    tool = data.get("tool_name", "")
    args = data.get("tool_input", {}) or {}
    raw_path = args.get("file_path") or args.get("notebook_path")
    rel = relative_path(raw_path)
    if rel is None:
        allow()

    # Rule 1: baseline is read-only.
    if rel == "baseline" or rel.startswith("baseline/"):
        if not rel.endswith("README.md") and onboarded() is not False:
            deny(EVENT, f"{rel}: baseline/ is a read-only snapshot. "
                 "Modified copies belong in src/.")

    # Rule 2: the guard protects itself.
    if rel.startswith(".claude/hooks/") or rel == ".claude/settings.json":
        deny(EVENT, f"{rel}: hooks and .claude/settings.json are maintained "
             "by the user, not by Claude. Suggest the change instead. (Other "
             "files under .claude/ — skills, agents, CLAUDE.md, AGENTS.md — "
             "are editable.)")

    # Rule 3: a planning session only plans. Each step is implemented in a
    # fresh context, so a session that started with the previous step
    # completed may write plans/ and .claude/CLAUDE.md, nothing else.
    kind = session_kind(data.get("session_id"))
    is_plan_file = rel.startswith("plans/") and rel.endswith(".md")
    in_plans = rel.startswith("plans/")  # includes plans/CURRENT_PLAN
    if kind == "planning" and not (in_plans or rel == ".claude/CLAUDE.md"):
        deny(EVENT, f"{rel}: this is a planning session (it started with the "
             "previous step completed, or a new step plan was recorded in it). "
             "It records the next step plan and stops. Suggest /clear; the "
             "user runs /next-step in a fresh context to implement.")

    # Rule 4: plan files.
    if not is_plan_file:
        allow()

    existing = read_text(rel)
    if existing is None:
        allow()  # creating a new plan file is fine

    # 3a: no whole-file overwrite of a populated plan.
    if tool == "Write" and PLACEHOLDER not in existing:
        deny(EVENT, f"{rel} already exists and is populated. Plans are "
             "append-only history: use Edit to change specific sections.")

    status = plan_status(existing)
    edits = args.get("edits") or [args]  # MultiEdit carries a list
    for edit in edits:
        old = edit.get("old_string") or ""
        new = edit.get("new_string") or ""

        # 4a: a planning session never starts implementation.
        if kind == "planning" and "in-progress" in new and "Status" in old:
            deny(EVENT, "Status -> in-progress is the Implementer's first act and "
                 "belongs in a fresh context. Leave the plan `planned`, suggest "
                 "/clear, and the user runs /next-step.")

        # 4b: frozen plans.
        if status in ("completed", "rolled-back") and tool != "Write":
            sets_rolled_back = "rolled-back" in new and "Status" in old
            if not sets_rolled_back:
                deny(EVENT, f"{rel} has status `{status}` and is frozen. "
                     "Only a rollback (Status -> rolled-back) may touch it. "
                     "Record new work in a new step plan.")

        # 4c: Approved Plan section is append-only.
        m = APPROVED_HEADING.search(existing)
        idx = m.start() if m else -1
        if idx >= 0 and old:
            pos = existing.find(old)
            if pos >= idx:
                is_append = (
                    new.startswith(old)
                    and existing.rstrip().endswith(old.rstrip())
                )
                if not is_append:
                    deny(EVENT, f"{rel}: the Approved Plan section is "
                         "append-only. Add a `### Plan Revision — <timestamp>` "
                         "sub-section at the end of the file instead of "
                         "editing approved text.")
    allow()


if __name__ == "__main__":
    main()
