# Comparison: `llms.txt` vs. Claude Skill vs. MCP Server

## Side-by-side

| Dimension | **llms.txt** | **Claude Skill** | **MCP Server** |
|---|---|---|---|
| **What it is** | Static docs file at a known URL/path | Folder of Markdown + optional scripts loaded by Claude on demand | Running process exposing typed tools to any MCP client |
| **Effort to build v1** | Half a day (mostly scripting the build) | 1–2 days (authoring + curation) | ~1 week (server + sandbox for code validation) |
| **Effort to maintain** | Rebuild on docs change (CI-able) | Same; plus periodically re-tune `description` to fire on the right prompts | Same; plus tool-API stability across SDK versions |
| **Reach (which tools benefit)** | Anything that fetches URLs or reads repo files: all major chatbots, Cursor, Copilot, Continue, Claude Code, etc. | Claude only: Claude Code, claude.ai, Claude Desktop, Agent SDK | Any MCP host: Claude Code/Desktop, Cursor, Windsurf, Zed, Continue, OpenAI's MCP support — broad and growing |
| **Discovery story** | User points their tool at the URL, or tool auto-discovers via convention | Plugin marketplace (best), `~/.claude/skills/` (manual), or bundled in the wheel | Manual config in client (`mcp.json`) — bundle as `comcheck-mcp` console script + `comcheck-api setup-mcp` |
| **Code-gen quality lift** | Modest — depends on whether the client actually loads it | Solid — progressive disclosure lets Claude pull deep context only when needed | Highest — model can call `lookup_type`, `validate_code`, get real feedback |
| **Always-loaded context cost** | Zero unless explicitly fetched | Only frontmatter (~50–100 tokens per skill) until triggered | ~1,500–2,500 tokens (tool definitions), cached |
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

## Token usage

Token cost is small but non-zero. Numbers below assume Claude Code's
prompt caching is active (which it is by default).

### Where the tokens go

#### `CLAUDE.md` (paired with `llms.txt`)

Prepended to the system prompt of every Claude Code session in that
project:

- Loaded **once per session start**, then **resent on every turn**
  (the system prompt is part of every API call).
- Counts as **input tokens**, not output.
- Anthropic API caches the system prompt — repeated turns pay ~10% of
  the original token cost for the cached prefix.

Per-session math for a ~1,200-token `CLAUDE.md`:

| Event | Token cost |
|---|---|
| Session start (first read) | ~1,200 input tokens |
| Each subsequent turn (cached) | ~120 input tokens |
| 20-turn session, no caching | 24,000 input tokens |
| 20-turn session, with caching | ~1,200 + 19 × 120 ≈ ~3,500 input tokens |

For Sonnet 4.6 input pricing (~$3 per million uncached, ~$0.30 per
million cached), a full 20-turn session adds **fractions of a cent**.

#### MCP server: two distinct costs

**Cost 1 — Tool definitions (always-loaded).** When Claude Code
connects to your MCP server, it asks "what tools do you offer?" The
server replies with each tool's name, description, and JSON schema.
All of this gets injected into the system prompt.

- Happens **once at session start**, then cached.
- Per tool: ~100–250 tokens.
- A server with ~10 tools costs **~1,500–2,500 tokens always-loaded**
  on top of the existing context.

This is the cost paid even if the user never invokes a single tool —
the "tax" for the server being connected.

**Cost 2 — Tool calls (per-use).** When the model calls a tool, three
things cost tokens:

