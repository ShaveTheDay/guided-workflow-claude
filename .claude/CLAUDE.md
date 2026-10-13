@AGENTS.md

# Project CLAUDE.md

> Project-specific instructions for Claude Code. Overrides global defaults where
> they conflict. Updated during discovery and as the project evolves. The line
> above imports `.claude/AGENTS.md` (the role definitions).

---

## Session Start

A `SessionStart` hook injects the project state (time, `Onboarded`, active plan,
status, role, git state) and a **Route** line at the start of every session.
Follow the Route line:

- `Onboarded: false` → invoke `/start`.
- `Onboarded: true` → invoke `/next-step`.

The reliable launch is `claude "/start"` or `claude "/next-step"`. Sessions
start in **plan mode** (read-only) — set in `.claude/settings.json`.

---

## Project Overview

- **Onboarded:** `false`  <!-- Set to true by /start after onboarding files are written. Do not edit manually. -->
- **Project name:** _[set during discovery]_
- **Goal:** _[one-line summary — set during discovery]_
- **Goal file:** `plans/000-goal.md`
- **Discovery notes:** `plans/000-discovery.md`

---

## Environment Configuration

<!-- Defaults inherited from global CLAUDE.md. Override only what differs. -->

| Setting              | Value                          | Differs from default? |
|----------------------|--------------------------------|-----------------------|
| Development OS       | WSL2 (Ubuntu)                  | No                    |
| Target OS            | Windows                        | No                    |
| Language             | Python 3.11+                   | No                    |
| Environment          | `.venv/` managed by `uv`       | No                    |
| Package manager      | `uv` exclusively               | No                    |
| Dependency file      | `pyproject.toml`               | No                    |
| Lockfile             | `uv.lock`                      | No                    |
| Test command         | `uv run pytest`                | No                    |
| Lint command         | `uv run ruff check src tests`  | No                    |
| Key dependencies     | _[set during discovery]_       | —                     |

> If discovery changes a default, update this table and note the reasoning in
> `plans/000-discovery.md`. For a non-Python project, set Language, Package
> manager, Dependency file, Lockfile, Test command and Lint command here; the
> Implementer and the reviewer agent read the two command rows.

---

## Project Structure

```
project-root/
├── README.md              ← Human-facing intro and getting-started guide.
├── CHANGES.md             ← What changed from the previous template version, and why.
│
├── .claude/
│   ├── CLAUDE.md          ← You are here. Project-level instructions.
│   ├── AGENTS.md          ← Role definitions (imported above).
│   ├── settings.json      ← Plan mode by default; hook registrations.
│   ├── hooks/             ← Python hooks that enforce the rules (user-maintained).
│   ├── agents/reviewer.md ← The Reviewer subagent (read-only, fresh context).
│   └── skills/            ← /start, /next-step, /discovery, /grill-me.
│
├── pyproject.toml, uv.lock, .gitignore
│
├── plans/                 ← The project's authoritative records.
│   ├── CURRENT_PLAN       ← Filename of the active step plan.
│   ├── PLAN_TEMPLATE.md   ← Template for every step plan.
│   ├── 000-goal.md        ← Initial project goal (input).
│   ├── 000-discovery.md   ← Discovery session outputs.
│   ├── step-000-initial.md← Initial plan, produced by onboarding.
│   └── step-NNN-*.md      ← One file per step (append-only).
│
├── docs/                  ← User-supplied reference material, data, outputs.
├── baseline/              ← Optional. Read-only snapshot of original code (enforced).
├── samples/               ← Optional. Code style references.
├── src/, tests/, scripts/ ← Your code.
```

---

## What the Hooks Enforce

You will see a denied tool call with a reason when a rule is hit. Take the
permitted route instead; do not try another way around. The rules are exactly
those listed here — do not infer wider ones (for example, `.claude/skills/` is
editable).

| Hook | When | Rule |
|------|------|------|
| `guard_edits.py` | before Edit/Write | `baseline/` read-only once onboarded; `.claude/hooks/` and `.claude/settings.json` not editable (everything else under `.claude/` is); populated plans never overwritten whole; `completed`/`rolled-back` plans frozen (except a rollback); `## Approved Plan` append-only |
| `guard_bash.py` | before Bash | git write commands, pip, sudo, `rm -rf`, curl, wget, chmod, chown — anywhere in a command chain; any shell-side write to `plans/`, `baseline/` or the hooks (use the Edit tool for those) |
| `session_context.py` | session start | injects time, state and the Route line; records the session kind (`onboarding`, `planning`, `implementing`) in `.claude/session-state.json` |
| `guard_edits.py` + `guard_bash.py` | planning session | a session that started with the previous step `completed` may change only files under `plans/` (including `CURRENT_PLAN`) and `.claude/CLAUDE.md`, may not set a status to `in-progress`, and may not write through the shell (`uv run` and the project's test/lint commands allowed). Implementation needs `/clear` then `/next-step`. |
| `prompt_time.py` | every prompt | injects the system time for timestamps |
| `check_plan.py` | after a plan edit | reports bad status values, placeholders, malformed or stale timestamps, missing Approved Plan section |

---

## Git Policy

See the global `~/.claude/CLAUDE.md` § Git Policy. No git write commands;
suggest commits with a message for the user to run.

---

## Project-Specific Rules

<!-- Add rules here as the project evolves. Examples: -->
<!-- - All file paths must use pathlib, not os.path -->
<!-- - No external API calls without a mock in tests -->

_[none yet — add as discovery and development surface them]_

---

## Rollback Procedure

1. Identify the target step plan in `plans/` (for example `step-003-feature-x.md`).
2. Set every later step plan's status to `rolled-back` (the only edit the hook
   allows on a frozen plan).
3. Update `plans/CURRENT_PLAN` to the target step plan.
4. Use `git diff` / `git log` to identify code to revert; the user runs git.
5. Create a new step plan (next number) documenting the rollback and why.

Rollback never deletes plan files.

---

## Post-Step Workflow

After the Reviewer passes a step, complete these **before** setting status
`completed` (a completed plan is frozen):

### Pre-Clear Checklist

- [ ] **Session State** finalised (completed items, files modified, environment state).
- [ ] **Code Plan** reflects what was actually done (deviations noted).
- [ ] The reviewer subagent's report is recorded in the step plan.
- [ ] `plans/CURRENT_PLAN` points to this step plan.
- [ ] New blockers or unknowns recorded.
- [ ] `Last updated` refreshed.
- [ ] **Last:** status set to `completed`.

### Context Transition

Suggest `/clear`. The user then runs `/next-step`. If the session is not in
plan mode after `/clear`, the user presses Shift+Tab until the status bar shows
plan mode, or relaunches with `claude "/next-step"`.
