# Approach 2: Implementation Plan

This plan implements [Approach 2 from 09-supporting-agent-repo.md](09-supporting-agent-repo.md):
expand this package with `ai/` and `mcp/` subpackages, ship the Skill
folder + reusable framework-agnostic tool functions + an MCP server,
and provide a CLI for installation/setup. **No agent code lives in
this repo** — the LangGraph agent, A2A endpoint, and AgentCore
deployment all live in the separate agent repo, which consumes this
package as a dependency.

## Scope (what this repo will host)

✅ In scope:

- SDK (existing, unchanged behavior).
- `comcheck_api/ai/skill/` — canonical content (SKILL.md, reference,
  examples, validation script).
- `comcheck_api/ai/content.py` — runtime loader for Skill files.
- `comcheck_api/ai/tools/` — plain-Python tool functions wrapping the
  SDK. Framework-agnostic: NO LangGraph, NO Claude Agent SDK, NO MCP
  imports.
- `comcheck_api/mcp/` — local stdio MCP server using `ai/tools/` and
  `ai/content.py`.
- `comcheck_api/cli.py` — `comcheck-api` command with `setup-mcp`,
  `init`, `install-skill` subcommands.
- `scripts/build_ai_assets.py` — generates `llms.txt`,
  `llms-full.txt`, `CLAUDE.md`, `.cursor/rules/comcheck.mdc` from the
  Skill source.
- `pyproject.toml` — optional `[mcp]` and `[agent]` extras; console
  scripts.

❌ Out of scope (lives in agent repo):

- LangGraph graph definitions, nodes, state.
- A2A endpoint, agent card.
- AgentCore deployment config, IAC.
- System prompts for the production chatbot.
- Approval policy for the hosted agent.
- Eval harness for full-graph integration.

## Repo layout after implementation

```
comcheckweb-api-python/
├── comcheck_api/
│   ├── __init__.py
│   ├── api/                          # existing
│   ├── client/                       # existing
│   ├── project_operations/           # existing
│   ├── types/                        # existing
│   ├── defaults.py                   # existing
│   ├── exceptions.py                 # existing
│   ├── ai/                           # ★ new
│   │   ├── __init__.py
│   │   ├── content.py                # Skill loader (importlib.resources)
│   │   ├── CLAUDE.md                 # generated; copy of SKILL.md body
│   │   ├── skill/                    # canonical content
│   │   │   ├── SKILL.md
│   │   │   ├── reference/
│   │   │   │   ├── operations.md
│   │   │   │   ├── types.md
│   │   │   │   └── simulation.md
│   │   │   ├── examples/
│   │   │   │   ├── small_office.py
│   │   │   │   └── full_project.py
│   │   │   └── scripts/
│   │   │       └── validate_code.py
│   │   └── tools/
│   │       ├── __init__.py           # re-exports
│   │       ├── lookup.py             # list_operations, lookup_type, search_docs
│   │       ├── projects.py           # list/get/create/update/delete project
│   │       ├── simulation.py         # start, status, result
│   │       └── validation.py         # validate_code, dry_run_project
│   ├── mcp/                          # ★ new
│   │   ├── __init__.py
│   │   ├── server.py                 # FastMCP server entry point
│   │   ├── setup.py                  # setup_mcp() flow
│   │   └── clients.py                # per-AI-client config logic
│   └── cli.py                        # ★ new (comcheck-api command)
├── scripts/
│   └── build_ai_assets.py            # ★ new
├── docs_site/
│   ├── ...                           # existing
│   ├── llms.txt                      # generated
│   └── llms-full.txt                 # generated
├── .cursor/
│   └── rules/
│       └── comcheck.mdc              # generated
├── CLAUDE.md                         # generated (repo root)
└── pyproject.toml                    # updated with extras + scripts
```

## Dependency rules (the discipline rule)

```
mcp/ ──▶ ai/tools/ ──▶ comcheck_api SDK (existing)
           ▲
           │
       ai/skill/ (data files only — no code dep)
```

- `comcheck_api/ai/tools/` has **no** dependency on LangGraph, MCP,
  Claude Agent SDK, or any framework.
