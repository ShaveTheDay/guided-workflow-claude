# Changes

## Version 20 (2026-10-08) — findings from the second live test (a Go project)

| Area | Change | Found by |
|------|--------|----------|
| Questions | Confirmation questions must show what is being confirmed. Global rule added under Communication → Questions; discovery 1.2 (goal restatement) and 1.3 (proposed "done" test) now say to write the proposal in full before the form. Prose only; nothing enforces it. | test: Claude asked whether a "done" test was right without showing it |
| Toolchains | Python stays the default but is no longer enforced by the deny list. `go`, `cargo`, `rustc`, `node`, `npm`, `npx`, `yarn`, `pnpm`, `ruby`, `gem`, `php`, `composer`, `dotnet`, `java`, `mvn`, `gradle` moved from `deny` to `ask` in `settings.global.json`. `pip`, `sudo`, `curl`, `wget`, `rm -rf`, `chmod`, `chown` stay denied. | test: `go version` denied during discovery |
| Toolchains | `.claude/CLAUDE.md` environment table gains **Test command** and **Lint command** rows (same rows in `000-discovery.md`, `PLAN_TEMPLATE.md`, `step-000-initial.md`). Discovery 2.3 is now "Language and version" and, for a non-Python project, gathers the replacement rows and tells the user about the "ask" permissions. The reviewer agent runs the two command rows, falling back to `uv run pytest` / `uv run ruff check`. Global Code Standards say the Python defaults yield to the project's rows. README gains a Non-Python Projects section. | user decision |
| Hooks | `guard_edits.py`: a planning session may now edit any file under `plans/`, including `plans/CURRENT_PLAN`. Previously only `plans/*.md` was allowed, which blocked step 4 of the Planner's recording procedure in every planning session. Three test cases added (90 total). | test: `Update(plans/CURRENT_PLAN)` denied |


## Version 19 (2026-10-07) — fixes and enforcement from first live test

Version 18 was tested on a real project. Every finding below came from that
test. Hooks pass an 87-case regression suite, `.claude/hooks/hooktest.py`, covering
every scenario in this list. Run it from the project root:
`python3 .claude/hooks/hooktest.py .`

| Area | Change | Found by |
|------|--------|----------|
| `/start`, `/next-step` | The injected `Onboarded` check broke the skill (backticks inside the `` !`…` `` command), then matched the wrong line, then returned two values because the flag line's comment contains "true". Final form: `grep -m1 '\*\*Onboarded:\*\*' … \| sed 's/<!--.*-->//' \| grep -oE 'true\|false'`. Goal-file check now reports a placeholder line count. `git status` output no longer aborts the injection in a non-git folder. `Bash(sed *)` added to allowed tools. | test |
| `check_plan.py` | No longer reports `## Approved Plan` as not last when the pasted plan has its own `##` headings (checks only that no template section follows it). Only inspects timestamp fields; dates in prose or filenames are ignored. | test |
| Hook scope | Deny message and `.claude/CLAUDE.md` state that only `.claude/hooks/` and `.claude/settings.json` are protected; skills, agents and instruction files are editable. The model had over-generalised one denial to all of `.claude/`. | test |
| Workflow | Planning and building are separated by a context clear. After recording a step plan the Planner stops and tells the user to run `/clear` then `/next-step`. Global rules loop is now 7 steps; AGENTS.md, `/next-step` and README updated. | user request |
| Session kinds (new) | `session_context.py` classifies each session at start — `onboarding`, `planning` (active plan `completed`/`rolled-back`), `implementing` — and records it with the active plan in `.claude/session-state.json` (git-ignored). In a planning session `guard_edits.py` allows only `plans/` and `.claude/CLAUDE.md`, refuses a status change to `in-progress`; `guard_bash.py` refuses any shell write except `uv run`. An implementing session that records a new step plan becomes a planning session. | user request |
| `guard_bash.py` | Blocks shell-side writes to `plans/`, `baseline/`, `.claude/hooks/`, `.claude/settings.json` (redirection, `sed -i`, `tee`, `cp`/`mv`/`rm` into them, interpreters naming them). The model had tried to rewrite a plan with a Python heredoc, which bypassed `guard_edits.py`. | test |
| `baseline/` during onboarding | Both guards allow populating `baseline/` while `Onboarded` is `false`, so the Discoverer can take the snapshot. | review |

## Version 18 (2026-10-06)

Version 17 relied on instruction text for everything: git policy, append-only
plans, timestamps from the clock, role boundaries. That holds with a strong
model and degrades with weaker ones. Version 18 keeps the workflow a user
experiences — `/start`, `/next-step`, plan mode, four roles, one step plan per
step — and moves each rule that must always hold into something the harness
enforces. The always-loaded instruction text (global rules, project rules, roles)
drops from about 650 lines to about 450, and the full set including skills
and the plan template from about 1,900 to about 1,500.

Each change below names the risk it addresses from the Opencode portability
assessment, so the mapping is explicit when the template is ported.

