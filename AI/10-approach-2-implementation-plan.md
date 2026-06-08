# Implementation Plan

This plan implements the design in [09-supporting-agent-repo.md](09-supporting-agent-repo.md):
expand this package with an `ai/` subpackage that ships the Skill
folder + reusable framework-agnostic tool functions, plus a generated
`CLAUDE.md`. **No agent code lives in this repo** — the LangGraph
agent, A2A endpoint, and AgentCore deployment all live in the
separate agent repo, which consumes this package as a dependency.

## Scope (what this repo will host)

✅ In scope:

- SDK (existing, unchanged behavior).
- `comcheck_api/ai/skill/` — canonical content (SKILL.md, reference,
  examples, validation script).
- `comcheck_api/ai/content.py` — runtime loader for Skill files.
- `comcheck_api/ai/tools/` — plain-Python tool functions wrapping the
  SDK. Framework-agnostic: NO LangGraph, NO Claude Agent SDK imports.
- `comcheck_api/ai/CLAUDE.md` — generated from `SKILL.md`.
- `pyproject.toml` — optional `[agent]` extra.

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
│   ├── ai/                           # AI-facing surface
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
│   │       ├── projects.py           # list/get/update project
│   │       ├── simulation.py         # start, status, result
│   │       └── validation.py         # validate_code, dry_run_project
└── pyproject.toml                    # updated with [agent] extra
```

## Dependency rules

```
ai/tools/ ──▶ comcheck_api SDK (existing)
   ▲
   │
ai/skill/ (data files only — no code dep)
```

- `comcheck_api/ai/tools/` has **no** dependency on LangGraph,
  Claude Agent SDK, or any framework.
- No other subpackage depends on `ai/`.
- Result: a user with `pip install comcheck_api` (no extras) gets
  zero extra dependencies. The agent repo with `[agent]` gets the
  SDK + `ai/`.

## Phase plan and status

| Phase | Status | What landed |
|---|---|---|
| 1. Scaffold | ✅ done | Directory layout, Skill content, `pyproject.toml` `[agent]` extra |
| 2. `ai/tools/` | ✅ done | Real tool functions wrapping `COMcheckClient` and the operation modules |
| 3. Tests + CI | ⏳ pending | Unit tests, generated-files-in-sync check |

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
- `pyproject.toml` declares the `[agent]` extra.

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
shapes, so downstream agents can serialize without adapters.

### Phase 3 — Tests + CI ⏳

Not yet landed. Plan:

- Unit tests for `ai/content.py` (loads files via
  `importlib.resources`).
- Unit tests for each `ai/tools/*` function with mocked SDK
  (intercept `httpx.Client` so no real network).
- CI verifies that `comcheck_api/ai/CLAUDE.md` stays in sync with
  the body of `SKILL.md`.

## How to use this today

```bash
# From this repo, with the package in editable install:
pip install -e .

# Or, when consumed from the agent repo:
pip install comcheck_api[agent]
```

The agent repo, when stood up, should `pip install
comcheck_api[agent]` and consume `comcheck_api.ai.content` +
`comcheck_api.ai.tools.*` directly — see
[09-supporting-agent-repo.md](09-supporting-agent-repo.md).
