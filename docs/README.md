# Documents & Reference Material

> This folder holds user-supplied reference material, background information,
> and any documents relevant to the project. It is **not** for process
> artifacts — those live in `plans/`.

## Purpose

Use this folder for anything that provides context to the project but is
not part of the step-based process itself. Examples:

- **Reference material** — API documentation, technical specs, standards
  documents, protocol descriptions.
- **Background information** — Architecture diagrams from other systems,
  existing design documents, meeting notes, stakeholder requirements.
- **Research** — Articles, papers, or notes gathered during investigation.
- **Data files** — Sample data, test inputs, configuration exports, error
  logs, screenshots.
- **Output documents** — Reports, summaries, or deliverables that the
  project produces but that aren't code (e.g., a performance analysis
  report, a migration guide).

## Structure

This folder is freeform — organise it however makes sense for the project.
Some common patterns:

```
docs/
├── reference/          ← External docs, specs, API guides
├── data/               ← Sample data, test inputs, exports
└── output/             ← Generated reports, deliverables
```

Or simply put files at the root of `docs/` if the volume is small.

## Relationship to Other Folders

| Folder       | Contains                                         |
|--------------|--------------------------------------------------|
| `plans/`     | Process artifacts: goal, discovery, step plans    |
| `docs/`      | User-supplied reference material and outputs      |
| `baseline/`  | Read-only snapshot of original production code    |
| `samples/`   | Code style and pattern references for Claude      |
