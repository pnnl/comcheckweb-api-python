# Option 1: `llms.txt` + LLM-Friendly Context Files

## What it actually is

`llms.txt` is a community-driven convention (proposed by Jeremy Howard,
late 2024) for putting a *machine-readable index of your docs at the
root of your site* — analogous to `robots.txt` but pointing AI clients
at the canonical learning material for your project. It has gained
adoption from Anthropic, Cloudflare, Stripe, Supabase, Vercel, and
others.

There are typically **two** files:

| File | Purpose | Size budget |
|---|---|---|
| `/llms.txt` | A short, structured index — Markdown with H1 (project name), blockquote (one-paragraph summary), then sections of links to important docs | A few KB |
| `/llms-full.txt` | The actual flattened content — all docs concatenated as plain Markdown, optimized for being pasted into a context window | Up to a few hundred KB |

### `llms.txt` format (canonical structure)

```markdown
# COMcheck Web API – Python Client

> Type-safe Python client for the PNNL COMcheck Web API. Use it to build
> COMcheck project JSON, run compliance simulations, and parse results.

This package targets Python 3.12+. The core entry point is
`COMcheckClient`. Project construction uses fluent operation classes
(BuildingArea, Envelope, InteriorLighting, ...). All inputs/outputs are
Pydantic models.

## Docs

- [Getting Started](https://comcheck.example.com/getting-started.md): install, auth, first project
- [Types Guide](https://comcheck.example.com/types-guide.md): Pydantic models the SDK accepts and returns
- [COMcheckClient](https://comcheck.example.com/api/client.md): top-level client API
- [Simulation](https://comcheck.example.com/api/simulation.md): start/poll/fetch results

## Project Operations

- [Building Area](https://comcheck.example.com/api/operations/building-area.md)
- [Envelope](https://comcheck.example.com/api/operations/envelope.md)
- [Interior Lighting](https://comcheck.example.com/api/operations/interior-lighting.md)
- [Mechanical](https://comcheck.example.com/api/operations/mechanical.md)
- ...

## Examples

- [Build + simulate a small office](https://github.com/.../examples/small_office.py)

## Optional

- [Changelog](https://comcheck.example.com/CHANGELOG.md)
```

The `## Optional` section is special — clients are expected to drop it
first when they're context-constrained.

### `llms-full.txt`

A single concatenated Markdown file with every doc the model needs.
Generate it from the existing MkDocs sources — the structure already
lines up:

```
docs_site/index.md
docs_site/getting-started.md
docs_site/types-guide.md
docs_site/api/client.md
docs_site/api/simulation.md
docs_site/api/operations/*.md
```

Plus a hand-curated *cheat sheet* at the top (3–5 worked examples
covering the 80% use cases) — that one section drives most code-gen
quality.

## Will any AI tool auto-load it after `pip install`?

Short answer: **no, not automatically.** Installing a PyPI package
doesn't trigger anything in any AI tool. The user's AI client only
loads `llms.txt` if *that client is configured to look for it* — and
most aren't, by default.

| Tool | Will it auto-load after `pip install`? | What it actually does |
|---|---|---|
| **Claude Code** | No | Reads `CLAUDE.md` in the project/home dir automatically. Will not scan site-packages or fetch docs URLs on its own. The user has to point at it (`@path/to/llms.txt`) or paste it. |
| **Cursor** | No | Reads `.cursor/rules/*.mdc` and `cursor.rules` from the project. Won't pull from a PyPI install. |
| **GitHub Copilot** | No | Doesn't read external files. Uses open editor context. |
| **Continue / Cline / Aider** | No | Each has its own rules format; doesn't auto-discover `llms.txt`. |
| **ChatGPT / Claude.ai (web)** | No | Won't fetch URLs unless the user explicitly enables web/browse and prompts it. |
| **Anything with a "browse" tool** | Only if user asks | E.g., a user types "fetch https://yoursite/llms.txt and use it." Then yes. |

So `pip install comcheck_api` → AI tool magically knows about it: that
isn't how any of this works today.

## Why companies adopt it anyway

The convention is "passive" *for the user's local IDE AI*, but that's a
narrow audience. Three reasons publishers like Anthropic, Stripe,
Cloudflare, Supabase, and Vercel still adopt it:

### 1. It's a coordination point

Before `llms.txt`, every AI tool that wanted to ingest a project's
docs had to scrape HTML — slow, lossy, inconsistent. Publishing a
clean Markdown file at a known path means *when* a tool decides to
fetch your docs, it gets a high-fidelity version cheaply. Same logic
as `robots.txt`, `sitemap.xml`, OpenAPI schemas, OpenGraph tags. None
of those *push* — they make life easier for the eventual consumer,
and the publisher benefits when that consumer shows up.

