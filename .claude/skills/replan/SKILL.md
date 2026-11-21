---
name: replan
description: Refocus a step-based project on its goal when work drifts. Runs an independent read-only audit (replan-auditor subagent) that re-anchors on plans/000-goal.md, traces every step plan, scans code for speculative abstractions or configurability, and proposes the simplest plan that satisfies the current step. No code changes. Use when the user says "replan", "we're drifting", "refocus", "regroup", "back to basics", "is this still on track", or when the current work looks wider than the goal or the last approved plan.
allowed-tools: Bash(date *), Bash(cat plans/*), Bash(grep *), Bash(sed *), Bash(git status *)
---

# Replan — Refocus on the Goal

## Current state (injected by the harness when this skill loads)

- **Time now:** !`date '+%Y-%m-%d %H:%M:%S'`
- **Onboarded:** !`grep -m1 '\*\*Onboarded:\*\*' .claude/CLAUDE.md | sed 's/<!--.*-->//' | grep -oE 'true|false'`
- **Active plan:** !`cat plans/CURRENT_PLAN`
- **Status line:** !`grep -m1 '^| Status' "plans/$(cat plans/CURRENT_PLAN)"`
- **Git:** !`git status --short 2>&1 | head -20`

These values come from the files and the clock, not from memory. Use them.

---

## Purpose

Drift has two sources. Each step can move a little further from the goal,
and the model can design for needs nobody stated. This skill pulls both
back. The aim is not a better design. It is the **simplest solution that
satisfies the requirement**: no abstractions, interfaces, factory patterns
or configurability for hypothetical future needs.

`/replan` makes **no code changes**. Its only possible writes are to the
step plan, through the existing revision or planning process.

## 1. Check Preconditions

- **Onboarded** is `false`: stop and suggest `/start`.
- Not in plan mode: ask the user to press Shift+Tab until the status bar
  shows plan mode. The audit and the discussion are read-only.

## 2. Capture the Trigger

If the user has not said why they are running `/replan`, ask in plain
text: what made them think the work is drifting? Also note any decisions
the user made in chat this session that are not yet in a plan file.

## 3. Run the Audit

Spawn the **`replan-auditor`** subagent. Its task message contains only:

- the active plan path;
- the user's reason, in their words;
- unrecorded user decisions from chat, if any.

Do **not** pass your own reasoning, design ideas or justification for the
current scope. The audit is independent only if it sees the records, not
the arguments.

## 4. Present and Decide

Present the report verbatim. Then ask about the proposed changes with
AskUserQuestion: each **cut** or **defer** item (group them when there are
more than four), recommended option first. Show the item and the auditor's
reason in the message before the form. If the verdict is ON COURSE, say so
and stop. Nothing is recorded.

Do not argue for items the auditor cut. If you disagree, say so once with
the reason, and let the user decide.

## 5. Act by Status

| Status | What happens |
|--------|--------------|
| `planned` / `in-progress` | Submit the trimmed plan for approval (plan mode). After approval, follow the revision process: append a `### Plan Revision — <timestamp>` row set to Plan Revision History, append the trimmed plan to the Approved Plan section under the same heading with headings demoted two levels, record the user's answers in User Inputs & Decisions, refresh `Last updated`. Then **stop**: tell the user to run `/clear` then `/next-step`. Recording the revision is planning, and planning and building never share a context (the hooks refuse code edits in this session). |
| `implemented` | Do not revise. Run the `reviewer` subagent as normal, and record the audit's cut items alongside the review as issues for the user to decide on. |
| `completed` / `rolled-back` | Enter the **Planner** role. Draft the next step's objective against the audit's goal line and "simplest plan" bullets. Its Changes from Previous Plan records the realignment and what was deferred. |

If the recommendation is **roll back**, explain what that would mean and
point to `.claude/CLAUDE.md` § Rollback Procedure. Never start a rollback
without the user's explicit decision.

Deferred items are not lost: record them in the step plan's Blockers &
Unknowns as `risk` rows with status `accepted` and the note "deferred by
/replan".

## Boundaries

- No code edits, no shell writes, no git writes.
- No new scope. A replan only keeps, cuts, defers or simplifies.
- One record: everything goes in the step plan. No separate replan file.