- `comcheck_api/mcp/` is the only place that imports `mcp` (the
  optional extra).
- No other subpackage depends on `mcp/` or `ai/`.
- Result: a user with `pip install comcheck_api` (no extras) gets
  zero extra dependencies. A user with `[mcp]` gets MCP. The agent
  repo with `[agent]` gets the SDK + `ai/` (no MCP).

## Phase plan and status

| Phase | Status | What landed |
|---|---|---|
| 1. Scaffold | ✅ done | Directory layout, Skill content, `pyproject.toml` extras, `comcheck-api` / `comcheck-mcp` console scripts |
| 2. `ai/tools/` | ✅ done | Real tool functions wrapping `COMcheckClient` and the operation modules |
| 3. MCP server | ✅ done | `mcp/server.py` exposes 11 tools, Skill resources, and a connection prompt |
| 4. CLI | ✅ done | `setup-mcp`, `install-skill`, `init`, `setup-ai` with `--dry-run` / `--force` / `--yes` |
| 5. Build pipeline | ✅ done | `scripts/build_ai_assets.py` runs and produces all five derived files |
| 6. Tests + CI | ⏳ pending | Unit tests, MCP smoke test, generated-files-in-sync check |

### Phase 1 — Scaffold ✅

Delivered:

- Directory layout matches the section above.
- [`comcheck_api/ai/skill/SKILL.md`](../comcheck_api/ai/skill/SKILL.md)
  with frontmatter + body (~5 KB).
- Reference docs:
  [operations.md](../comcheck_api/ai/skill/reference/operations.md),
  [types.md](../comcheck_api/ai/skill/reference/types.md),
  [simulation.md](../comcheck_api/ai/skill/reference/simulation.md).
- Examples:
  [small_office.py](../comcheck_api/ai/skill/examples/small_office.py),
  [full_project.py](../comcheck_api/ai/skill/examples/full_project.py).
- Static-only [validate_code.py](../comcheck_api/ai/skill/scripts/validate_code.py)
  that does syntax + import checks.
- `pyproject.toml` declares `[mcp]` and `[agent]` extras and the
  `comcheck-api` / `comcheck-mcp` console scripts.

### Phase 2 — `ai/tools/` ✅

Plain-Python tool functions, no framework imports:

- [`lookup.py`](../comcheck_api/ai/tools/lookup.py):
  - `list_operations()` — discovered live via `inspect` over the
    operation modules; returns 26 functions with signatures.
  - `lookup_type(name)` — Pydantic model reflection. Returns
    `{kind, fields[{name, type, required, default, description}]}`
    for `BaseModel`, `{kind: enum, members: [...]}` for StrEnums.
  - `search_docs(query, k=5)` — BM25 ranking over Skill content
    (paragraph-chunked at 800 chars).
- [`projects.py`](../comcheck_api/ai/tools/projects.py):
  - `list_projects()`, `get_project(id)`, `update_project(id, data)` —
    thin wrappers over `COMcheckClient`. Read `COM_API_KEY` from env
    or accept explicit `api_key=...`. Return raw dicts.
  - (No `create_project` / `delete_project` because the underlying
    SDK doesn't expose them — the COMcheck Web API treats projects
    as CRUD via the website's own UI; the SDK only updates existing
    saved projects.)
- [`simulation.py`](../comcheck_api/ai/tools/simulation.py):
  - `start_simulation(project_id)` — fetches the saved project,
    kicks off a sim, returns `{"session_id": "..."}`.
  - `start_simulation_from_data(project_data, project_id=None)` —
    for in-memory projects.
  - `get_status(session_id)`, `get_result(session_id)`.
- [`validation.py`](../comcheck_api/ai/tools/validation.py):
  - `validate_code(code, run=False)` — static syntax+import check
    by default; with `run=True` runs in a subprocess sandbox with
    network blocked and the COMcheck HTTP service mocked. 5-second
    default timeout.
  - `dry_run_project(json)` — validates against
    `ComBuilding.model_validate`, returns Pydantic errors as
    structured `[{loc, msg, type}]`.

