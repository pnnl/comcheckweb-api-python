# Option 2: Claude Skill

## What it actually is

A **Skill** is a folder of files (Markdown + optional scripts/assets)
that Claude can dynamically load when a task matches its description.
Anthropic introduced them in late 2025 as the official way to package
domain expertise for Claude — they're like "plugins" but lighter: just
files, no protocol, no running process.

Mechanically, every Skill has the same shape:

```
comcheck-api/
├── SKILL.md            # required: name + description + body of instructions
├── reference/          # optional: extra Markdown loaded on demand
│   ├── operations.md
│   ├── types.md
│   └── simulation.md
├── examples/           # optional: copy/curate from your existing examples/
│   ├── small_office.py
│   └── full_project.py
└── scripts/            # optional: helper scripts Claude can execute
    └── validate_code.py
```

### How Claude finds and uses it

Skills live in well-known locations the host scans at startup:

- `~/.claude/skills/` — user-level, available across all projects
- `<project>/.claude/skills/` — project-level
- Bundled inside an Anthropic Plugin (more on this below)

When the user asks Claude something, Claude reads only the **YAML
frontmatter** of every skill (name + description). If a skill's
description matches the request, Claude loads its `SKILL.md` body.
Files in `reference/`, `examples/`, and `scripts/` are loaded only if
`SKILL.md` instructs Claude to read them. This **progressive
disclosure** is the whole point — the full docs corpus stays out of
context until needed.

### `SKILL.md` shape

```markdown
---
name: comcheck-api
description: Use this skill when the user is writing Python code that uses
  the comcheck_api package to build COMcheck project JSON, run compliance
  simulations against the PNNL COMcheck Web API, or work with envelope,
  lighting, mechanical, or building-area operations. Triggers on imports
  of `comcheck_api`, mentions of COMcheck/ASHRAE 90.1/IECC compliance,
  or requests to validate building energy code compliance.
---

# COMcheck API Python Client Skill

## When to use this skill

[Concrete triggers — code patterns, file names, keywords...]

## Quick start

```python
from comcheck_api import COMcheckClient
client = COMcheckClient(api_key=...)
project = client.create_project(...)
```

## Core concepts

- The `COMcheckClient` is the single entry point.
- Project construction uses fluent operation classes...
- All inputs/outputs are Pydantic models — see `reference/types.md`.

## Common patterns

[3-5 worked examples covering 80% of use cases — these drive most of the
quality lift.]

## When you need more detail

- For envelope assemblies → read `reference/operations.md`
- For type signatures → read `reference/types.md`
- For a worked example → read files in `examples/`
- To validate generated code → run `scripts/validate_code.py`
```

### Distribution channels

Two ways users get a Skill:

1. **Manual install** — user clones into
   `~/.claude/skills/comcheck-api/`. Works today, no infra. Publish
   the skill folder in the GitHub repo (or as a separate
   `comcheck-skill` repo).
2. **Plugin** — wrap the skill in an Anthropic Plugin. Plugins are
   distributed via plugin marketplaces (community or your own) and
   installed via `claude plugin install`. This is the "official" path
   for public distribution — gives discoverability without users
   needing to know which folder to drop files into.

The skill folder could also ship *inside the PyPI package* with a
`comcheck-api install-skill` console script that copies it to
`~/.claude/skills/`. Nice quality-of-life touch — install both at once.

## Realistic tradeoffs

- **Effort**: lowest of the three to write *well* — it's structured
  authoring, not engineering. ~1–2 days for a solid v1.
- **Reach**: Claude ecosystem only (Claude Code, claude.ai, Claude
  Desktop, Agent SDK). Doesn't help users on Cursor, ChatGPT, etc.
- **Quality lift**: real — Claude reads the file with intent, follows
  instructions, and progressive disclosure means a *lot* of content
  can be included without polluting every turn. But there's no
  validation loop unless `scripts/validate_code.py` is also shipped
  for Claude to execute.
- **Maintenance**: rebuild when SDK changes, same as the others. Easy
  to keep in lockstep with `llms.txt` since the source content is the
  same.
