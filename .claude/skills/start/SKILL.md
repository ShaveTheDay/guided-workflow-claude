---
name: start
description: Onboard a new step-based project. Presents the welcome summary, captures the project goal, runs discovery in plan mode, and writes the onboarding files after the user approves. Use on the first session of a project, when `Onboarded` is `false` in `.claude/CLAUDE.md`, or when the user says "start", "begin", "new project", "set up project", "let's start", or "kick off".
allowed-tools: Bash(date *), Bash(cat plans/*), Bash(grep *), Bash(sed *)
---

# Start a New Step-Based Project

## Current state (injected by the harness when this skill loads)

- **Time now:** !`date '+%Y-%m-%d %H:%M:%S'`
- **Onboarded:** !`grep -m1 '\*\*Onboarded:\*\*' .claude/CLAUDE.md | sed 's/<!--.*-->//' | grep -oE 'true|false'`
- **Goal placeholder lines (1 = goal not yet written, 0 = written):** !`grep -c 'Your project goal here' plans/000-goal.md`

This skill runs once per project. It presents the welcome, captures the
goal, runs discovery, and — after the user approves the onboarding plan —
writes the step-000 files. The session starts in plan mode (read-only):
everything up to approval is conversation.

---

## 1. Confirm This Is a First Session

- **Onboarded** `true` and goal placeholder lines `0` → stop; this project is set up.
  Suggest `/next-step`.
- **Onboarded** `true` but goal placeholder lines `1` → treat as `false`,
  proceed, and note the anomaly to the user.
- **Onboarded** `false` → proceed.
- If the session is not in plan mode, ask the user to press Shift+Tab until
  the status bar shows plan mode.

## 2. Present the Welcome Summary

> *Welcome to this step-based project. Here's how it works.*
>
> **The workflow** breaks development into small steps. Each step runs in a
> fresh context window: I plan the step with you in plan mode, you approve it,
> I record it, implement it, and an independent reviewer checks it. Then you
> clear the context and start the next step.
>
> **Every step leaves a record.** After each approval I write a step plan into
> this project's `plans/` folder, with the approved plan text inside it. That
> folder is the project's permanent, append-only history. Project hooks keep
> it that way.
>
> **The project structure** has three layers: process files (`.claude/`,
> `plans/`), project code (`src/`, `tests/`, `scripts/`), and supporting
> context (`docs/`, `baseline/`, `samples/`).
>
> **First, I need your project goal.**

## 3. Capture the Project Goal

Ask with AskUserQuestion (one question, two options):

- **"I'll describe it here (Recommended)"** — the user types the goal next.
- **"It's already in plans/000-goal.md"** — read it and confirm what you found.

The goal itself is free text; never ask for it as a choice. Keep an inline
goal for the onboarding plan; it is written to `plans/000-goal.md` after approval.

## 4. Run Discovery

> *Next, a structured discovery session: environment defaults, edge cases,
> any existing code to baseline, and the high-level plan. Nothing is written
> until you approve.*

Invoke `/discovery` and follow its phases.

## 5. Present the Onboarding Plan for Approval

Draft the onboarding plan in plan mode. It must contain: the goal (verbatim
if given inline); the discovery findings for `plans/000-discovery.md`;
environment changes for `.claude/CLAUDE.md`, if any; baseline files to copy,
if any; the high-level project plan and the step 001 scope; and the list of
files to be written. Ask the user to approve it.

## 6. Write the Onboarding Files (after approval)

Immediately after approval, before any other change. Use the injected time
for timestamps (run `date '+%Y-%m-%d %H:%M:%S'` if more than 10 minutes have passed).

1. `plans/000-goal.md` — goal, `Provided via`, `Timestamp`. (Edit the
   placeholder file; a whole-file Write is allowed only while it still holds
   the placeholder.)
2. `plans/000-discovery.md` from the discovery findings.
3. `.claude/CLAUDE.md` § Project Overview (name, goal) and the environment table if needed.
4. Copy baseline files into `baseline/` if applicable.
5. `plans/step-000-initial.md`: Meta (`Created`, `Last updated`), every
   section from discovery and the high-level plan, every user decision in
   User Inputs & Decisions, and the approved onboarding plan pasted under
   `## Approved Plan` → `### Approved — <timestamp>`.
6. Confirm `plans/CURRENT_PLAN` contains `step-000-initial.md`.

## 7. Complete Onboarding

1. Check the step-000 verification criteria; then set its status to
   `completed` and refresh `Last updated` (this is the last edit — a
   completed plan is frozen).
2. Set `Onboarded: true` in `.claude/CLAUDE.md`.
3. Tell the user onboarding is complete; suggest a git commit with a message
   (do not execute).
4. Suggest `/clear`, then `/next-step` to plan step 001.

## Boundaries

- Runs once per project. On an onboarded project, redirect to `/next-step`.
- No file is written before the user approves the onboarding plan.
- No project code. No plan files beyond `step-000-initial.md`.
