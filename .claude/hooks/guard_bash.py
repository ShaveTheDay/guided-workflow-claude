#!/usr/bin/env python3
"""PreToolUse hook for Bash: block git writes and other denied commands.

The permission deny list in ``~/.claude/settings.json`` is the first line of
defence, but it matches the start of a command string. This hook looks at
every command in a chain (``a && b``, ``a; b``, ``a | b``, ``$(...)``) and
at git's global options (``git -C . commit``, ``git --no-pager push``), so
the git policy holds however the command is written.

Blocked:
- any git subcommand that writes (commit, push, add, merge, ...)
- pip / pip3 (the project uses uv)
- sudo, rm -rf, curl, wget, chmod, chown
- in a planning session (started with the previous step completed): any
  shell write at all — redirection, sed -i, tee, cp, mv, rm, touch, mkdir,
  interpreters — except ``uv run`` (tests and lint are reads)
- shell-side writes to protected paths (plans/, baseline/, .claude/hooks/,
  .claude/settings.json): redirection, sed -i, tee, cp, mv, rm, or an
  interpreter (python, perl, ruby, node) in a command that names them. Those
  files are edited with the Edit tool, where guard_edits.py checks them.

Allowed through to the normal permission flow: everything else, including
read-only git (status, log, diff, show, branch --list).
"""

from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import allow, deny, onboarded, read_input, session_kind  # noqa: E402

EVENT = "PreToolUse"

GIT_WRITE = {
    "add", "commit", "push", "pull", "fetch", "tag", "checkout", "switch",
    "merge", "rebase", "reset", "restore", "stash", "rm", "mv", "clean",
    "cherry-pick", "revert", "am", "apply", "init", "clone", "worktree",
    "submodule", "notes", "filter-branch", "gc", "prune", "reflog",
    "remote", "config",
}
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
GIT_BRANCH_WRITE_FLAGS = {"-d", "-D", "-m", "-M", "-c", "-C", "--delete",
                          "--move", "--copy", "-f", "--force", "-u",
                          "--set-upstream-to", "--unset-upstream"}

SPLIT_RE = re.compile(r"\|\||&&|;|\||\n|\$\(|`")
PROTECTED = re.compile(r"(?:^|[\s'\"/=])(?:plans/|baseline/|\.claude/hooks/|\.claude/settings\.json)")
WRITERS = {"sed", "tee", "cp", "mv", "rm", "truncate", "dd", "python", "python3",
           "perl", "ruby", "node", "uv"}


def git_verdict(tokens: list[str]) -> str | None:
    """Return a reason if this git command writes, else None."""
    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok in GIT_OPTS_WITH_VALUE:
            i += 2
            continue
        if tok.startswith("-"):
            i += 1
            continue
        break
    if i >= len(tokens):
        return None
    sub = tokens[i]
    if sub in GIT_WRITE:
        return f"`git {sub}` writes to the repository"
    if sub == "branch":
        rest = tokens[i + 1:]
        if any(t in GIT_BRANCH_WRITE_FLAGS for t in rest):
            return "`git branch` with a write flag"
        if rest and not any(t.startswith("-") for t in rest):
            return "`git branch <name>` creates a branch"
    return None


def main() -> None:
    data = read_input()
    if data.get("tool_name") != "Bash":
        allow()
    command = (data.get("tool_input") or {}).get("command", "") or ""

    # A planning session reads and plans; it does not change the tree.
    if session_kind(data.get("session_id")) == "planning":
        if re.search(r"(?<![<>])>{1,2}(?!&)", command):
            deny(EVENT, "This is a planning session (previous step completed): "
                 "no shell writes. Record the step plan, then suggest /clear; "
                 "the user runs /next-step in a fresh context to implement.")
        for seg in SPLIT_RE.split(command):
            try:
                toks = shlex.split(seg)
            except ValueError:
                toks = seg.split()
            while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
                toks = toks[1:]
            if not toks:
                continue
            h = Path(toks[0]).name
            if h in WRITERS | {"touch", "mkdir", "rmdir", "ln", "chmod"} and not (
                h == "sed" and "-i" not in " ".join(toks)
            ) and not (h == "uv" and toks[1:2] == ["run"]):
                deny(EVENT, f"`{h}` is not permitted in a planning session. This "
                     "session records the next step plan and stops; implementation "
                     "starts after /clear and /next-step.")

    # Before onboarding is complete, the Discoverer may populate baseline/.
    snapshot_phase = onboarded() is False
    if PROTECTED.search(command) and not (
        snapshot_phase and "baseline/" in command
        and not re.search(r"plans/|\.claude/", command)
    ):
        if re.search(r"(?<![<>])>{1,2}(?!&)", command):
            deny(EVENT, "Shell redirection into plans/, baseline/ or .claude/hooks "
                 "is not permitted. Edit those files with the Edit tool so the "
                 "project hooks can check the change.")
        for seg in SPLIT_RE.split(command):
            try:
                toks = shlex.split(seg)
            except ValueError:
                toks = seg.split()
            while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
                toks = toks[1:]
            if toks and Path(toks[0]).name in WRITERS:
                if Path(toks[0]).name == "sed" and "-i" not in " ".join(toks):
                    continue
                if Path(toks[0]).name == "cp" and not PROTECTED.search(" ".join(toks[-1:])):
                    continue  # copying OUT of plans/ is a read
                deny(EVENT, f"`{Path(toks[0]).name}` on plans/, baseline/ or .claude/hooks "
                     "is not permitted from the shell. Use the Edit tool so the "
                     "project hooks can check the change.")

    for segment in SPLIT_RE.split(command):
        segment = segment.strip()
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        if not tokens:
            continue
        # skip leading env assignments: FOO=bar git commit
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens = tokens[1:]
        tokens = [t.strip(')`') for t in tokens]
        tokens = [t for t in tokens if t]
        if not tokens:
            continue
        head = Path(tokens[0]).name

        if head == "git":
            reason = git_verdict(tokens)
            if reason:
                deny(EVENT, f"Git policy: {reason}. Claude never runs git "
                     "write commands; suggest the command and message for "
                     "the user to run.")
        elif head in ("pip", "pip3"):
            deny(EVENT, "Use `uv add <package>` / `uv sync`; pip is not used "
                 "in this project.")
        elif head == "sudo":
            deny(EVENT, "sudo is not permitted.")
        elif head == "rm" and any(
            t.startswith("-") and "r" in t and "f" in t for t in tokens[1:]
        ):
            deny(EVENT, "`rm -rf` is not permitted. Delete specific files "
                 "and explain first.")
        elif head in ("curl", "wget", "chmod", "chown"):
            deny(EVENT, f"`{head}` is not permitted by the project policy.")
    allow()


if __name__ == "__main__":
    main()
