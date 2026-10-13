---
name: discovery
description: Guide the Discoverer role through a structured clarification session that validates step-based template defaults against the project goal, surfaces edge cases, and gathers the content for plans/000-discovery.md and plans/step-000-initial.md. Invoked by the /start skill during onboarding. Do not use as the first command on a new project — use /start, which runs this skill at the right point.
---

# Project Setup Discovery

This skill runs inside `/start`, in plan mode. Discovery is a conversation:
gather every answer, but **do not write any file during discovery**. Where a
phase lists "Outputs", those are the destinations the content will be written
to after the user approves the onboarding plan (see `/start` step 6).

Work through the phases below **in order**. Each phase produces specific
outputs. Do not skip phases, but individual questions within a phase can
be skipped if the answer is already clear from the project goal or prior
answers.

**Interaction style:**
- Ask questions with the **AskUserQuestion** tool (multiple-choice forms), following
  the global `~/.claude/CLAUDE.md` § Communication. Group up to 4 related questions per form.
- Put your best-guess answer first, marked "(Recommended)", so the user can confirm
  or correct it rather than starting from zero.
- Ask open-ended questions (listed as "Open" in the table below) in plain text.
- If a question doesn't apply to the project type, say so and move on.
- Keep track of every answer and which output location it belongs to.

**Question types in this skill:**

| Type | Questions |
|------|-----------|
| Multiple choice | 1.1, 1.2, 2.1–2.4, 3.1, 3.4, 4.1, 4.4, 5.1–5.5, 6.1–6.3, Phase 7 offer, 8.1, 8.2 |
| Open (plain text) | 1.3, 2.5, 3.2, 3.3, 3.5, 4.2, 4.3, 4.5, 8.3 |

Multiple-choice questions can still be answered in the user's own words through "Other".
For open questions, offer a form afterwards if the answer leads to a choice.

---

## Phase 1 — Project Classification

**Goal:** Understand what kind of project this is so that later questions
can be scoped appropriately.

### Questions

1.1 **Project type** — Based on the goal, which of these best describes the work?

| Type                  | Description                                          | Examples                                                        |
|-----------------------|------------------------------------------------------|-----------------------------------------------------------------|
| `new-build`           | Building something from scratch                      | Daycare check-in app, sound desk tutorial, Rosella alert system |
| `enhance`             | Improving or extending existing working code         | Speed up ArcGIS tile processing                                 |
| `wrap`                | Creating a convenience layer over an existing API    | Geoviews wrapper, ArcGIS REST API module                        |
| `algorithm`           | Developing a standalone algorithm or computation     | Minimum viable H3 resolution                                    |
| `troubleshoot`        | Diagnosing and fixing a problem in existing code     | ArcGIS auth issues, Panel Tabulator row selections              |

> There are five types but a form allows at most four options. Offer the 3–4 most
> likely types, with your best guess first. The user can name another through "Other".
> A project can span more than one type (e.g., `troubleshoot` then `enhance`), so
> allow several answers (`multiSelect`).

1.2 **Scope check** — Write your one-sentence restatement of the project goal
in the message text, then ask the user to confirm it with a form (options:
"Correct (Recommended)" and "Needs changes" — the user explains changes through
"Other" or in reply). The restatement must be visible above the form; a form
option cannot hold it. This catches misinterpretations early.

1.3 **Success criteria** — Ask: *"How will we know this project is done?
What does success look like?"* Push for something concrete and testable. If
you propose a "done" test yourself, write the full proposed test in the message
text before asking whether it is right; never ask the user to confirm a test
they have not seen.

### Outputs

- Project type recorded in `plans/000-discovery.md` § Goal Interpretation.
- Confirmed goal restatement recorded in `plans/000-discovery.md` § Goal Interpretation.
- Success criteria recorded in `plans/step-000-initial.md` § Objective.

---

## Phase 2 — Environment Validation

**Goal:** Check each template default against the project's actual needs.
Only flag items that need to change.

### Questions

2.1 **Development OS** — Default is WSL2 (Ubuntu).

- Does this project require anything that won't work under WSL2?
- Watch for: GUI applications requiring a display server, hardware access
  (USB, GPIO, cameras, audio devices), Windows-only SDKs, Docker-in-WSL
  edge cases.
- For projects needing hardware (e.g., camera for image recognition, audio
  for sound desk): clarify whether hardware access happens at dev time or
  only at runtime on the target.

2.2 **Target OS / runtime** — Default is Windows.

- Where will this code actually run?
- Key variants to probe:

