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
`comcheck_api` and reports errors on generated code, similar to what
an MCP server would do.

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

## How a Skill differs from MCP

| Aspect | Claude Skill | MCP Server |
|---|---|---|
| Form | Static files | Running process |
| Content | Markdown + optional scripts | Code, defines tools at runtime |
| Activation | Description-matched, lazy | Tool-call-driven, always connected |
| Reflection (live SDK introspection) | No | Yes |
| Code execution | Yes, via `scripts/` (with permission) | Yes, via tools |
| Custom tool API | No (uses Claude's built-in tools to read files / run scripts) | Yes (you define the tool surface) |

A Skill is essentially **a guidebook with appendices and a few bundled
scripts**. An MCP server is **a live API**. A skill can do "read these
docs, then run this validation script." An MCP server can do "let me
query the installed package directly and tell you what fields
`EnvelopeAssembly` has." Different shapes, different sweet spots.

## Are Skills usable in other agents?

**No, not natively. Skills are a Claude-specific format.** The
*content* is portable, but the format is not.

### Why Skills are Claude-only

The Skill specification is defined by Anthropic. The
progressive-disclosure loading behavior, the frontmatter contract, and
the discovery paths (`~/.claude/skills/`, plugin marketplaces) are
implemented inside Claude's clients (Claude Code, Claude Desktop,
claude.ai, the Agent SDK). Nothing in the Skill format is open-protocol
the way MCP is.

A Cursor session, a ChatGPT session, a Gemini agent — none of them
know what `~/.claude/skills/` is, none of them parse `SKILL.md`
frontmatter, and none of them follow Claude's progressive-disclosure
rules. They'll happily ignore the folder if it exists on the user's
disk.

### What other ecosystems have instead

There's no perfect equivalent, but the rough analogues:

| Ecosystem | Closest thing | How it differs |
|---|---|---|
| **Cursor** | `.cursor/rules/*.mdc` | Always-loaded based on globs, no progressive disclosure, no scripts |
| **OpenAI / ChatGPT** | Custom GPTs (with knowledge files + actions) | Hosted on OpenAI, no local file loading, can't ship via PyPI |
| **Gemini** | Gems | Similar to Custom GPTs, hosted, not portable |
| **Generic agent frameworks** | RAG over docs | You pick the loading strategy, but no standard "skill" format |
| **MCP (cross-ecosystem)** | Tools + resources + prompts | Different shape — code-driven, not file-driven |

The closest thing to a *cross-ecosystem* skill format that several
tools agree on is actually **MCP itself** — specifically MCP's
"prompts" and "resources" features (less famous than tools, but
supported by the same servers). But MCP doesn't have Skill-style
progressive disclosure built in; you'd have to design that into your
server.

### How portable is the *content*?

Very. The actual prose and examples in `SKILL.md`, `reference/*.md`,
`examples/*.py` are just Markdown and Python. You can:

- Concatenate them into your `llms-full.txt` → useful for any AI tool.
- Copy `SKILL.md` body into a `.cursor/rules/*.mdc` → slightly
  different framing, mostly works.
- Expose them as MCP resources → any MCP client can fetch them.

So if you build a skill, treat the **content** as the canonical asset
and emit other formats from it (a single content pipeline). The Skill
packaging is what's Claude-specific; the words inside aren't.

### Practical implication

If your audience is mixed (some on Claude, some on Cursor, some on
ChatGPT), the right mental model is:

- **Skill**: best experience for Claude users specifically.
- **MCP server**: best cross-tool reach for IDE-based AI (Claude Code,
  Cursor, Windsurf, Zed, Continue, etc.).
- **`llms.txt` + `CLAUDE.md` + `cursor.rules`**: covers everyone else
  passively.

A Skill is a great *complement* to an MCP server when you want the
strongest possible Claude-specific experience (e.g., a skill that says
"prefer the comcheck-mcp tools when available; otherwise consult these
reference docs"). It's not a replacement for MCP if you want to reach
beyond Claude.

## Distribution channels

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