### 2. It's cheap insurance against a likely future

For a company like Stripe, the cost of publishing one Markdown file
is rounding error. The expected value is non-trivial — every time an
AI agent gets a question about Stripe billing, there's a much higher
chance it uses the canonical answer rather than an outdated
third-party blog post.

### 3. Adoption is itself the value

The convention only works if both sides converge. By adopting early,
big companies signal: "If you build a tool that reads `llms.txt`,
there will be content waiting for it." That makes it more attractive
for tool-builders to add support, which makes publishing one even
more valuable. Same bootstrap as `robots.txt` had.

### 4. Some consumers *do* fetch it today

The "passive" framing is mostly accurate from the user's local AI
tool perspective. But there's a different class of consumer that
already does:

- **AI search products** (Perplexity, ChatGPT Search, Claude's web
  tool) prefer `llms.txt` / `llms-full.txt` when they find one.
- **Agentic web-browsing models** explicitly prefer it because it
  costs fewer tokens than HTML.
- **Documentation indexers** (some, with permission) target these
  files.

So "passive" doesn't mean "nobody reads it." It means *the user's
local IDE AI doesn't auto-load it on `pip install`*.

## Why publish `llms.txt` if `docs_site/` already exists?

Fair question — and the honest answer is: **maybe you don't.** It
depends on who you expect to consume the docs. The breakdown:

### What `docs_site/` already gives you

Material-for-MkDocs HTML on GitHub Pages is:

- Browsable by humans.
- Crawlable by general-purpose web crawlers.
- Loadable by any AI tool with a `fetch_url` capability — they *can*
  read those pages today.

So the question isn't "do AI tools have access?" — they do. It's
"what shape are those docs in?"

### What `llms.txt` adds, concretely

1. **Cleaner content per token.** When an AI fetches a rendered
   docs page it gets nav chrome, sidebars, headers, JS bundles,
   syntax-highlight `<span>`s. A given context window holds 2–5x more
   useful information when it's the `.txt` version vs. the HTML.

2. **A canonical entry point + map.** `llms.txt` (the small one,
   ~5 KB) is a *table of contents* with absolute URLs. An agent that
   lands on it immediately knows what the project is, which docs
   exist, and which are core vs. optional.

3. **Lets agents find the docs at all.** Many agents only fetch URLs
   they were *given*. A user pointing at `https://yoursite/llms.txt`
   is one URL. Pointing at `https://yoursite/` requires the agent to
   navigate an SPA — which most don't do well.

4. **Indexing signal.** Some AI search products (Perplexity, you.com,
   newer search-grounded chatbots) explicitly prefer `llms.txt` when
   present.

### When it's not worth it

- Audience is exclusively in IDEs with MCP support → build the MCP
  server and skip `llms.txt`.
- Zero traffic from web-grounded AI is expected → `llms.txt` is true
  overhead. Skip.

For COMcheck, energy-modeling engineers and consultants will
realistically ask ChatGPT/Claude/Perplexity questions like "how do I
check IECC compliance for an office building." Better representation
in those answers is the practical payoff.

## Where to publish them

Three places, in order of value:

1. **The docs site root**: `https://<your-pages-url>/llms.txt` and
   `/llms-full.txt`. This is the canonical location AI clients look
   for. With MkDocs, drop them in `docs_site/` and add to the build.
2. **Inside the PyPI wheel**: include them in `comcheck_api/ai/` (or
   similar) so users can find them after `pip install`.
3. **Repo root**: `llms.txt` next to `README.md` — Claude Code,
   Cursor, etc. discover it locally during a session.

## How to generate them

Don't hand-maintain `llms-full.txt` — script it.

```python
# scripts/build_llms_txt.py  (sketch)
# Walks docs_site/, concatenates, prepends a generated cheat sheet from
# examples/, writes to docs_site/llms-full.txt.
```

Wire it into the existing MkDocs build (or a pre-commit hook). One-time
effort: ~half a day.

## Companion files: `CLAUDE.md` and `cursor.rules`

`llms.txt` / `llms-full.txt` are *reference* — fetched on demand, big,
detailed. The companion files (`CLAUDE.md`, `.cursor/rules/*.mdc`) are
*instructions* — small, always-on, telling the AI **how** to work in
this codebase. The two layers complement each other.

### `CLAUDE.md`

**Read by**: Claude Code (CLI + IDE extensions), Claude Desktop (when
working in a project folder), the Claude Agent SDK.

**How loading works**: when Claude Code starts a session, it walks up
from the current working directory looking for `CLAUDE.md` files. It
loads:

- `~/.claude/CLAUDE.md` (user-global instructions)
- Every `CLAUDE.md` between the repo root and the cwd (project-level)
- Optionally `CLAUDE.local.md` (gitignored, for personal overrides)

