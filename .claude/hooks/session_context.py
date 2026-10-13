#!/usr/bin/env python3
"""SessionStart hook: hand Claude the project state before the first prompt.

Runs on startup, /clear and resume. Injects a short block of facts that the
model otherwise has to discover with tool calls, and that weaker models
sometimes skip: the current time, whether the project is onboarded, the
active step plan and its status, which role that implies, and the git
state. The routing line tells Claude which skill to run.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    add_context,
    allow,
    current_plan,
    now,
    onboarded,
    plan_status,
    read_input,
    read_text,
    record_session,
    run,
    session_kind_for,
)

EVENT = "SessionStart"

ROLE_FOR_STATUS = {
    "completed": "Planner — plan the next step in plan mode",
    "planned": "Implementer — start the recorded plan",
    "in-progress": "Implementer — resume from Session State",
    "implemented": "Reviewer — run the reviewer subagent, record findings",
    "rolled-back": "Planner — read the rollback notes, then plan",
}


def main() -> None:
    data = read_input()
    if read_text("plans/CURRENT_PLAN") is None or read_text(".claude/AGENTS.md") is None:
        allow()  # not a step-based project; stay silent

    lines = ["[Step-based project — state injected by SessionStart hook]",
             f"System time: {now()} (use this for timestamps written now)"]

    flag = onboarded()
    plan = current_plan()
    status = None
    if plan:
        text = read_text(f"plans/{plan}")
        status = plan_status(text) if text else None

    kind = session_kind_for(status, flag)
    record_session(str(data.get("session_id") or "unknown"), kind, plan)

    lines.append(f"Onboarded: {flag}")
    lines.append(f"Active plan: plans/{plan or '(missing)'}  status: {status or '(unknown)'}")
    lines.append(f"Session kind: {kind}" + (
        " — this session plans the next step and records it. It does NOT implement. "
        "After the step plan is written, suggest /clear; the user runs /next-step in a "
        "fresh context to implement. Code edits are blocked in this session."
        if kind == "planning" else ""))

    if flag is False:
        lines.append("Route: run /start (first session; nothing else until onboarding is done).")
    elif plan == "step-000-initial.md" and status != "completed":
        lines.append("Route: onboarding did not finish cleanly. Tell the user, then act as Planner.")
    elif status in ROLE_FOR_STATUS:
        lines.append(f"Route: run /next-step. Role: {ROLE_FOR_STATUS[status]}.")
    else:
        lines.append("Route: run /next-step and ask the user for direction if the status is unreadable.")

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch:
        changed = run(["git", "status", "--short"])
        n = len(changed.splitlines()) if changed else 0
        lines.append(f"Git: branch {branch}, {n} changed file(s) (git status --short)")
    else:
        lines.append("Git: not a repository (or git unavailable)")

    add_context(EVENT, "\n".join(lines))


if __name__ == "__main__":
    main()
