# Implementation Plan

This plan implements the design in [supporting-agent-repo.md](supporting-agent-repo.md):
ship the Skill folder under `comcheck_api/ai/`, expose introspection
and validation as first-class SDK helpers, and generate a `CLAUDE.md`
from `SKILL.md`. **No agent code lives in this repo** — the
LangGraph agent, A2A endpoint, and AgentCore deployment all live in
the separate agent repo, which consumes this package as a dependency.

## Scope (what this repo will host)

✅ In scope:

- SDK (existing, unchanged behavior).
- `comcheck_api/introspection.py` — `list_operations()`,
  `lookup_type(name)` with Pydantic return models
  (`OperationInfo`, `TypeSchema`, `FieldSchema`).
- `comcheck_api/validation.py` — `validate_project(data)` with
  Pydantic return models (`ValidationResult`, `ValidationError`).
- `comcheck_api/ai/skill/` — canonical content (SKILL.md, reference,
  examples, validation script).
- `comcheck_api/ai/content.py` — runtime loader for Skill files.
- `comcheck_api/ai/CLAUDE.md` — generated from `SKILL.md`.
- `pyproject.toml` — optional `[agent]` extra (marker only today).

❌ Out of scope (lives in agent repo):

- LangGraph graph definitions, nodes, state.
- `@tool`-decorated wrappers around SDK calls.
- A2A endpoint, agent card.
- AgentCore deployment config, IAC.
- System prompts for the production chatbot.
- Approval policy for the hosted agent.
- Eval harness for full-graph integration.

## Repo layout after implementation

```
comcheckweb-api-python/
├── comcheck_api/
│   ├── __init__.py                   # exports introspection + validation helpers
│   ├── api/                          # existing
│   ├── client/                       # existing
│   ├── project_operations/           # existing
│   ├── types/                        # existing
│   ├── defaults.py                   # existing
│   ├── exceptions.py                 # existing
│   ├── introspection.py              # list_operations, lookup_type
│   ├── validation.py                 # validate_project
│   ├── ai/                           # AI-facing surface
│   │   ├── __init__.py
│   │   ├── content.py                # Skill loader (importlib.resources)
│   │   ├── CLAUDE.md                 # generated; copy of SKILL.md body
│   │   └── skill/                    # canonical content
│   │       ├── SKILL.md
│   │       ├── reference/
│   │       │   ├── operations.md
│   │       │   ├── types.md
│   │       │   └── simulation.md
│   │       ├── examples/
│   │       │   ├── small_office.py
│   │       │   └── full_project.py
│   │       └── scripts/
│   │           └── validate_code.py
└── pyproject.toml                    # [agent] marker extra
```

## Dependency rules

```
introspection.py, validation.py ──▶ comcheck_api SDK (existing)

ai/content.py ──▶ ai/skill/ (data files)
```

- The introspection / validation helpers depend only on the
  existing SDK — no agent framework, no MCP, nothing else.
- `ai/` depends on no code outside itself.
- The SDK never depends on `ai/`.
- Result: a user with `pip install comcheck_api` (no extras) gets
  the SDK, the typed introspection/validation helpers, and the
  Skill folder for free. No extra dependencies.

## Phase plan and status

| Phase | Status | What landed |
|---|---|---|
| 1. Skill scaffold | ✅ done | Directory layout, Skill content, `pyproject.toml` `[agent]` extra |
| 2. SDK helpers | ✅ done | `introspection.py` + `validation.py` exposed at the package root |
| 3. Tests + CI | ⏳ pending | Unit tests, generated-files-in-sync check |

### Phase 1 — Skill scaffold ✅

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

### Phase 2 — SDK helpers ✅

Typed, first-class helpers exported from `comcheck_api`:

- [`introspection.py`](../comcheck_api/introspection.py):
  - `list_operations() -> list[OperationInfo]` — discovered live via
    `inspect` over the operation modules; returns one
    `OperationInfo` per public function with module, name,
    signature, and docstring summary.
  - `lookup_type(name) -> TypeSchema | None` — Pydantic model
    reflection. Returns `TypeSchema(kind="model", fields=[...])`
    for `BaseModel`s, `TypeSchema(kind="enum", members=[...])` for
    StrEnums. Case-insensitive fallback. Returns `None` when no
    match.
- [`validation.py`](../comcheck_api/validation.py):
  - `validate_project(data) -> ValidationResult` — accepts a
    project dict or an existing `ComBuilding`; returns a typed
    `ValidationResult` with `ok: bool` and a list of
    `ValidationError(loc, msg, type)`. No network calls.

All return types are `pydantic.BaseModel` subclasses, so callers
that need JSON do `result.model_dump()` and downstream callers that
want typed access just use the attributes.

### Phase 3 — Tests + CI ⏳

Not yet landed. Plan:

- Unit tests for `introspection.list_operations` /
  `introspection.lookup_type` over the live SDK.
- Unit tests for `validation.validate_project` covering a default
  template (passes) and a known-bad payload (fails with expected
  loc/type).
- Unit tests for `ai/content.py` (loads files via
  `importlib.resources`).
- CI verifies that `comcheck_api/ai/CLAUDE.md` and the repo-root
  `CLAUDE.md` stay in sync with the body of `SKILL.md`.

## How to use this today

```python
import comcheck_api as cc

# Introspect available operations
for op in cc.list_operations():
    print(op.group, op.signature)

# Reflect a Pydantic model
schema = cc.lookup_type("ComBuilding")
if schema:
    for field in schema.fields:
        print(field.name, field.type, field.required)

# Validate project data
result = cc.validate_project(project_dict)
if not result.ok:
    for err in result.errors:
        print(err.loc, err.msg)
```

The agent repo, when stood up, should `pip install
comcheck_api[agent]` and consume `comcheck_api.list_operations`,
`comcheck_api.lookup_type`, `comcheck_api.validate_project`, plus
`COMcheckClient` directly — see
[supporting-agent-repo.md](supporting-agent-repo.md).