1. The model's tool call (50–200 output tokens).
2. The tool result (sent back as input on the next turn — sized by
   your server's response).
3. The model's response based on the result (normal output tokens).

The size of the result is up to your server:

| Tool | Typical result size |
|---|---|
| `lookup_type("EnvelopeAssembly")` | ~300 tokens (compact JSON of fields + types) |
| `get_skeleton("full_project")` | ~500 tokens (a starter snippet) |
| `search_docs("envelope assembly", k=5)` | ~1,500–3,000 tokens (5 chunks) |
| `get_example("small_office")` | ~1,500 tokens (full example file) |
| `validate_code(code)` | ~50–200 tokens (just errors, when designed well) |

#### Concrete session math (with caching)

A 20-turn session, both options paired:

| Component | Tokens (input, cached after first turn) |
|---|---|
| Claude Code's own system prompt | ~5,000 (existing baseline) |
| `CLAUDE.md` if you ship one | ~1,200 |
| MCP tool definitions (10 tools) | ~2,000 |
| **Plus, on turns where tools are called:** | |
| 5 `lookup_type` calls × 300 tokens result | +1,500 (one-time, not cached) |
| 2 `search_docs` calls × 2,000 tokens | +4,000 (one-time, not cached) |
| 3 `validate_code` calls × 100 tokens | +300 |

**Always-loaded delta from MCP**: ~2,000 tokens, cached after turn 1
→ effectively ~200 tokens/turn after the first.

**Per-call delta**: depends on what the model actually invokes. Light
usage adds essentially nothing; heavy usage with big `search_docs`
results can add 5,000–10,000 tokens per session.

Even a tool-heavy 20-turn session adds **a few cents** of input cost
— and **the user pays, not you** (via their Claude/Cursor
subscription).

### Where the cost can actually bite

Three patterns to watch for:

1. **Verbose tool definitions.** A description like *"This tool
   returns the field-level schema for any Pydantic model in the
   comcheck_api package, including type annotations, default values,
   validator constraints, and inheritance chain. Use this when..."*
   is a 500-token definition. Tighten descriptions ruthlessly.

2. **Returning too much.** A `search_docs` that returns 10 full docs
   pages costs ~10,000 tokens on a single turn. Return ranked
   snippets, not whole files. Cap result size in tokens, not
   characters.

3. **Loops.** The model can call tools in a loop until satisfied. A
   `validate_code` that fails 5 times costs 2,500 tokens of one-time
   input plus all the model's reasoning between attempts. Good for
   quality but expensive. Keep error outputs terse.

4. **`CLAUDE.md` bloat.** People grow `CLAUDE.md` over time — adding
   architecture diagrams, full type listings, every gotcha. A
   5,000-token `CLAUDE.md` *is* enough to notice. The discipline:
   keep it as instructions, not documentation. Reference content
   belongs in `llms-full.txt` (fetched on demand), not always-loaded.

### Token cost summary table

| Approach | Always-loaded cost | Per-call cost |
|---|---|---|
| `CLAUDE.md` | ~1,200 tokens, cached | 0 |
| `llms.txt` | 0 (not auto-loaded) | full file when fetched |
| `llms-full.txt` | 0 (not auto-loaded) | 30K–100K when fetched |
| Claude Skill (frontmatter only) | ~50–100 tokens per skill | 1,000–2,500 (body) when triggered; references on demand |
| **MCP server** | ~1,500–2,500 tokens (tool defs), cached | varies by tool, 100–3,000 typical |

### The interesting tradeoff

An MCP server has slightly higher always-loaded cost than `CLAUDE.md`,
but much lower than always-injecting `llms-full.txt`. And it lets the
model fetch *only the slice it needs*, instead of preloading
everything.

**You pay a small standing cost so the model can pull targeted context
on demand.** For SDK code-gen, that trade is favorable —
`lookup_type` returning 300 tokens of exact field info beats stuffing
the entire types reference into the system prompt.

A well-designed MCP server can actually *reduce* total session tokens
compared to dumping a big `CLAUDE.md` or always-loading `llms-full.txt`,
because the model fetches only what it needs.

### Net guidance on tokens

- The token tax is real but small; the user (not you) pays.
- Per-session cost in cents range, even for heavy usage.
- Output quality lift means *fewer broken-on-first-try generations*,
  which actually saves tokens overall.
- Discipline:
  - Keep `CLAUDE.md` under ~2,000 tokens.
  - Keep MCP tool descriptions tight.
  - Cap MCP tool result sizes.

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
