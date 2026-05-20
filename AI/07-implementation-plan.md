# Unified Implementation Plan: `llms.txt` + Claude Skill + MCP Server

This plan ships all three options from a **single source of content**.
The Claude Skill folder becomes the canonical asset; everything else is
generated from it or reads from it at runtime.

## Is this possible?

**Yes — and it's actually the cleanest architecture.** The trick:

- `llms.txt` / `llms-full.txt` are *built* from the same Markdown.
- The MCP server *reads from* the same Markdown at runtime, and
  exposes it via MCP's **resources** and **prompts** features in
  addition to its **tools**.
- `CLAUDE.md` and `.cursor/rules/comcheck.mdc` are also generated
  from the Skill body.

One content source, multiple renderings, no duplication. The Skill
folder becomes the canonical asset; the MCP server, llms files, and
companion rules are downstream artifacts.

## Why "MCP server uses the Skill" makes sense

MCP isn't only about tools. The protocol has three primitives:

| MCP primitive | What it does | What we'll put there |
|---|---|---|
| **Tools** | Functions the model can call | `lookup_type`, `search_docs`, `validate_code`, `get_skeleton`, `get_example` |
| **Resources** | Fetchable content the model can read | The Skill's Markdown files (`reference/*.md`, `examples/*.py`) |
| **Prompts** | Pre-formatted instructions the host can surface | The body of `SKILL.md` as a "use comcheck" system prompt |

So when an MCP-aware client connects to `comcheck-mcp`, it gets:

1. **Tools** — for live, type-safe queries against the installed SDK.
2. **Resources** — exposing the same docs the Skill exposes, so
   Claude (and any MCP client) can read them on demand.
3. **Prompts** — the Skill's instructions, surfaced as a connection
   prompt so the model gets the same "how to use this SDK" guidance
   that Claude users get from the Skill.

This means **non-Claude users (Cursor, Windsurf, Zed) get 90% of the
Skill experience through the MCP server**, without needing the Skill
file format. That's the architectural win.

## Repository layout (single source of truth)

```
comcheckweb-api-python/
├── comcheck_api/                      # the existing package
│   ├── __init__.py
│   ├── ...                            # existing code
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── skill/                     # ★ canonical content lives here
│   │   │   ├── SKILL.md
│   │   │   ├── reference/
│   │   │   │   ├── operations.md
│   │   │   │   ├── types.md
│   │   │   │   └── simulation.md
│   │   │   ├── examples/              # curated subset of /examples
│   │   │   │   ├── small_office.py
│   │   │   │   └── full_project.py
│   │   │   └── scripts/
│   │   │       └── validate_code.py
│   │   ├── CLAUDE.md                  # generated from SKILL.md
│   │   └── content.py                 # helpers to load skill files at runtime
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py                  # FastMCP server (tools + resources + prompts)
│   │   ├── tools.py                   # individual tool implementations
│   │   ├── setup.py                   # comcheck-api setup-mcp logic
│   │   └── clients.py                 # per-client config-file logic
│   └── cli.py                         # comcheck-api CLI entry point
├── docs_site/
│   ├── ...                            # existing docs
│   ├── llms.txt                       # generated
│   └── llms-full.txt                  # generated
├── scripts/
│   └── build_ai_assets.py             # the build pipeline
├── .cursor/
│   └── rules/
│       └── comcheck.mdc               # generated from SKILL.md
├── CLAUDE.md                          # repo-root copy (generated)
└── pyproject.toml                     # console scripts, [mcp] extra
```

The arrow points at `comcheck_api/ai/skill/` — that's the only place
content is hand-edited. Everything else is built from it.

## Phase-by-phase plan

### Phase 1 — Content authoring (1–2 days)

This is the most important phase. The quality of all three deliverables
depends on the quality of these files.

**Files to write by hand:**

- `comcheck_api/ai/skill/SKILL.md` — frontmatter + instructions body
  (~1,500 tokens). The "how to use comcheck_api" guidebook.
- `comcheck_api/ai/skill/reference/operations.md` — deep dive on
  operation classes.