All of these get prepended to the system prompt automatically — no
user action required.

**What it's for**: telling Claude *how to work in this codebase*. Not
raw documentation — instructions, conventions, gotchas:

```markdown
# COMcheck API Python Client

## What this package is
Type-safe Python client for the PNNL COMcheck Web API. Users build
COMcheck project JSON, run compliance simulations, parse results.

## Core entry points
- `COMcheckClient` — the only client class users instantiate
- Operation classes (`BuildingArea`, `Envelope`, ...) — fluent builders
- All inputs/outputs are Pydantic models from `comcheck_api.types`

## Conventions
- Always use the operation classes; do not build raw dicts
- Inputs accept dicts, outputs are validated Pydantic models — that
  asymmetry is intentional, do not "fix" it
- API key comes from the `COM_API_KEY` env var by default

## Don't
- Don't suggest constructing project JSON by hand
- Don't suggest `requests` — the package uses `httpx`
- Don't import private modules (anything starting with `_`)

## Useful files to read
- `comcheck_api/__init__.py` — public surface
- `comcheck_api/project_operations/` — operation classes
- `examples/` — golden patterns
- `docs_site/llms-full.txt` — full SDK reference
```

The style: a brief to a new colleague, not API documentation. Reference
docs live in `llms-full.txt`; `CLAUDE.md` is the *guidance layer* on
top.

### `cursor.rules` / `.cursor/rules/*.mdc`

**Read by**: Cursor.

**How loading works**: Cursor checks the project for rules files at
session start. The format has evolved:

- **Old** (still supported): a single `.cursorrules` file at the repo
  root — plain text, always loaded.
- **New** (preferred since 2024): a directory of `.cursor/rules/*.mdc`
  files. Each file has YAML frontmatter declaring *when* it should
  attach (always, or only when matching glob patterns).

**Example `.cursor/rules/comcheck.mdc`**:

```markdown
---
description: Conventions for the comcheck_api Python client
globs: ["**/*.py"]
alwaysApply: true
---

# COMcheck API Python Client

[same content as CLAUDE.md, lightly reworded for Cursor's voice]
```

### Does shipping `CLAUDE.md` inside the wheel auto-load it?

**No.** Claude Code only walks *up* from the cwd, not *down* into
venvs. A file at
`.venv/lib/python3.12/site-packages/comcheck_api/CLAUDE.md` will never
load automatically.

Ways to actually get it loaded:

| Delivery | Effort | User effort | Reliability |
|---|---|---|---|
| Ship in wheel only | None | Has to know it's there and copy it | Low |
| Document in README | Tiny | Manual copy-paste | Medium |
| `comcheck-api init` console script that copies it | Small | Run one command | High |
| MCP server exposes guidance as a connection prompt | Medium | One-time MCP config | Highest |

The `comcheck-api init` route is the practical sweet spot: ship the
file inside the wheel, but provide a CLI command that drops it into
the user's project root. Once it's there, every Claude session in
that project auto-loads it.

### What it actually buys you

For the user who has it loaded in their project:

1. **Stops Claude from making up method names.** Without it, Claude
   generates plausible-but-wrong code (`client.create_envelope(...)`,
   `client.add_building_area(...)`). With "the entry point is
   `COMcheckClient`, project sections are built via operation
   classes," hallucination drops sharply.

2. **Encodes the *non-obvious* conventions.** Things the model can't
   infer from imports alone: `httpx` not `requests`, `COM_API_KEY`
   env var, dicts in / Pydantic models out, async simulation flow.

3. **Steers behavior, not just facts.** `llms-full.txt` is reference;
   `CLAUDE.md` is instructions: "always show the three-step
   simulation pattern," "prefer operation classes over raw dicts."

4. **Always-on, no fetch round-trip.** In the system prompt every
   turn — no `@`-mention, no MCP config, no manual loading.

## Recommended file set

Minimum useful set for the repo root:

```
llms.txt                          # TOC for web-grounded AI
docs_site/llms-full.txt           # full docs as MD (built from docs_site/)
CLAUDE.md                         # auto-loads in Claude Code sessions
.cursor/rules/comcheck.mdc        # auto-loads in Cursor sessions
```

Plus optional inside-the-wheel copies if the package install should
carry the guidance — useful but lower-leverage than the repo-root
files.

## Realistic tradeoffs

- **Quality lift**: noticeable when users explicitly point their AI
  at the file or use a tool that auto-loads it. Less impact on tools
  that don't.
- **Cost**: zero infra. Token cost is small (see [comparison](05-comparison.md)).
- **Maintenance**: rebuild on docs changes — automate via CI on push.