All tools return plain dicts/lists — no SDK objects in return
shapes, so downstream agents and MCP clients can serialize without
adapters.

### Phase 3 — MCP server ✅

[`comcheck_api/mcp/server.py`](../comcheck_api/mcp/server.py)
exposes:

- **11 tools**: `list_operations`, `lookup_type`, `search_docs`,
  `list_projects`, `get_project`, `update_project`,
  `start_simulation`, `get_simulation_status`,
  `get_simulation_result`, `validate_code`, `dry_run_project`.
- **Resources**: `comcheck://skill/SKILL.md` and one resource per
  reference and example file.
- **Prompt**: `use_comcheck` returning the SKILL.md body (frontmatter
  stripped) as connection-time guidance.

The `mcp` package is lazy-imported inside `main()` so users without
the `[mcp]` extra can still import the rest of `comcheck_api`
cleanly. `mcp/setup.py` + `mcp/clients.py` implement the
`comcheck-api setup-mcp` flow.

### Phase 4 — CLI ✅

[`comcheck_api/cli.py`](../comcheck_api/cli.py) — `comcheck-api`
command with subcommands:

- `setup-mcp` — register `comcheck-mcp` with detected AI clients
  (writes the absolute path via `shutil.which` so it works without
  the user's venv activated). `--remove` unregisters.
- `install-skill` — copy `ai/skill/` into
  `~/.claude/skills/comcheck-api/`.
- `init [path]` — drop `CLAUDE.md` and `.cursor/rules/comcheck.mdc`
  into a project directory (default cwd).
- `setup-ai [path]` — one-shot: runs install-skill, setup-mcp, and
  init in sequence with confirmation prompts.

Common flags `--dry-run`, `--force`, `--yes` are available on every
subcommand via a parent parser.

### Phase 5 — Build pipeline ✅

[`scripts/build_ai_assets.py`](../scripts/build_ai_assets.py)
generates from `comcheck_api/ai/skill/`:

- [`docs_site/llms.txt`](../docs_site/llms.txt) — TOC pointing at
  `docs_site/*.md` and example files.
- [`docs_site/llms-full.txt`](../docs_site/llms-full.txt) —
  concatenated SKILL.md body + reference + docs_site + example code.
- [`comcheck_api/ai/CLAUDE.md`](../comcheck_api/ai/CLAUDE.md) —
  in-wheel copy (frontmatter stripped).
- [Repo-root `CLAUDE.md`](../CLAUDE.md) — same body, for Claude Code
  sessions in this repo.
- [`.cursor/rules/comcheck.mdc`](../.cursor/rules/comcheck.mdc) —
  same body with Cursor `alwaysApply: true` frontmatter.

Wire into the MkDocs build (or pre-commit) is still TODO; for now
run by hand: `python scripts/build_ai_assets.py`.

### Phase 6 — Tests + CI ⏳

Not yet landed. Plan:

- Unit tests for `ai/content.py` (loads files via
  `importlib.resources`).
- Unit tests for each `ai/tools/*` function with mocked SDK
  (intercept `httpx.Client` so no real network).
- Smoke test for the MCP server (start, list tools, list resources,
  call one tool — gated behind `[mcp]` extra in CI matrix).
- CI verifies that running `scripts/build_ai_assets.py` produces no
  diff against the committed generated files.

## How to use this today

```bash
# From this repo, with the package in editable install:
pip install -e '.[mcp]'

# Generate llms.txt, CLAUDE.md, etc. from the Skill source:
python scripts/build_ai_assets.py

# Set up everything for a Claude / Cursor user:
comcheck-api setup-ai

# Or just register the MCP server:
comcheck-api setup-mcp

# Or just install the Skill globally for Claude:
comcheck-api install-skill

# Or just drop CLAUDE.md / cursor rules into a project:
comcheck-api init /path/to/project
```

The agent repo, when stood up, should `pip install
comcheck_api[agent]` and consume `comcheck_api.ai.content` +
`comcheck_api.ai.tools.*` directly — see
[09-supporting-agent-repo.md](09-supporting-agent-repo.md).
