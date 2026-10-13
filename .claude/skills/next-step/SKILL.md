---
name: next-step
description: Start or resume a step on an already-onboarded step-based project after /clear or a new session. Reads the current state, loads the active step plan, and enters the right role based on its status. Use after /clear, when starting a new session on an onboarded project, or when the user says "next step", "continue", "pick up where I left off", or "resume". Do NOT use for first-session onboarding — use /start instead.
allowed-tools: Bash(date *), Bash(cat plans/*), Bash(grep *), Bash(sed *), Bash(git status *)
---

# Start or Resume a Step

## Current state (injected by the harness when this skill loads)

- **Time now:** !`date '+%Y-%m-%d %H:%M:%S'`
- **Onboarded:** !`grep -m1 '\*\*Onboarded:\*\*' .claude/CLAUDE.md | sed 's/<!--.*-->//' | grep -oE 'true|false'`
- **Active plan:** !`cat plans/CURRENT_PLAN`
- **Status line:** !`grep -m1 '^| Status' "plans/$(cat plans/CURRENT_PLAN)"`
- **Git:** !`git status --short 2>&1 | head -20`

These values come from the files and the clock, not from memory. Use them.

---

## 1. Confirm Onboarding State

- If **Onboarded** is `false`: stop. Tell the user the project has not been
  onboarded and suggest `/start`.
- If `true` but `plans/000-goal.md` still contains `_[Your project goal here]_`:
  treat as not onboarded, redirect to `/start`, and note the anomaly.
- Otherwise proceed.

## 2. Re-establish Context

Read the active step plan in full, with attention to:

- **Meta → Status** — decides the role.
- **Session State** — where the last session stopped.
- **Code Plan** and the **Approved Plan** section (including any revisions) —
  the approved approach.

If **Active plan** above is empty or the file is missing, stop and ask the
user for direction.

## 3. Enter the Role

| Status         | Role and action                                                   |
|----------------|-------------------------------------------------------------------|
| `completed`    | **Planner.** Plan the next step in plan mode.                     |
| `planned`      | **Implementer.** Start the recorded plan.                         |
| `in-progress`  | **Implementer.** Resume from Session State.                       |
| `implemented`  | **Reviewer.** Run the `reviewer` subagent; record its report.     |
| `rolled-back`  | Read the rollback notes, then **Planner**.                        |

**Anomaly:** active plan is `step-000-initial.md` and status is not
`completed` → onboarding did not finish cleanly. Tell the user, then act as
Planner (step-000 is never implemented).

## 4. Summarise, Then Seek Approval

> *"The active plan is step-NNN (status: X). From Session State, the next
> action is [Y]."*

- **Planner:** must be in plan mode. If not, ask the user to press Shift+Tab
  until the status bar shows plan mode. Ask clarifying questions with
  AskUserQuestion, then submit the plan for approval. After approval, record
  the step plan and **stop**: tell the user to run `/clear` then `/next-step`.
  Implementation always starts in a fresh session.
- **Implementer or Reviewer:** these change files, so submit the next action
  as a short plan for approval; approval exits plan mode. This short plan
  only resumes the recorded step — it is not a new step plan or a revision,
  so it is not added to the Approved Plan section.

Plan approval is the confirmation. Do not also ask "Shall I proceed?".
