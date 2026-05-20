# Comparison: `llms.txt` vs. Claude Skill vs. MCP Server

## Side-by-side

| Dimension | **llms.txt** | **Claude Skill** | **MCP Server** |
|---|---|---|---|
| **What it is** | Static docs file at a known URL/path | Folder of Markdown + optional scripts loaded by Claude on demand | Running process exposing typed tools to any MCP client |
| **Effort to build v1** | Half a day (mostly scripting the build) | 1–2 days (authoring + curation) | ~1 week (server + sandbox for code validation) |
| **Effort to maintain** | Rebuild on docs change (CI-able) | Same; plus periodically re-tune `description` to fire on the right prompts | Same; plus tool-API stability across SDK versions |
| **Reach (which tools benefit)** | Anything that fetches URLs or reads repo files: all major chatbots, Cursor, Copilot, Continue, Claude Code, etc. | Claude only: Claude Code, claude.ai, Claude Desktop, Agent SDK | Any MCP host: Claude Code/Desktop, Cursor, Windsurf, Zed, Continue, OpenAI's MCP support — broad and growing |
| **Discovery story** | User points their tool at the URL, or tool auto-discovers via convention | Plugin marketplace (best), `~/.claude/skills/` (manual), or bundled in the wheel | Manual config in client (`mcp.json`) — bundle as `comcheck-mcp` console script |
| **Code-gen quality lift** | Modest — depends on whether the client actually loads it | Solid — progressive disclosure lets Claude pull deep context only when needed | Highest — model can call `lookup_type`, `validate_code`, get real feedback |
| **Always-loaded context cost** | Zero unless explicitly fetched | Only frontmatter (~100 tokens per skill) until triggered | Zero — tools described, not loaded |
| **Stays in sync with installed SDK version** | No — points at "current" docs | No — same | **Yes** — reflects against the installed package directly |
| **Validation/feedback loop** | None | Possible via `scripts/` (Claude can execute) | First-class — that's the whole point of tools |
| **Hosting cost to you** | Zero | Zero | Zero (runs on user's machine) |
| **Privacy** | Public docs only | Public docs only | Local; no data leaves user's machine |
| **Sweet spot** | Browser chatbots, generic AI assistants | Claude users who want a curated, well-tuned helper | Power users in coding IDEs who want correctness |

## How they overlap (and where they don't)

- **Source content overlap**: ~80% of what goes into each is the same
  docs + examples. Build a single content pipeline and emit all three.
- **Where they don't overlap**:
  - `llms.txt` is *passive* — it's just text waiting to be read. No
    tools, no actions.
  - A Skill is *guided* — Claude reads instructions about *how* to use
    the SDK, not just *what* exists.
  - An MCP server is *interactive* — the model can ask for specific
    facts (`lookup_type`) or test its work (`validate_code`).

## Picking one to start

If only **one** is built, here's the decision tree:

- **Mostly care about reach?** → `llms.txt`. Zero infra, helps every
  tool. Floor of quality, very low effort. Great default.
- **Mostly care about Claude users specifically?** → Skill. Slightly
  more effort, much better outcomes than `llms.txt` *for Claude*.
  Distributable via plugins.
- **Mostly care about correctness in real coding workflows?** → MCP
  server. Highest effort, highest payoff, broadest reach in the IDE
  ecosystem.

## Recommendation if doing two

`llms.txt` + **MCP server**.

- `llms.txt` covers everyone — chatbots, generic tools, and tools that
  don't yet support MCP.
- MCP server covers the users who'll actually generate working code
  (people in Claude Code / Cursor / Windsurf), and `validate_code` is
  what separates "code that looks right" from "code that runs."
- Skill is great but its value is mostly subsumed by MCP for Claude
  users. The exception: for a presence in the *plugin marketplace* for
  discoverability, ship a thin Skill that just says "use the
  comcheck-mcp tools when available, otherwise consult these docs."

## Recommendation if doing all three

Build a single content pipeline that produces:

- `llms.txt` + `llms-full.txt` (web)
- `comcheck-api/` skill folder (Claude)
- An MCP server that reads from the same Markdown + examples
  (universal)

The shared substrate is the existing `docs_site/` and `examples/` —
not maintaining three corpora, just three *renderings* of one.