### 1. Hooks enforce the rules (risks: rule volume, no harness-level enforcement, role drift)

Five Python 3 hooks in `.claude/hooks/`, registered in `.claude/settings.json`.
Standard library only; they run with the system `python3`.

| Hook | Event | What it does |
|------|-------|--------------|
| `guard_bash.py` | PreToolUse (Bash) | Blocks git write subcommands anywhere in a command chain, including `git -C`, `git --no-pager`, `$(...)` and `FOO=bar git ...` forms. Blocks pip, sudo, `rm -rf`, curl, wget, chmod, chown. |
| `guard_edits.py` | PreToolUse (Edit, Write, MultiEdit, NotebookEdit) | `baseline/` read-only. Hooks and `.claude/settings.json` not editable by Claude. A populated plan file is never overwritten whole. `completed`/`rolled-back` plans are frozen except for a rollback status change. The `## Approved Plan` section is append-only. |
| `session_context.py` | SessionStart | Injects time, `Onboarded`, active plan, status, the role that status implies, git state, and a Route line (`/start` or `/next-step`). |
| `prompt_time.py` | UserPromptSubmit | Injects the system time every turn. |
| `check_plan.py` | PostToolUse (plan files) | Reports bad status values, missing or empty Approved Plan section, placeholder or malformed timestamps, `Last updated` older than 15 minutes, and a `CURRENT_PLAN` that names a missing file. |

Tested cases are in the hook docstrings. Blocked calls return a reason that
Claude sees, so it takes the permitted route instead of retrying.

### 2. One plan record instead of two (risk: native-plan dependency)

Version 17 kept Claude Code's own plan-mode file as a second record and copied
it into an appendix with `cat ~/.claude/plans/<name>.md`. That path is a
Claude Code internal, the file is periodically deleted, and the copy step was
the most fragile instruction in the template.

Version 18 has one record. After approval the Planner pastes the approved plan
into the step plan's final `## Approved Plan` section under
`### Approved — <timestamp>`. Revisions append `### Plan Revision — <timestamp>`.
The hook makes the section append-only. The `Source plan` Meta row, the
appendix, and all `~/.claude/plans` references are gone.

Trade-off: the record is what Claude pastes, not an independent file copy.
The append-only hook and plan-mode's own approval step cover the gap for
practical purposes.

### 3. Timestamps come from the harness (risk: skipped `date` calls)

The system time is injected on session start and on every prompt. The rule
"run `date` before every timestamp" becomes "use the injected time; run `date`
only if the turn has run more than 10 minutes". `check_plan.py` catches
placeholders and stale values after the fact. The `/start` and `/next-step`
skills also inject the time, the active plan and the status line with
`` !`command` `` so the model reads them instead of fetching them.

### 4. Reviewer is a subagent (risks: role drift, work grading itself)

`.claude/agents/reviewer.md` runs the review in a fresh context with
`Read, Grep, Glob, Bash` only. It cannot edit and returns a fixed-format
report (verdict, criterion-by-criterion results, deviations, issues, tests,
lint) that the main session records in the step plan. Its `model:` field can
point the review at a different model.

Discoverer, Planner and Implementer stay in the main session because they
must talk to the user; subagents cannot use AskUserQuestion.

### 5. Instructions trimmed (risk: rule volume)

- `CLAUDE.global.md`: 300 → about 150 lines. Auditability detail now lives in
  `plans/PLAN_TEMPLATE.md`'s header and the Planner role, where it is read when
  needed.
- `.claude/AGENTS.md` and `.claude/CLAUDE.md` shortened; repeated rules replaced
  by a pointer and a table of what the hooks enforce.
- The Pre-Clear Checklist now ends with setting status `completed`, because a
  completed plan is frozen.

### 6. Permissions

`settings.global.json`: removed `Bash(cat ~/.claude/plans/*)`; added read-only
`cat plans/*`, `grep`, `head`, `ls`, `wc` so the skills' injected commands and
routine reads do not prompt. Deny list unchanged; the bash hook now backs it up.

### Unchanged

The discovery questionnaire, `/grill-me`, folder layout, `pyproject.toml`,
code standards, communication rules, AskUserQuestion conventions, and the
user-facing commands.

### For a later Opencode port

| Version 18 mechanism | Opencode equivalent |
|----------------------|---------------------|
| PreToolUse hooks | plugin `tool.execute.before` (throw to deny) |
| SessionStart / UserPromptSubmit injection | command files with `` !`cmd` `` injection; `instructions` key |
| `!`cmd`` in SKILL.md | same syntax in `.opencode/commands/*.md` |
| `reviewer` subagent with `tools` and `model` | `.opencode/agents/reviewer.md` with `permission` and `model` |
| `defaultMode: plan` | `default_agent: plan` with `edit: deny` |
| `settings.global.json` permissions | `opencode.json` `permission` block (last match wins — order the rules) |

The policy decisions (what is blocked, what is append-only, what the reviewer
may touch) carry across unchanged; only the file syntax changes.