| Target               | Implications                                          |
|-----------------------|-------------------------------------------------------|
| Windows desktop       | Default. pathlib paths, no Linux assumptions.          |
| Browser (WASM/pyodide)| Severely restricted stdlib. No filesystem, no threads, limited networking. Many PyPI packages unavailable. |
| Linux server          | Reversed from default — paths, services, permissions differ. |
| Cross-platform        | Must test on both. Avoid OS-specific APIs.             |
| ArcGIS Pro (embedded) | Runs inside Pro's Python env. Version pinned to Pro release. Limited control over dependencies. |
| Cloud / container     | Docker or serverless. Different dependency and config story. |

> The table has six targets but a form allows at most four options. Offer the
> 3–4 most likely, with your best guess first; "Other" covers the rest.
>
> If the target is WASM/pyodide, flag this prominently — it changes almost
> everything about dependency management, testing, and available APIs.

2.3 **Language and version** — Default is Python 3.11+.

- Is the project constrained to a specific Python version?
- Common constraints: ArcGIS Pro pins its Python version per release.
  WASM/pyodide supports a specific CPython version. Legacy code may
  require an older version.
- **If the project is not Python** (Go, Rust, Node, .NET, Java, ...): record
  the language and version, and gather replacements for the Python rows in
  the `.claude/CLAUDE.md` environment table — Package manager, Dependency
  file, Lockfile, **Test command** and **Lint command** (for example Go:
  `go test ./...` and `go vet ./...`). The `uv`, `pyproject.toml` and ruff
  rules then do not apply; say so in Project-Specific Rules. Tell the user
  that `~/.claude/settings.json` sets that toolchain's commands to "ask"
  (not "deny"); routine ones such as the test command can be moved to
  `allow` by the user. Skip 2.4 and the PyPI parts of 2.5.

2.4 **Package manager** — Default is `uv` exclusively.

- Is there any reason `uv` won't work for this project?
- Watch for: conda-only packages (common in geospatial/scientific stacks —
  GDAL, rasterio, fiona sometimes need conda-forge). ArcGIS Pro's built-in
  conda environment. Environments where uv isn't installable.
- If conda is needed, document which packages require it and whether a
  hybrid approach (uv for most, conda for specific compiled deps) is viable.

2.5 **Key dependencies** — What are the core libraries this project needs?

- Ask the user to list them, or infer from the goal and confirm.
- For each key dependency, check:
  - Is it available on PyPI, or only conda-forge / manual install?
  - Does it have compiled/binary components (C extensions, GDAL, CUDA)?
  - Are there known version constraints or conflicts?
  - Does it work under the target runtime (especially WASM/pyodide)?

### Outputs

- Environment decisions table updated in `plans/000-discovery.md` § Environment Review.
- Additional dependencies table populated in `plans/000-discovery.md` § Environment Review.
- `.claude/CLAUDE.md` environment table updated for any deviations from defaults,
  including Test command and Lint command for a non-Python project.

---

## Phase 3 — Baseline Code Assessment

**Goal:** Determine whether existing production code needs to be captured
in `baseline/` and, if so, what to include.

### Questions

3.1 **Existing code** — Is there existing production code that this project
modifies, extends, wraps, or troubleshoots?

- If **no** → mark baseline as N/A, skip to Phase 4.
- If **yes** → continue.

3.2 **Source location** — Where does the existing code live?

- Local file path? Git repo? Shared drive? Embedded in another application
  (e.g., ArcGIS Pro toolbox `.pyt` file)?
- Can it be copied into the project, or are there licensing / size constraints?

3.3 **Scope of baseline** — Which files are relevant?

- For large codebases, identify the specific modules, classes, or files in scope.
- Ask: *"If you had to point someone to the 3–5 most important files for
  understanding what we're working with, which would they be?"*

3.4 **Version / state** — What version or state is the code in?

