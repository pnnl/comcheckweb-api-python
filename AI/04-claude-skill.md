# Claude Skill

## What it actually is

A **Skill** is a folder of files (Markdown + optional scripts/assets)
that Claude can dynamically load when a task matches its description.
Anthropic introduced them in late 2025 as the official way to package
domain expertise for Claude — they're like "plugins" but lighter: just
files, no protocol, no running process.

Mechanically, every Skill has the same shape. This repo ships its
Skill at [`comcheck_api/ai/skill/`](../comcheck_api/ai/skill/):

```
comcheck_api/ai/skill/
├── SKILL.md            # required: name + description + body of instructions
├── reference/          # extra Markdown loaded on demand
│   ├── operations.md
│   ├── types.md
│   └── simulation.md
├── examples/           # worked examples
│   ├── small_office.py
│   └── full_project.py
└── scripts/            # helper scripts Claude can execute
    └── validate_code.py
```

The same folder is bundled in the wheel and is the canonical content
source for `CLAUDE.md` and the framework-agnostic tool functions
(via `comcheck_api.ai.content`).

## How a Skill actually works: the three-stage loading model

Claude doesn't load all of this at once. The cleverness is **progressive
disclosure** — three stages, each loading more content only when needed.

### Stage 1: At startup — load only frontmatter

When a Claude session starts, Claude reads only the **YAML frontmatter**
of every skill on disk:

```yaml
---
name: comcheck-api
description: Use this skill when the user is writing Python code that uses
  the comcheck_api package to build COMcheck project JSON, run compliance
  simulations, or work with envelope, lighting, mechanical, or
  building-area operations. Triggers on imports of `comcheck_api`,
  mentions of COMcheck/ASHRAE 90.1/IECC compliance.
---
```

Cost: ~50–100 tokens per skill. You can have dozens of skills installed;
they all sit at this stage cheaply.

The **description** is doing real work — it's a routing signal. Claude
reads "okay, comcheck-api is for COMcheck/energy code stuff" and files
it away. If the user's request doesn't match any skill, none of the
bodies load.

### Stage 2: When triggered — load `SKILL.md` body

If the user's prompt matches a skill's description (Claude decides
this), Claude loads the rest of `SKILL.md`:

```markdown
# COMcheck API Skill

## When to use this skill
[concrete triggers]

## Quick start
[a short worked example]

## Core concepts
[~3-5 bullets — entry point, operation classes, type system]

## Common patterns
[3-5 small worked examples that cover 80% of cases]

## When you need more detail
- For envelope assemblies → read `reference/operations.md`
- For type signatures → read `reference/types.md`
- To validate generated code → run `scripts/validate_code.py`
```

Cost: ~1,000–2,500 tokens. Loaded into the context for that
conversation.

The body is **instructions, not reference**. It teaches Claude how to
use the SDK and tells it where to look for deeper info.

### Stage 3: When Claude needs detail — load specific files

The body of `SKILL.md` says things like *"For envelope assemblies,
read `reference/operations.md`."* When Claude actually needs that
detail (mid-conversation, when the user asks something specific), it
reads that file. Same for `examples/` and `scripts/`.

Files in `scripts/` can also be **executed** — Claude runs them as
subprocesses (when the user has approved the relevant tool). That's
how a skill can include a `validate_code.py` that imports
`comcheck_api` and reports errors on generated code.

### Why this design matters

The progressive disclosure means a skill can ship **a lot of content**
without polluting context unless that content is actually needed:

- Frontmatter alone: cheap to scan dozens of skills.
- Body: only loaded for relevant skills, so a 2,000-token body costs
  nothing on unrelated turns.
- References/examples: only loaded on the specific turn that needs
  them.

A skill with 50KB of total content might use only 100 tokens on most
turns and only 5,000 tokens on the rare turn where Claude pulls a deep
reference. Compare to `CLAUDE.md`, which costs its full size on
**every** turn.

## Distribution

Users get the Skill bundled inside the PyPI wheel under
`comcheck_api/ai/skill/`. They can copy it into
`~/.claude/skills/comcheck-api/` to make it available across all of
their Claude sessions.

The same folder is also the canonical source for the repo-root
`CLAUDE.md`, which auto-loads in Claude Code sessions opened against
this project.

## Realistic tradeoffs

- **Effort**: lowest of the AI options to write *well* — it's
  structured authoring, not engineering. ~1–2 days for a solid v1.
- **Reach**: Claude ecosystem (Claude Code, claude.ai, Claude Desktop,
  Agent SDK).
- **Quality lift**: real — Claude reads the file with intent, follows
  instructions, and progressive disclosure means a *lot* of content
  can be included without polluting every turn. The
  [`scripts/validate_code.py`](../comcheck_api/ai/skill/scripts/validate_code.py)
  bundled with this Skill gives Claude a real syntax/import feedback
  loop too.
- **Maintenance**: rebuild when SDK changes. The Skill folder is the
  single source — `CLAUDE.md` is generated from it.
