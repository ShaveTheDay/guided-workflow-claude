# Step Plan: 000 — Initial Plan

> **This file is the only record of this step.** Claude writes it immediately
> after the user approves the step's plan in plan mode. The approved plan text
> is pasted into the final `## Approved Plan` section, which is append-only
> from then on (enforced by `.claude/hooks/guard_edits.py`).
>
> **Timestamp rules — read before editing this file:**
>
> - Every timestamp uses `YYYY-MM-DD HH:MM:SS` (24-hour, local timezone).
> - Use the system time the harness injects at the start of each turn. If
>   the turn has run more than 10 minutes, run `date '+%Y-%m-%d %H:%M:%S'`.
>   Never guess, never reuse an old value. `check_plan.py` flags bad values.
> - **Create-once fields** (`Created`, decision-row timestamps, Plan
>   Revision headings, Approved Plan headings): write once, never refresh.
> - **Update-on-change fields** (`Last updated`, Session State `Last
>   Updated`): refresh to current system time on meaningful changes.
> - To revise a decision recorded earlier, do NOT edit the original row.
>   Append a `### Plan Revision — YYYY-MM-DD HH:MM:SS` sub-section to the
>   Plan Revision History section AND the revised plan text to the Approved
>   Plan section, then refresh `Last updated`.
> - A plan with status `completed` or `rolled-back` is frozen (enforced).

## Meta

| Field          | Value                                                          |
|----------------|----------------------------------------------------------------|
| Step           | 000                                                            |
| Status         | `planned`                                                      |
| Previous plan  | none                                                           |
| Created        | YYYY-MM-DD HH:MM:SS                                            |
| Last updated   | YYYY-MM-DD HH:MM:SS                                            |

---

## Changes from Previous Plan

N/A — Initial plan.

---

## Plan Revision History

<!-- Append a sub-section here ONLY when meaningful changes are made to     -->
<!-- this plan after it was recorded: decision reversed, priorities          -->
<!-- reordered, scope adjusted, blocker resolved or discovered. Cosmetic     -->
<!-- edits and typo fixes do NOT warrant a revision entry.                   -->
<!--                                                                         -->
<!-- Revisions are a flexibility safety valve, not a routine.                -->
<!--                                                                         -->
<!-- Process: return to plan mode, revise the plan with the user, and after  -->
<!-- approval:                                                               -->
<!--   1. Take the timestamp from the injected system time.                  -->
<!--   2. Append a revision sub-section here (format below).                 -->
<!--   3. Append the revised plan text to the Approved Plan section under    -->
<!--      `### Plan Revision — <same timestamp>`.                            -->
<!--   4. Refresh `Last updated` in the Meta table to the same timestamp.    -->
<!--                                                                         -->
<!-- Order: chronological, earliest first. Never edit earlier revisions.     -->

_[No revisions yet. Sub-sections will be appended below as needed.]_

---

## Objective

Onboard the project, complete discovery, and produce the high-level project
plan that subsequent step plans will execute against.

---

## Project Goal

_[Copied or summarised from `plans/000-goal.md`. This is the anchor for the entire project.]_

---

## Discovery Summary

_[Summarised from `plans/000-discovery.md`. Key findings from the clarification session:]_

### Environment Decisions

| Setting              | Default              | Project Value     | Reason for Change (if any)   |
|----------------------|----------------------|-------------------|------------------------------|
| Development OS       | WSL2 (Ubuntu)        |                   |                              |
| Target OS            | Windows              |                   |                              |
| Language             | Python 3.11+         |                   |                              |
| Environment          | `.venv/` via `uv`    |                   |                              |
| Package manager      | `uv` exclusively     |                   |                              |
| Dependency file      | `pyproject.toml`     |                   |                              |
| Lockfile             | `uv.lock`            |                   |                              |
| Test command         | `uv run pytest`      |                   |                              |
| Lint command         | `uv run ruff check src tests` |          |                              |
| Key dependencies     | —                    |                   |                              |

### Edge Cases & Constraints Identified

- _[list edge cases surfaced during discovery]_

### Out of Scope (for now)

- _[anything explicitly deferred]_

### Baseline Code

<!-- Mark N/A if building from scratch. -->