- Git commit hash, release version, date of last modification.
- Is the code currently working (and we're improving it), or broken
  (and we're fixing it)?

3.5 **Known issues** — Are there known problems, performance bottlenecks,
or limitations in the existing code that motivate this project?

> This question often surfaces the real requirements — the goal statement
> may say "speed up tile processing" but the known issues reveal that the
> bottleneck is actually in I/O, not computation.

### Outputs

- `plans/000-discovery.md` § Baseline Code Snapshot fully populated.
- `baseline/` populated with relevant files after approval (preserving directory structure).
- Known issues captured in `plans/step-000-initial.md` § Blockers & Unknowns.

---

## Phase 4 — Architecture & Design Constraints

**Goal:** Surface constraints that will shape the implementation approach
before planning begins.

### Questions

4.1 **Deployment model** — How does the user interact with the end product?

| Model              | Follow-up questions                                       |
|--------------------|-----------------------------------------------------------|
| CLI tool / script  | Argument parsing approach? stdin/stdout or file I/O?      |
| Library / package  | Public API surface? Will it be published to PyPI?         |
| Web application    | Framework preference? Browser-only (WASM) or server?      |
| Desktop GUI        | Framework preference? Tkinter, Qt, or other?              |
| Embedded (ArcGIS)  | Toolbox `.pyt`? Add-in? Notebook?                         |
| Background service | Scheduling? Monitoring? Logging requirements?             |

> Six models, four options per form: offer the 3–4 most likely, best guess first.
> Ask the follow-up questions for the chosen model in the next form.

4.2 **Data flow** — What goes in and what comes out?

- Input formats (files, APIs, databases, user input, hardware sensors).
- Output formats (files, API responses, UI, alerts, reports).
- Data volumes — are we dealing with kilobytes or gigabytes?
- For geospatial projects: coordinate reference systems, file formats
  (shapefile, GeoJSON, GeoPackage, KMZ, raster formats), resolution.

4.3 **External dependencies** — Does the project interact with systems
outside the codebase?

- APIs or web services (REST, SOAP, GraphQL)?
- Databases (SQLite, PostgreSQL, enterprise GIS databases)?
- Authentication systems (OAuth, IWA/NTLM/Kerberos, API keys, certificates)?
- Hardware (cameras, audio devices, sensors)?
- Third-party services that might be unavailable, rate-limited, or require credentials?

> For each external dependency, ask: *"Can we mock or stub this for
> development and testing, or do we need live access?"*

4.4 **Performance requirements** — Are there specific performance targets?

- Response time / processing speed expectations.
- Memory constraints.
- Concurrency requirements (async, threading, multiprocessing).
- Batch size limitations.

> Only ask this if the project type is `enhance`, `algorithm`, or the goal
> mentions performance. Don't force performance targets on a wrapper library.

4.5 **Error handling & resilience** — What happens when things go wrong?

- Are there failure modes that need graceful handling (network timeouts,
  corrupt input files, missing credentials)?
- Retry logic needed?
- Logging and observability requirements?

### Outputs

- Architecture notes captured in `plans/step-000-initial.md` § Implementation Notes.
- External dependencies listed in `plans/step-000-initial.md` § Blockers & Unknowns.
- Performance criteria captured in `plans/step-000-initial.md` § Verification Criteria.

---

## Phase 5 — Edge Cases & Risks

**Goal:** Proactively identify things that could derail the project or
complicate the implementation.

### Questions

Work through these categories. For each, list the potential issues you see
based on everything learned so far as a multiple-choice question with
`multiSelect` ("Which of these apply?"). The user ticks the ones that apply
and can add their own through "Other".

5.1 **Environment edge cases**

- Cross-platform path handling (Windows backslashes vs. POSIX).
- File encoding issues (UTF-8 vs. system default, BOM handling).
- Line ending differences (CRLF vs. LF) — especially relevant when
  code runs in WSL2 but targets Windows.
- Filesystem permissions or case sensitivity differences.

5.2 **Dependency edge cases**

- Packages that behave differently across platforms (e.g., GDAL, rasterio).
- Packages unavailable in WASM/pyodide if that's a target.
- Version conflicts between key dependencies.
- Packages that require system-level libraries (libgdal, libspatialindex, ffmpeg).

5.3 **Runtime edge cases**

- WASM/pyodide restrictions: no threads, no subprocess, limited filesystem,
  no native sockets, synchronous-only in some contexts.
- ArcGIS Pro embedded Python: version pinning, limited package installation,
  Pro-specific APIs that differ from standalone arcpy.
- Large data handling: memory limits, streaming vs. loading into memory.

5.4 **Integration edge cases**

- Authentication complexity (IWA/Kerberos from WSL2 is non-trivial;
  WASM environments can't do NTLM).
- API rate limits or quotas.
- Network access restrictions (firewalls, proxy servers, VPNs).
- Concurrency issues with external services.

5.5 **Testing edge cases**

- Can the core logic be tested without the external dependencies?
- Are there test datasets available, or do we need to create synthetic ones?
- For geospatial projects: do we have sample geometries covering edge cases
  (antimeridian, poles, large polygons, slivers, multipart geometries)?
- For troubleshooting projects: can we reproduce the problem reliably in dev?

### Outputs

- All identified edge cases recorded in `plans/000-discovery.md` § Edge Cases & Constraints.
- Mitigations or investigation tasks added to `plans/step-000-initial.md` § Blockers & Unknowns.

---

## Phase 6 — Code Style & Patterns

**Goal:** Determine whether the `samples/` folder should be populated and
whether default code standards need project-specific overrides.

### Questions

6.1 **Existing conventions** — Does the existing codebase (if any) follow
specific coding patterns or styles that we should match?

- If the project has a `baseline/`, scan it and note:
  - Naming conventions (snake_case, camelCase, etc.).
  - Docstring style (if different from NumPy/SciPy default).
  - Error handling patterns.
  - Logging approach.
  - Import organisation.
- Ask the user if these existing patterns should be preserved or if this
  is an opportunity to modernise.

6.2 **Style references** — Does the user have code samples they'd like to
provide as references for how new code should look or behave?

- If yes, collect them and place in `samples/` with appropriate subfolder
  structure (`style/` and/or `patterns/`).

6.3 **Standard overrides** — Do any of the global code standards need to
change for this project?

- Line length (88 is the default — does the project need something different)?
- Ruff rule selection (additional rules to enable or rules to disable)?
- Testing framework (pytest is default — anything else needed)?
- Type hint strictness (full mypy strict, or just public API signatures)?

### Outputs

- `samples/` populated after approval if the user provides reference code.
- Any standard overrides recorded in `.claude/CLAUDE.md` § Project-Specific Rules.
- Notes on existing code patterns in `plans/000-discovery.md` § Clarifying Questions & Answers.

---

## Phase 7 — Optional Deep Dive (Grill Me)

**Goal:** Offer the user a chance to stress-test the project design before
finalising the plan.

After completing Phases 1–6, offer the grill-me session as a two-option
question (put "Yes" or "Skip" first depending on your recommendation — see
the note below), with this explanation:

> *"We've covered the structured discovery questions. Before we finalise the
> plan, would you like me to grill you on the design? This is an intensive,
> one-question-at-a-time interview that walks down every branch of the
> decision tree to surface anything we might have missed. It typically takes
> 10–20 minutes. Otherwise, we can move straight to planning."*

- If the user **accepts** → invoke the `/grill-me` skill. Focus the
  interview on the project goal, architecture decisions, and edge cases
  surfaced so far. Add any new findings to the discovery content that will be
  written to `plans/000-discovery.md` and `plans/step-000-initial.md`.
- If the user **declines** → proceed directly to Phase 8.

> The grill-me session is most valuable for complex or ambiguous projects
> (types: `new-build`, `enhance`) and less critical for well-scoped tasks
> (types: `algorithm`, `wrap`). Gauge the project complexity and frame
> your recommendation accordingly.

---

## Phase 8 — Planning Inputs

**Goal:** Gather the final inputs needed to produce `step-000-initial.md`
and the high-level project plan.

### Questions

8.1 **Rough decomposition** — Based on everything learned, present a
proposed breakdown of the work into 3–7 high-level steps in text, then ask
for feedback with a form (for example "Looks right (Recommended)",
"Merge or split steps", "Reorder steps").

- Each step should be small enough to complete in one or two sessions.
- Identify dependencies between steps.
- Flag which steps carry the most risk or uncertainty.

8.2 **Priority call** — If there are competing goals or trade-offs, ask
the user to choose what matters most, with one question per trade-off.

- Common trade-offs: speed vs. readability, completeness vs. shipping
  fast, backward compatibility vs. clean design, comprehensive tests
  vs. working prototype first.

8.3 **Anything else?** — Ask: *"Is there anything I haven't asked about
that you think is important for this project?"*

> This catches the things that structured questions miss. Give the user
> space to surface tacit knowledge.

### Outputs

- High-level plan recorded in `plans/step-000-initial.md` § High-Level Project Plan.
- Priority decisions recorded in `plans/step-000-initial.md` § User Inputs & Decisions.

---

## Completion Checklist

Before handing back to `/start`, confirm you have gathered:

- [ ] The project goal (inline or from `plans/000-goal.md`).
- [ ] Content for every applicable section of `plans/000-discovery.md`.
- [ ] Any environment changes for the `.claude/CLAUDE.md` table, with reasons.
- [ ] Any project-specific rules for `.claude/CLAUDE.md`.
- [ ] The baseline file list and source details (if applicable).
- [ ] Any reference code for `samples/` (if the user provided it).
- [ ] The high-level plan and step 001 scope, confirmed by the user.
- [ ] Every user decision made during discovery, for User Inputs & Decisions.

> Then hand control back to `/start` (step 5). `/start` presents the onboarding
> plan for approval, writes all files, sets step-000 to `completed`, and sets
> `Onboarded: true`.
