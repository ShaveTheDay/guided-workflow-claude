# Baseline

> **This folder is optional.** Use it when the project's goal is to enhance,
> optimise, or troubleshoot existing production code.

## Purpose

Store a **read-only snapshot** of the original production code as it existed
before any work began. This serves as:

- **A diff anchor** — compare `baseline/` against `src/` at any point to see
  exactly what has changed, without relying on git history.
- **A rollback reference** — if something goes wrong, the untouched original
  is always right here.
- **Discovery input** — the Discoverer role reads this to understand the
  starting point, identify existing patterns, and assess what needs to change.
- **An audit artifact** — makes the project self-contained. Anyone reviewing
  the work can see before and after without needing access to the original repo.

## When to Use This Folder

Use `baseline/` when the project involves:

- Enhancing or extending an existing codebase (e.g., speeding up image tile
  processing in an ArcGIS toolbox).
- Troubleshooting production code (e.g., debugging authentication issues).
- Refactoring or restructuring existing modules.
- Wrapping or adapting an existing library or API.

**Do not use** `baseline/` when:

- The project is building something entirely from scratch — there is no
  pre-existing code to snapshot.
- The original code lives in a repo you can reference by URL and the team
  has reliable access to it (though even then, a snapshot can be useful for
  offline / self-contained work).

## Rules

1. **Read-only.** No role in the step-based process may modify files in
   `baseline/`. If you need to change something, copy it to `src/` first
   and modify it there.
2. **Snapshot once.** Populate this folder during the discovery phase (step-000)
   and do not update it afterward. It must always reflect the original state.
3. **Include only what's relevant.** If the production codebase is large, copy
   only the files and modules that are in scope for this project. Document what
   was included and what was excluded in `plans/000-discovery.md`.
4. **Preserve structure.** Mirror the original folder structure so that file
   paths in `baseline/` correspond to their equivalents in the source repo.

## How to Populate

During the discovery phase, the Discoverer role will:

1. Identify which production code files are relevant to the project goal.
2. After the user approves the onboarding plan, copy them into `baseline/`,
   preserving the original directory structure. (Discovery itself runs in plan
   mode, which is read-only, so nothing is copied until approval.)
3. Record the source location, version/commit hash (if available), and the
   snapshot timestamp in `plans/000-discovery.md`.
4. Note any files that were excluded and why.

## Relationship to Other Folders

| Folder       | Contains                                    | Editable? |
|--------------|---------------------------------------------|-----------|
| `baseline/`  | Original production code (snapshot)         | **No**    |
| `src/`       | Working code (new or modified from baseline)| Yes       |
| `samples/`   | Style and pattern references                | **No**    |