- **Existing production code:** Yes / No
- **Baseline populated:** Yes / No / N/A
- **Source:** _[repo URL, file path, or description]_
- **Key files:** _[list the main files in `baseline/` relevant to this project]_

---

## High-Level Project Plan

<!-- This is the roadmap. Each item here will become one or more step plans. -->
<!-- Sequencing and priorities may shift as the project progresses.          -->

### Proposed Steps

| Seq | Title                          | Priority | Dependencies     | Notes                    |
|-----|--------------------------------|----------|------------------|--------------------------|
| 1   | _e.g., "Set up project env"_   | P0       | none             |                          |
| 2   | _e.g., "Core data model"_      | P0       | Step 1           |                          |
| 3   | _e.g., "Processing pipeline"_  | P0       | Step 2           |                          |

---

## User Inputs & Decisions

<!-- Record every decision the user made that affects this step, including  -->
<!-- decisions made during the plan-mode conversation before approval.      -->

| # | Decision / Input                         | User Response            | Timestamp           |
|---|------------------------------------------|--------------------------|---------------------|
| 1 | Environment defaults acceptable?         |                          |                     |
| 2 | Existing production code to baseline?    |                          |                     |
| 3 | High-level plan and step 001 scope approved? |                      |                     |

---

## Model Reasoning & Decisions

<!-- Record decisions you (Claude) made, with reasoning and confidence. -->

| # | Decision                                  | Reasoning                            | Confidence | Timestamp           |
|---|-------------------------------------------|--------------------------------------|------------|---------------------|
|   |                                           |                                      |            |                     |

---

## Blockers & Unknowns

| # | Item                                  | Type       | Status   | Resolution / Notes           |
|---|---------------------------------------|------------|----------|------------------------------|
|   |                                       |            |          |                              |

**Types:** `blocker` (can't proceed), `unknown` (uncertain, may impact approach), `risk` (known risk, plan for it)
**Status:** `open`, `investigating`, `resolved`, `accepted` (risk accepted)

---

## Tasks for Step 001

### P0 — Must Do (this step fails without these)

- [ ] _Task description_

### P1 — Should Do (important but step can technically complete without)

- [ ] _Task description_

### P2 — Could Do (nice to have, do if time/clarity permits)

- [ ] _Task description_

---

## Implementation Notes

_[Technical details, approach notes, code structure decisions. Can include pseudocode,
architecture notes, file structure plans, API references, etc.]_

---

## Code Plan

N/A — step-000 produces no code. The code-level plan for each step is recorded in that step's plan.

---

## Verification Criteria

- [ ] `plans/000-goal.md` is populated with the project goal.
- [ ] `plans/000-discovery.md` records the clarification session.
- [ ] `.claude/CLAUDE.md` environment table reflects any changes from defaults.
- [ ] If existing production code is in scope, `baseline/` is populated and documented.
- [ ] This plan (step-000) is fully populated, with the approved onboarding plan in the Approved Plan section.
- [ ] User has approved the high-level plan and step 001 scope.

---

## Session State (Handoff Context)

<!-- Updated DURING implementation. A new session reads this to pick up where   -->
<!-- the last left off.                                                          -->

### Last Updated: _[not yet started]_

**Completed in this session:**
- _[nothing yet]_

**In progress / partially done:**
- _[nothing yet]_

**Files modified:**
- _[none yet]_

**Current environment state:**
- _[not yet set up]_

**Immediate next action:**
- _Launch `claude "/start"` to begin onboarding._

**Context not obvious from code/plan:**
- _[none yet]_

---

## Approved Plan

<!-- Keep this section LAST in the file. It is append-only (enforced).        -->
<!--                                                                           -->
<!-- Immediately after approval, add:                                          -->
<!--   ### Approved — YYYY-MM-DD HH:MM:SS                                      -->
<!--   followed by the plan exactly as the user approved it in plan mode.      -->
<!--                                                                           -->
<!-- A revision is appended the same way:                                      -->
<!--   ### Plan Revision — YYYY-MM-DD HH:MM:SS                                 -->
<!--   followed by the revised plan as re-approved.                            -->
<!-- Never edit text already in this section.                                  -->
