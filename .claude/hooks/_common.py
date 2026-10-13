"""Shared helpers for the project's Claude Code hooks.

Every hook reads one JSON object from stdin (the hook input) and may write
one JSON object to stdout (the hook output). These helpers keep that
plumbing in one place so each hook script is just its rule.

Hooks run with the system ``python3``, outside the project's ``.venv``, and
use only the standard library.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMESTAMP_RE = re.compile(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b")
PLACEHOLDER = "YYYY-MM-DD HH:MM:SS"
STATUSES = ("planned", "in-progress", "implemented", "completed", "rolled-back")


def read_input() -> dict:
    """Return the hook input JSON from stdin, or an empty dict."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def project_dir() -> Path:
    """Return the project root (CLAUDE_PROJECT_DIR, else the working dir)."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def relative_path(raw: str | None) -> str | None:
    """Return ``raw`` relative to the project root, or None if outside it."""
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = project_dir() / path
    try:
        return path.resolve().relative_to(project_dir()).as_posix()
    except ValueError:
        return None


def now() -> str:
    """Return the current local time as ``YYYY-MM-DD HH:MM:SS``."""
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def deny(event: str, reason: str) -> None:
    """Block the tool call with ``reason`` and exit."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(out))
    sys.exit(0)


def add_context(event: str, text: str) -> None:
    """Inject ``text`` into Claude's context for this event and exit."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }
    }
    print(json.dumps(out))
    sys.exit(0)


def allow() -> None:
    """Make no decision; the normal permission flow applies."""
    sys.exit(0)


def run(cmd: list[str]) -> str:
    """Run a read-only command and return its stdout, or '' on failure."""
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10, cwd=project_dir()
        )
        return res.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def read_text(rel: str) -> str | None:
    """Return the text of a project file, or None if it does not exist."""
    path = project_dir() / rel
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def current_plan() -> str | None:
    """Return the active step plan filename from ``plans/CURRENT_PLAN``."""
    text = read_text("plans/CURRENT_PLAN")
    if not text:
        return None
    return text.strip().splitlines()[0].strip() or None


def plan_status(text: str) -> str | None:
    """Return the Status value from a step plan's Meta table."""
    m = re.search(r"^\|\s*Status\s*\|\s*`?([a-z-]+)`?", text, re.MULTILINE)
    return m.group(1) if m else None


def onboarded() -> bool | None:
    """Return the Onboarded flag from ``.claude/CLAUDE.md``."""
    text = read_text(".claude/CLAUDE.md")
    if text is None:
        return None
    m = re.search(r"\*\*Onboarded:\*\*\s*`?(true|false)`?", text)
    return None if not m else m.group(1) == "true"


SESSION_STATE = ".claude/session-state.json"


def session_kind_for(status: str | None, is_onboarded: bool | None) -> str:
    """Classify a session by the project state when it started.

    - ``onboarding``: /start has not finished; nothing is restricted.
    - ``planning``: the active plan is completed or rolled back, so this
      session exists to plan the next step. Code edits are denied.
    - ``implementing``: a plan is planned/in-progress/implemented, so this
      session implements and reviews it.
    """
    if is_onboarded is False:
        return "onboarding"
    if status in ("completed", "rolled-back", None):
        return "planning"
    return "implementing"


def record_session(session_id: str, kind: str, plan: str | None = None) -> None:
    """Remember ``kind`` and the active plan for ``session_id``."""
    path = project_dir() / SESSION_STATE
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except (OSError, ValueError):
        data = {}
    data = {k: v for k, v in list(data.items())[-20:]}  # keep it small
    data[session_id] = {"kind": kind, "plan": plan, "started": now()}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass


def session_entry(session_id: str | None) -> dict:
    """Return the recorded entry for this session, or {} if unknown."""
    if not session_id:
        return {}
    path = project_dir() / SESSION_STATE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    entry = data.get(session_id)
    return entry if isinstance(entry, dict) else {}


def session_kind(session_id: str | None) -> str | None:
    """Return the effective kind for this session, or None if unknown.

    A session that started as ``implementing`` is bound to the plan that was
    active then. If ``plans/CURRENT_PLAN`` now names a different file, a new
    step was recorded in this session, and it becomes ``planning``: the new
    step is implemented after /clear, in a fresh context.
    """
    entry = session_entry(session_id)
    kind = entry.get("kind")
    if kind == "implementing" and entry.get("plan") and current_plan() != entry.get("plan"):
        return "planning"
    return kind
