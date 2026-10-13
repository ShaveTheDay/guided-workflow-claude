# Skills

> Skill files provide structured instructions for specialised tasks within
> the step-based process. Each skill lives in its own directory with a
> `SKILL.md` file containing YAML frontmatter and markdown instructions.

## Installed Skills

| Skill | Invocation | Purpose |
|-------|------------|---------|
| `start` | `/start` | First-session onboarding. Injects the project state, presents the welcome, captures the goal, runs `/discovery` in plan mode, and writes the step-000 files after approval. Runs once per project. |
| `next-step` | `/next-step` | Start or resume a step on an onboarded project. Injects time, active plan, status and git state, then enters the right role. |
| `discovery` | `/discovery` | Structured project clarification. Run by `/start`; not a first command. |
| `grill-me` | `/grill-me` | Relentless one-at-a-time interview to stress-test a plan or design. Optional deep dive during discovery. |

## Skill File Format

Each skill uses the [Agent Skills](https://agentskills.io) open standard:

```
.claude/skills/
├── skill-name/
│   └── SKILL.md         ← YAML frontmatter + markdown instructions
└── another-skill/
    ├── SKILL.md
    └── references/      ← Optional supporting files
```

### YAML Frontmatter

```yaml
---
name: skill-name
description: What this skill does and when to use it. Include trigger phrases. Must be a single line — multiline descriptions break skill discovery.
---
```

- **name:** optional. Lowercase letters, numbers, and hyphens, max 64 characters.
  The slash command is `/<name>`; if `name` is omitted, the directory name is used.
  Keep `name` and the directory name the same to avoid confusion.
- **description:** max 1024 characters, single line. This is the primary trigger
  mechanism — Claude uses it to decide when to load the skill automatically.
  Include both what the skill does AND when to use it.

### Optional frontmatter

- **disable-model-invocation: true** — only the user can run the skill (by typing
  `/<name>`); Claude will not load it automatically. Useful for skills with side
  effects. Not used in this template, because Claude needs to route sessions to
  `/start` and `/next-step` itself.

## When to Create a Skill

A skill file is warranted when:

- A task requires a structured, repeatable interaction pattern (e.g., a discovery
  questionnaire for a specific domain).
- The project involves a specialised domain where Claude needs guided prompting
  to ask the right questions or follow the right procedure.
- A task will be repeated across multiple steps or projects and benefits from
  a codified approach.

## Adding Skills

Create a new directory under `.claude/skills/` with a `SKILL.md` file.
Skills are discovered automatically by Claude Code when it reads the
`.claude/skills/` directory. If a need for a new skill is identified
during the project lifecycle, note it in `plans/000-discovery.md` § Skill
Requirements.
