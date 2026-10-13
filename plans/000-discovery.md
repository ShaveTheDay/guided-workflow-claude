# Discovery Notes

> This file records the outputs of the clarification / discovery session between
> the user and Claude (in the Discoverer role). Claude writes it after the user
> approves the onboarding plan. It captures environment decisions,
> edge cases, constraints, and any adjustments to the default template setup.
>
> **Timestamp rules:** every timestamp uses `YYYY-MM-DD HH:MM:SS` (24-hour,
> local timezone), taken from the system time the harness injects each turn
> (or `date '+%Y-%m-%d %H:%M:%S'` if the turn has run long). Never guess.
> The `Session Timestamp` and `Snapshot timestamp` fields are create-once —
> set them when the corresponding event occurs and do not refresh.

---

## Session Timestamp: _YYYY-MM-DD HH:MM:SS_

---

## 1. Goal Interpretation

_[How Claude interpreted the project goal. Restate it in your own words to confirm
understanding. Note any ambiguities identified.]_

---

## 2. Environment Review

### Defaults Checked

| Setting              | Default              | Valid for this project? | Adjusted to     | Reason             |
|----------------------|----------------------|------------------------|-----------------|--------------------|
| Development OS       | WSL2 (Ubuntu)        |                        |                 |                    |
| Target OS            | Windows              |                        |                 |                    |
| Language             | Python 3.11+         |                        |                 |                    |
| Environment          | `.venv/` via `uv`    |                        |                 |                    |
| Package manager      | `uv` exclusively     |                        |                 |                    |
| Dependency file      | `pyproject.toml`     |                        |                 |                    |
| Lockfile             | `uv.lock`            |                        |                 |                    |
| Test command         | `uv run pytest`      |                        |                 |                    |
| Lint command         | `uv run ruff check src tests` |               |                 |                    |

### Additional Dependencies Identified

| Package / Tool       | Purpose                          | Version constraint     |
|----------------------|----------------------------------|------------------------|
|                      |                                  |                        |

---

## 3. Clarifying Questions & Answers

| # | Question                                          | User Answer                        | Impact on Plan             |
|---|---------------------------------------------------|------------------------------------|----------------------------|
| 1 |                                                   |                                    |                            |

---

## 4. Edge Cases & Constraints

| # | Edge Case / Constraint                            | Impact                             | Mitigation                 |
|---|---------------------------------------------------|------------------------------------|----------------------------|
| 1 |                                                   |                                    |                            |

---

## 5. Baseline Code Snapshot

<!-- Complete this section if the project enhances, optimises, or troubleshoots -->
<!-- existing production code. Delete or mark N/A if building from scratch.      -->

- **Baseline populated:** Yes / No / N/A (new project)
- **Source location:** _[original repo URL, file path, or description]_
- **Version / commit hash:** _[if known]_
- **Snapshot timestamp:** YYYY-MM-DD HH:MM:SS

### Files Included in `baseline/`

| File / Directory                     | Purpose / Relevance                       |
|--------------------------------------|-------------------------------------------|
|                                      |                                           |

### Files Excluded (and why)

| File / Directory                     | Reason for Exclusion                      |
|--------------------------------------|-------------------------------------------|
|                                      |                                           |

---

## 6. Scope Boundaries

### In Scope

- _[what the project will deliver]_

### Out of Scope (deferred or excluded)

- _[what it won't — and why]_

### Assumptions

- _[things we're assuming to be true that, if wrong, would change the approach]_

---

## 7. Skill Requirements

_[Were any specialised skills (in `.claude/skills/`) needed for this discovery? If a new
skill was identified as needed, note it here with a description of what it should do.]_

---

## 8. Summary & Recommendation

_[Brief summary of discovery findings and recommended approach. This feeds directly
into the initial plan (step-000-initial.md).]_
