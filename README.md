# Step-Based Project Template

> A folder structure and guided workflow for iterative Python development
> in Claude Code. Version 20: rules that must always hold are enforced by
> hooks and permissions, not by instruction text, and each step is planned
> and built in separate context windows. See `CHANGES.md`.

The template has two goals:

1. **Context management.** Work is split into small steps. Each step runs in a
   fresh context window, so the model stays focused on one step at a time.
2. **Auditability.** Every step leaves a complete, timestamped plan record in
   this project's `plans/` folder, committed with the code.

---

## First-Time Setup (once per machine)

1. Copy `CLAUDE.global.md` to `~/.claude/CLAUDE.md`.
2. Copy `settings.global.json` to `~/.claude/settings.json`.
3. Make sure `python3` is on the path in WSL2 (the hooks use it; no packages
   needed) and [uv](https://docs.astral.sh/uv/) is installed.

The project's own files refer to the two global files by their installed paths.
The global files give Claude its cross-project defaults; they switch on the step
workflow only in projects that contain `plans/CURRENT_PLAN` and `.claude/AGENTS.md`.

---

## Getting Started

Open this folder in VS Code and launch Claude Code from the **integrated terminal**.

**First session on a new project:**

```bash
claude "/start"
```

**Every session after that:**

```bash
claude "/next-step"
```

Launching with the command as the first prompt is the reliable way to start. A
plain `claude` opens a session that waits for you; a session-start hook then
tells Claude the project state and which command to run, so typing `/start` or
`/next-step` works too.

Sessions start in **plan mode** (set in `.claude/settings.json`). Plan mode is
read-only: Claude can read and discuss, but it can't change files until you
approve a plan. Shift+Tab cycles modes.

> The Claude Code **VS Code extension panel** does not read the project's starting
> mode. Use the integrated terminal, or switch to plan mode manually in the panel.

**Questions appear as menus.** When Claude needs a decision, it shows a
multiple-choice form with its recommended answer first.

---

## The Step Workflow

```
claude "/start"      plan mode: welcome → goal → discovery
                     approve → Claude writes goal, discovery notes, step-000
                     /clear
                        │
                        ▼
claude "/next-step"  ┌──────────────────────────────────────────────────┐
                     │ 1. Plan      plan mode, discuss with Claude       │
                     │ 2. Approve   you approve; plan mode exits         │
                     │ 3. Record    Claude writes plans/step-NNN with    │
                     │              the approved plan pasted in          │
                     │ 4. Stop      /clear, then /next-step              │
                     │ 5. Implement fresh session; Session State kept    │
                     │ 6. Review    independent reviewer subagent        │
                     │ 7. Clear     /clear, then /next-step              │
                     └──────────────────────────────────────────────────┘
```

Each step's plan has a status: `planned` → `in-progress` → `implemented` →
`completed`. `/next-step` reads the status and picks up at the right point.
Planning and building never share a context window: once the plan is recorded
Claude stops, and you run `/clear` then `/next-step` to begin building.

---

## One Plan Record

Each step has exactly one record: `plans/step-NNN-<title>.md`. Immediately after
you approve a plan, Claude writes this file from `plans/PLAN_TEMPLATE.md` and
pastes the approved plan into its final **Approved Plan** section. From then on
that section is append-only, and once the step is `completed` the whole file is
frozen. Both rules are enforced by a hook, not by trust.

Mid-step changes go through plan mode again and are appended as timestamped
Plan Revisions. Plans are never deleted or overwritten.

---

## What Is Enforced, and How

| Rule | Enforced by |
|------|-------------|
| No git write commands, however they are chained or spelled | `~/.claude/settings.json` deny list **and** `.claude/hooks/guard_bash.py` |
| No pip, sudo, `rm -rf`, curl, wget, chmod, chown | same |
| `baseline/` is read-only | `.claude/hooks/guard_edits.py` |
| Populated plan files are never overwritten whole | `guard_edits.py` |
| `completed` / `rolled-back` plans are frozen (except a rollback) | `guard_edits.py` |
| The Approved Plan section is append-only | `guard_edits.py` |
| Hooks and project settings are not editable by Claude | `guard_edits.py` |
| Timestamps come from the system clock | `prompt_time.py` injects the time every turn; `check_plan.py` flags placeholders, malformed and stale values after each plan edit |
| Sessions route to `/start` or `/next-step` | `session_context.py` injects state and a Route line |
| The review is independent | `.claude/agents/reviewer.md` runs in a fresh context with no edit tools |
| Planning and building never share a context | `session_context.py` classifies each session at start (`onboarding`, `planning`, `implementing`) and records it in `.claude/session-state.json`; in a planning session `guard_edits.py` and `guard_bash.py` refuse code edits, shell writes and a status change to `in-progress`. A session that records a new step plan becomes a planning session. |
| No shell-side edits to plans, baseline or hooks | `guard_bash.py` — those files are changed with the Edit tool so `guard_edits.py` can check them |

When a hook blocks something, Claude sees the reason and takes the permitted
route. The hooks are plain Python 3 with no dependencies; you maintain them,
Claude cannot edit them. Everything else under `.claude/` (skills, agents,
instruction files) Claude can edit.

---

## What's in This Template

| Path                     | Purpose                                                      |
|--------------------------|--------------------------------------------------------------|
| `.claude/CLAUDE.md`      | Project instructions for Claude. Imports `AGENTS.md`.        |
| `.claude/AGENTS.md`      | The four roles: Discoverer, Planner, Implementer, Reviewer.  |
| `.claude/settings.json`  | Plan mode by default; hook registrations.                    |
| `.claude/hooks/`         | The five enforcement hooks (Python 3, standard library).     |
| `.claude/agents/`        | The `reviewer` subagent.                                     |
| `.claude/skills/`        | `/start`, `/next-step`, `/discovery`, `/grill-me`.           |
| `plans/`                 | Goal, discovery notes, and every step plan.                  |
| `src/`, `tests/`, `scripts/` | Your code.                                               |
| `docs/`                  | Your reference material, data, and outputs.                  |
| `baseline/`              | Optional. Read-only snapshot of original production code.    |
| `samples/`               | Optional. Code style / pattern references for Claude.        |
| `pyproject.toml`         | Dependencies, ruff config, project metadata.                 |
| `CLAUDE.global.md`       | Cross-project defaults — copy to `~/.claude/CLAUDE.md` once. |
| `settings.global.json`   | Tool permissions — copy to `~/.claude/settings.json` once.   |
| `CHANGES.md`             | What changed from version 17 and why.                        |

---

## Non-Python Projects

Python is the default, not a requirement. If discovery settles on another
language, it records the language, package manager, test command and lint
command in `.claude/CLAUDE.md`, and the Implementer and reviewer use those.
The global permissions set other toolchains (`go`, `cargo`, `node`, `dotnet`,
`java`, ...) to "ask" rather than "deny"; move the commands you use every day
to `allow` in `~/.claude/settings.json`.

## Key Conventions

- **Python environments:** `uv` only. `uv sync`, `uv add <package>`, `uv run pytest`.
- **Git:** Claude never runs git write commands; it suggests commits for you to run.
- **Timestamps:** `YYYY-MM-DD HH:MM:SS` from the system clock, which the harness
  hands to Claude every turn.
- **Shell commands are explained** in plain English before they run.
- **Plans are immutable history.**

---

## Changing the Reviewer's Model

Open `.claude/agents/reviewer.md` and set `model:` to `sonnet`, `opus`,
`haiku` or a full model ID. `inherit` (the default) uses the session's model.
A cheaper or different model for review is a deliberate option: the review
should not share the implementer's blind spots.

---

## Troubleshooting

**Claude opens but doesn't start.** Type `/start` (new project) or
`/next-step` (existing project). The session-start hook should already have
told Claude which one applies.

**The session isn't in plan mode after `/clear`.** Press Shift+Tab until the
status bar shows plan mode, or relaunch with `claude "/next-step"`.

**A tool call was blocked with a reason.** That is a hook doing its job. If the
rule is wrong for your project, edit the hook in `.claude/hooks/` yourself.

**Hooks don't seem to run.** Check that `python3` works in the terminal where
Claude Code runs, and that `.claude/settings.json` is the project copy from this
template. Run `claude --debug` to see hook output. To test the hooks themselves,
run `python3 .claude/hooks/hooktest.py .` from the project root (90 checks).

**You want to change the plan mid-step.** Return to plan mode and tell Claude
what should change. After re-approval, Claude appends a Plan Revision.

**You want to roll back to a previous step.** See `.claude/CLAUDE.md` § Rollback Procedure.

**You want to stress-test a plan.** Run `/grill-me`.