- `comcheck_api/ai/skill/reference/types.md` — Pydantic model
  reference.
- `comcheck_api/ai/skill/reference/simulation.md` — the start →
  poll → fetch flow.
- `comcheck_api/ai/skill/examples/*.py` — 3–5 curated examples
  (copy/adapt from existing `examples/`).
- `comcheck_api/ai/skill/scripts/validate_code.py` — runs user code
  against a mocked client; returns errors.

**Why this comes first:** the rest of the pipeline is mechanical.
The content itself drives 90% of the quality lift across all three
options.

### Phase 2 — Build pipeline (~1 day)

`scripts/build_ai_assets.py` does:

1. **Generate `docs_site/llms.txt`** — TOC of `docs_site/*.md` with
   absolute URLs.
2. **Generate `docs_site/llms-full.txt`** — concatenate
   `comcheck_api/ai/skill/SKILL.md` body (cheat sheet at the top) +
   `docs_site/*.md` + `comcheck_api/ai/skill/examples/*.py`.
3. **Generate `comcheck_api/ai/CLAUDE.md`** — copy of `SKILL.md` body
   (without the Skill-specific frontmatter).
4. **Generate repo-root `CLAUDE.md`** — same content.
5. **Generate `.cursor/rules/comcheck.mdc`** — same content with
   Cursor frontmatter prepended.

Wire this into:

- A `make ai-assets` (or `uv run scripts/build_ai_assets.py`) target.
- The MkDocs build (so `mkdocs build` always emits fresh
  `llms.txt`/`llms-full.txt`).
