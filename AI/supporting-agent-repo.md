# Supporting an External Agent Repo

The agent (LangGraph + A2A + AWS AgentCore — see [agent.md](agent.md))
will live in a **separate repository**. This `comcheckweb-api-python`
package becomes a **dependency** of the agent repo. The question this
doc answers: *what should this package expose so the agent repo has
an easy time consuming it?*

**Decision**: keep all useful helpers as first-class SDK surface,
and ship the Skill content under `comcheck_api/ai/skill/` for
agents that want progressive-disclosure context.

## What "support agent development" means

Three things the agent repo will need from this package:

1. **The SDK itself** — `import comcheck_api` (already done; that's
   the package's job). This now includes typed introspection and
   validation helpers (`list_operations`, `lookup_type`,
   `validate_project`).
2. **Knowledge content** — the Skill folder (`SKILL.md`,
   `reference/*.md`, `examples/*.py`) so the agent can load it as
   Skill-style progressive-disclosure context.
3. **No agent-shaped wrappers** — the agent repo wraps SDK calls
   itself with whatever framework decorators it uses
   (LangGraph `@tool`, etc.). This package stays
   framework-agnostic.

## Chosen design

**One package. SDK is the surface. Skill content lives under `ai/`.**

### Layered structure inside `comcheck_api`

```
comcheck_api/
  __init__.py                    # SDK surface (existing + introspection/validation)
  client/                        # SDK (existing)
  project_operations/            # SDK (existing)
  types/                         # SDK (existing)
  introspection.py               # list_operations, lookup_type
  validation.py                  # validate_project
  ...

  ai/                            # AI-facing surface
    __init__.py
    CLAUDE.md                    # generated from SKILL.md
    content.py                   # Python helpers to load Skill files
    skill/                       # canonical content (Markdown + examples)
      SKILL.md
      reference/
      examples/
      scripts/
```

### The dependency direction is strict and one-way

```
ai/content.py ──▶ ai/skill/ (data files)

introspection.py, validation.py ──▶ comcheck_api SDK (existing)
```

`ai/` depends on no code outside itself. The introspection/validation
helpers depend on the SDK they introspect. The SDK never depends on
`ai/`. This means:

- A user who runs `pip install comcheck_api` gets the SDK + the
  introspection/validation helpers + bundled Skill files.
- The agent repo runs `pip install comcheck_api[agent]` (currently
  identical — the extra is a marker for future agent-specific
  optional deps).

### Optional dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
agent = []   # marker extra; agents consume comcheck_api directly
```

### Shipping the Skill folder in the wheel

`pyproject.toml` already includes the data files:

```toml
[tool.hatch.build.targets.wheel]
packages = ["comcheck_api"]
include = [
  "comcheck_api/ai/skill/**/*.md",
  "comcheck_api/ai/skill/**/*.py",
]
```

Now `comcheck_api.ai.content` can read those files at runtime via
`importlib.resources` — works whether the package is installed
normally or zip-imported.

### What the agent repo's code looks like

```python
# agent_repo/agent/tools.py
from langchain_core.tools import tool
import comcheck_api as cc
from comcheck_api.ai.content import load_skill_reference

@tool
def list_operations() -> list[dict]:
    """List public functions in the project operation modules."""
    return [op.model_dump() for op in cc.list_operations()]

@tool
def lookup_type(name: str) -> dict | None:
    """Reflect a Pydantic model or enum from comcheck_api.types."""
    schema = cc.lookup_type(name)
    return schema.model_dump() if schema else None

@tool
def validate_project(data: dict) -> dict:
    """Validate a project dict against the SDK schema."""
    return cc.validate_project(data).model_dump()

@tool
def update_project(project_id: str, project_data: dict) -> dict:
    """Update a saved COMcheck project."""
    client = cc.COMcheckClient()
    return client.update_project(project_id=project_id, project_data=project_data)


# agent_repo/agent/nodes/skill_router.py
def load_relevant_knowledge(state):
    msg = state["user_message"].lower()
    if "envelope" in msg:
        state["context"] += load_skill_reference("operations.md")
    if "type" in msg:
        state["context"] += load_skill_reference("types.md")
    return state
```

The agent repo holds:

- LangGraph graph definitions.
- System prompts.
- Approval policies.
- A2A endpoint code.
- AgentCore deployment config.
- Eval harness.
- The thin `@tool` adapters that wrap typed SDK calls into
  JSON-shaped tool returns.

Every line of substantive COMcheck logic is reused from
`comcheck_api`, not duplicated.

## Why this shape is the right one

### 1. The Skill folder serves multiple audiences from one location

| Audience | How they use it |
|---|---|
| Local Claude users (PyPI install) | Copy the bundled folder to `~/.claude/skills/` |
| The hosted agent | LangGraph's retrieval node loads it via `comcheck_api.ai.content` |
| Repo-root `CLAUDE.md` | Auto-loads in Claude Code sessions opened against this repo |

If it lived in the agent repo, the local Claude users would have to
reach across repos to get it.

### 2. Introspection helpers are first-class

`list_operations`, `lookup_type`, `validate_project` are useful to
anyone — a dev exploring the SDK in a notebook, an IDE plugin, an
LLM agent. They live on the SDK proper and return typed Pydantic
models. Agents that need plain JSON `.model_dump()` themselves —
that's a one-liner, not a reason for a shim layer.

### 3. The agent repo stays small and focused

It becomes a **deployment + orchestration repo**: LangGraph topology,
infra-as-code, system prompts, eval harness. Not a place where
COMcheck domain logic lives. That separation is healthy — it lets
infra changes happen without touching domain logic and vice versa.

## What goes where: ownership map

| Lives in **`comcheckweb-api-python`** (this repo) | Lives in **agent repo** |
|---|---|
| `comcheck_api/` SDK | LangGraph graph & state definitions |
| `comcheck_api/introspection.py`, `validation.py` | System prompt + prompt iteration |
| `comcheck_api/ai/skill/` (canonical content) | `@tool`-decorated wrappers around SDK calls |
| `comcheck_api/ai/content.py` (Skill loader) | Skill *retrieval node* (which docs to load when) |
| `comcheck_api/ai/CLAUDE.md` (generated) | Approval policy nodes |
| Public docs (`docs_site/`) | A2A endpoint code |
| **Unit tests** for introspection/validation/content | AgentCore deployment config |
|   | Eval harness for chat-style flows |
|   | Internal runbooks |

Two repos, two clear missions:

- **This repo**: "Here is the COMcheck domain SDK and the canonical
  content that goes with it."
- **Agent repo**: "Here is the deployed product that uses that SDK
  to provide a hosted chatbot."

## The one discipline rule

**The SDK package depends on nothing agent-framework-specific.** It
exposes plain Python functions and Pydantic models. The agent repo
is responsible for adapting them into `@tool`-decorated LangChain
tools (or Claude Agent SDK tools, or CrewAI tools, etc.).

A `langchain_core` import inside `comcheck_api` would force every
PyPI consumer to pull in LangChain's transitive dependencies. Don't
do it. Adapters belong in the consumer, not the library.

## Phased path forward

### Step 1 — Land the SDK + Skill substrate in this repo ✅ done

Tracked in [implementation-plan.md](implementation-plan.md).
What landed:

- `ai/skill/` content authored (SKILL.md, 3 reference docs, 2
  examples, validate_code.py).
- `ai/content.py` Skill loader using `importlib.resources`.
- `comcheck_api.list_operations` / `lookup_type` / `validate_project`
  as first-class SDK helpers with Pydantic return types.
- `comcheck_api/ai/CLAUDE.md` generated from `SKILL.md`.

Pending here: unit tests, CI sync check.

### Step 2 — Stand up the agent repo (next, in the agent repo)

- `pyproject.toml` declares `comcheck_api[agent]` dependency.
- LangGraph graph defined.
- `@tool` wrappers around `comcheck_api.list_operations`,
  `lookup_type`, `validate_project`, and the `COMcheckClient`
  methods.
- Skill retrieval node using `comcheck_api.ai.content`.
- A2A endpoint.
- AgentCore deployment.

The agent repo can start *immediately* — every helper it needs from
this package is already there.

### Step 3 — Iterate together

When the agent reveals a missing helper ("the LLM keeps wanting to
introspect a default template"), the missing helper gets added to
the SDK in this repo, a new version is released, and the agent's
dependency is bumped. Single source of truth pays off.

## Summary

- **One package** (`comcheck_api`), **two install profiles**
  (SDK only or `[agent]`).
- **One canonical content folder** (`comcheck_api/ai/skill/`) used by
  Claude users and the hosted agent.
- **Introspection / validation are first-class on the SDK** — typed
  Pydantic returns, no shim layer.
- **The agent repo is small and focused**: orchestration, prompts,
  deployment, framework-specific adapters. All COMcheck domain
  logic stays here.
