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

## Where to publish them

Three places, in order of value:

1. **The docs site root**: `https://<your-pages-url>/llms.txt` and
   `/llms-full.txt`. This is the canonical location AI clients look
   for. With MkDocs, drop them in `docs_site/` and add to the build.
2. **Inside the PyPI wheel**: include them in `comcheck_api/ai/` (or
   similar) so users can find them after `pip install`. This is what
   lets local AI tools auto-discover them without a network call.
3. **Repo root**: `llms.txt` next to `README.md` — Claude Code, Cursor,
   etc. discover it locally during a session.

## How to generate them

Don't hand-maintain `llms-full.txt` — script it.

```python
# scripts/build_llms_txt.py  (sketch)
# Walks docs_site/, concatenates, prepends a generated cheat sheet from
# examples/, writes to docs_site/llms-full.txt.
```

Wire it into the existing MkDocs build (or a pre-commit hook). One-time
effort: ~half a day.

## Realistic tradeoffs

- **Quality lift**: noticeable when users explicitly point their AI at
  the file or use a tool that auto-loads it. Less impact on tools that
  don't read it (most general chatbots without a browse tool won't
  fetch it on their own).
- **Cost**: zero. No infra, no inference.
- **Maintenance**: rebuild on docs changes — automate via CI on push.