- A pre-commit hook (optional — keeps generated files in sync).
- CI (verifies generated files match what's committed).

### Phase 3 — MCP server (~3–5 days)

`comcheck_api/mcp/server.py` using `FastMCP`:

```python
from mcp.server.fastmcp import FastMCP
from comcheck_api.ai import content
from comcheck_api.mcp import tools

mcp = FastMCP("comcheck")

# --- Tools (live introspection of the installed SDK) ---

@mcp.tool()
def list_operations() -> dict:
    """List the operation classes available in comcheck_api."""
    return tools.list_operations()

@mcp.tool()
def lookup_type(name: str) -> dict:
    """Return field-level schema for a Pydantic model in the SDK."""
    return tools.lookup_type(name)

@mcp.tool()
def search_docs(query: str, k: int = 5) -> list[dict]:
    """Search the bundled Skill reference + examples for a query."""
    return tools.search_docs(query, k)

@mcp.tool()
def get_skeleton(scenario: str) -> str:
    """Return a vetted starter snippet for a common scenario."""
    return tools.get_skeleton(scenario)

@mcp.tool()
def get_example(name: str) -> str:
    """Return the contents of a bundled example file."""
    return tools.get_example(name)

@mcp.tool()
def validate_code(code: str) -> dict:
    """Run code in a sandboxed subprocess against a mocked client."""
    return tools.validate_code(code)

@mcp.tool()
def dry_run_project(project_json: dict) -> dict:
    """Validate project JSON against the bundled jsonschema."""
    return tools.dry_run_project(project_json)

# --- Resources (Skill content as fetchable URIs) ---

@mcp.resource("comcheck://skill/reference/{name}")
def reference_doc(name: str) -> str:
    return content.read_reference(name)

@mcp.resource("comcheck://skill/examples/{name}")
def example_file(name: str) -> str:
    return content.read_example(name)

# --- Prompts (the Skill body as a connection-time guidance prompt) ---

@mcp.prompt()
def use_comcheck() -> str:
    """How to use comcheck_api correctly."""
    return content.read_skill_body()

def main():
    mcp.run()
```

Subtasks:

- **Tool implementations** in `comcheck_api/mcp/tools.py`. Each one
  should be small and have unit tests.
- **`validate_code` sandbox** is the trickiest piece. Run user code in
  a subprocess with a short timeout, no network, and a mocked
  `httpx.Client`. Returns structured errors (line, column, message).
- **`search_docs`** — start with BM25 over Skill content; vector
  search is a future enhancement.
- **CI smoke test** — start the server, list tools, list resources,
  call one tool. Catches startup regressions.

### Phase 4 — CLI (~1 day)

`comcheck_api/cli.py` exposes a single `comcheck-api` command with
subcommands:

| Command | What it does |
|---|---|
| `comcheck-api setup-mcp` | Detects installed AI clients and registers `comcheck-mcp` in their MCP config files (using absolute path). |
| `comcheck-api install-skill` | Copies `comcheck_api/ai/skill/` into `~/.claude/skills/comcheck-api/`. |
| `comcheck-api init` | Drops `CLAUDE.md` and `.cursor/rules/comcheck.mdc` into the user's current project directory. |
| `comcheck-api setup-ai` | One-shot: runs all three of the above with prompts. |

Edge cases per [Option 3](03-mcp-server.md#edge-cases-worth-handling):
existing configs, malformed JSON, symlinks, Windows paths,
`--dry-run`, `--remove`, `--force`.

### Phase 5 — Packaging & distribution (~1 day)

**`pyproject.toml`** updates:

```toml
[project.optional-dependencies]
mcp = ["mcp>=1.0"]

[project.scripts]
comcheck-mcp = "comcheck_api.mcp.server:main"
comcheck-api = "comcheck_api.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["comcheck_api"]
# Make sure the skill folder ships with the wheel:
include = ["comcheck_api/ai/skill/**/*"]
```

**Distribution channels:**

- **PyPI** — `pip install comcheck_api[mcp]` gets everything except
  the published llms files.
- **GitHub Pages** — publish `llms.txt` and `llms-full.txt` from
  `docs_site/`.
- **Repo root** — `CLAUDE.md` and `.cursor/rules/comcheck.mdc` so
  contributors and forkers benefit immediately.
- **Anthropic Plugin marketplace** (optional, follow-up release) —
  publish the Skill folder as a plugin for one-click install in
  Claude.

### Phase 6 — Evaluation & iteration (ongoing)

Build a small golden eval set (~20 prompts covering the 80% use
cases). For each, the eval harness:

1. Generates code via Claude (with your MCP server connected).
2. Runs it through `validate_code`.
3. Records: imports OK? builds project? matches expected fields?

This is what tells you the system is actually helping. Run it on
every release.

## Effort summary

| Phase | Time | Owner concern |
|---|---|---|
| 1. Content authoring | 1–2 days | Content quality |
| 2. Build pipeline | 1 day | CI |
| 3. MCP server | 3–5 days | Sandbox security |
| 4. CLI | 1 day | Cross-platform paths |
| 5. Packaging | 1 day | PyPI release |
| 6. Eval | ongoing | Pass-rate over time |
| **Total to public release** | **~2 weeks** | |

## How users use it

After release, users have three on-ramps depending on their setup.

### On-ramp 1: Web chatbot user (lowest setup)

Someone using ChatGPT / Claude.ai / Perplexity in a browser:

```
"Use the COMcheck Python SDK at https://yoursite/llms-full.txt to
help me write code that builds a 5,000 sqft office project."
```

The chatbot fetches your published `llms-full.txt` and grounds its
answer. **No install needed.** The user is just pointing the chatbot
at canonical docs.

### On-ramp 2: Claude user

```bash
pip install comcheck_api[mcp]
comcheck-api setup-ai           # one-shot setup
```

`setup-ai` runs three things with confirmation prompts:

1. `install-skill` → copies the Skill into `~/.claude/skills/`
2. `setup-mcp` → registers `comcheck-mcp` in `~/.claude.json`
3. `init` → drops `CLAUDE.md` into the current project

Now the user opens Claude Code in any project, says *"build me an
office project,"* and Claude:

- Sees the Skill description, loads its body.
- Connects to the MCP server, sees the tools.
- Reads the project's `CLAUDE.md` (if `init` was run there).
- Generates code. Calls `lookup_type` to verify field names. Calls
  `validate_code` to test the result. Iterates if anything fails.

The user gets working code on the first turn.

### On-ramp 3: Cursor / Windsurf / Zed user

```bash
pip install comcheck_api[mcp]
comcheck-api setup-mcp
```

Same MCP server, same tools, same MCP **prompts** and **resources**.
The user gets ~90% of the Claude Skill experience without the
Claude-specific format. Everything works through MCP.

### On-ramp 4: Power user / contributor

Clones the repo. The repo-root `CLAUDE.md` and `.cursor/rules/` are
already there. Their AI is already loaded with project conventions
on day one.

## How it benefits the user

### Better code, first try

The combination of:

- Skill instructions (style + conventions)
- MCP `lookup_type` (real type signatures)
- MCP `validate_code` (real error feedback)

…means generated code typically runs on the first try. Users stop
copy-pasting hallucinated method names from chatbots. The
[validate_code feedback loop](03-mcp-server.md#validation-the-killer-feature)
is what makes this dramatically better than generic AI coding
assistants.

### Always in sync with the installed SDK

`lookup_type` reflects the *installed* package. If the user has
`comcheck_api==0.9` and the SDK has `comcheck_api==1.0` documented
publicly, the MCP server gives them the right answers for *their*
version. Static docs can't do this.

### Works in the user's existing tool

No new chatbot to log into, no SaaS subscription, no UI to learn.
Whichever AI tool the user already uses for code (Claude Code,
Cursor, Windsurf, Zed, Continue) is suddenly more capable for
COMcheck. Adoption friction is just `pip install` + one CLI command.

### Cross-tool consistency

Because the Skill, MCP server, and llms files all derive from the
same source content, a user who switches from Claude Code to Cursor
mid-project gets the same conventions, the same examples, the same
guidance.

### No data leaves their machine

The MCP server runs locally. Their COMcheck API key, their project
JSON, their generated code — none of it is sent to any third party
beyond what their AI client already sends. Important for
consultants working with proprietary building data.

### Free

The user pays for their existing AI subscription, nothing more. No
COMcheck-specific SaaS fee. No hosted API quota. The whole AI layer
is just files in their venv.

## How it benefits *you* (the publisher)

- **Single source of truth.** Edit `SKILL.md` once; `llms.txt`,
  `CLAUDE.md`, and the MCP server's prompts all update.
- **Zero hosting cost.** Everything runs on the user's machine.
- **Standard PyPI workflow.** No new infra, no oncall, no SaaS
  billing.
- **Cross-tool reach.** One artifact (the MCP server) covers the IDE
  ecosystem; the Skill covers the Claude-specific marketplace; the
  llms files cover everything else.
- **Discoverable.** Each artifact is published in its native
  ecosystem (PyPI, GitHub Pages, plugin marketplace).

## What success looks like

After release, you should see:

- Eval pass-rate (code-gen → runs without errors) of ~90% on a
  20-prompt suite.
- Users discovering the package via AI-search results pointing at
  `llms.txt`.
- Claude users getting one-line setup via the plugin marketplace
  (when published there).
- Engineering consultants generating COMcheck projects from natural
  language without ever reading the Pydantic type docs themselves.

## What to defer to v2

Don't try to ship these in v1:

- Vector search in `search_docs` (start with BM25; upgrade later if
  eval shows retrieval is the bottleneck).
- Live API tools (`start_simulation`, `get_simulation_result`)
  beyond a feature-flagged opt-in.
- IDE extensions (Option 9 from [the overview](01-options-overview.md))
  — see if MCP is enough first.
- A hosted SaaS chat UI (Option 7).
- Fine-tuning a model (Option 10).

These are options if eval data shows you need them. None of them are
load-bearing for v1.

## Summary

**One source** (the Skill folder) → **three deliverables** (`llms.txt`,
the Skill itself, the MCP server) → **four user on-ramps** (web
chatbot, Claude, other IDEs, contributors).

Total effort: ~2 weeks to a public release. Total hosting cost: $0.
Quality lift: meaningful, measurable, and felt on the user's first
prompt.
