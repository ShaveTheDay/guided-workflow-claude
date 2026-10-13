# Code Samples

> **This folder is optional.** Use it when you want Claude to match specific
> coding patterns, styles, or conventions in the project.

## Purpose

Place code samples here that demonstrate:

- **Naming conventions** — how you name variables, functions, classes, files.
- **Code structure** — how you organise modules, imports, class layout.
- **Error handling patterns** — your preferred approach to exceptions, logging, retries.
- **Documentation style** — docstring format, comment density, README conventions.
- **Testing patterns** — how you structure tests, what you mock, assertion style.
- **API patterns** — how you design interfaces, wrap external services, handle config.

## How Claude Uses These

When the Implementer role writes code, it will check this folder and match the
patterns it finds here. If no samples are present, Claude falls back to the
default code standards in the global `~/.claude/CLAUDE.md`, plus any
overrides in `.claude/CLAUDE.md` § Project-Specific Rules.

## Guidelines

- A few short, representative files are better than a large codebase dump.
- Name files descriptively: `pattern_error_handling.py`, `style_class_layout.py`.
- Include comments in samples that explain *why* a pattern is preferred, not just *what* it does.
- Samples don't need to be runnable — they're reference material, not executable code.
