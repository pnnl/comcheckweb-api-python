# Supporting an External Agent Repo

The agent (LangGraph + A2A + AWS AgentCore — see [08-agent.md](08-agent.md))
will live in a **separate repository**. This `comcheckweb-api-python`
package becomes a **dependency** of the agent repo. The question this
doc answers: *what should this package expose so the agent repo has
an easy time consuming it?*

**Decision**: expand this package to ship SDK + Skill content +
reusable framework-agnostic tool functions, with strict internal
layering.

## What "support agent development" means

Three things the agent repo will need from this package:

1. **The SDK itself** — `import comcheck_api` (already done; that's
   the package's job).
2. **Knowledge content** — the Skill folder (`SKILL.md`,
   `reference/*.md`, `examples/*.py`) so the agent can load it as
   Skill-style progressive-disclosure context.
3. **Tools** — Python functions the agent's LangGraph nodes can call
   (`lookup_type`, `update_project`, `start_simulation`,
   `validate_code`, etc.).

## Chosen design

**Keep one package, with optional `[agent]` extra and a clear internal
layering.**

### Layered structure inside `comcheck_api`

```
comcheck_api/
  __init__.py                    # SDK surface (existing)
  client/                        # SDK (existing)
  project_operations/            # SDK (existing)
  types/                         # SDK (existing)
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
    tools/                       # ready-made tool functions
      __init__.py
      lookup.py                  # lookup_type, list_operations, search_docs
      projects.py                # list/get/update project
      simulation.py              # start, status, result
      validation.py              # validate_code, dry_run_project
```

### The dependency direction is strict and one-way

```
ai/tools/ ──▶ comcheck_api SDK (existing)
   ▲
   │
ai/skill/ (data files, no code dep)
```

`ai/` depends on the SDK. The SDK never depends on `ai/`. This means:

- A user who runs `pip install comcheck_api` gets the SDK and
  nothing else costly.
- The agent repo runs `pip install comcheck_api[agent]` and gets the
  SDK + `ai/` (skill content + reusable tool functions).

### Optional dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
agent = []   # marker extra; agents consume comcheck_api.ai directly
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
from comcheck_api.ai import tools as cc_tools  # shared layer
from comcheck_api.ai.content import load_skill_reference

@tool
def update_project(project_id: str, project_data: dict) -> dict:
    """Update a saved COMcheck project."""
    return cc_tools.projects.update_project(project_id, project_data)

@tool
def start_simulation(project_id: str) -> dict:
    """Start a compliance simulation. Costs the user's COMcheck quota."""
    return cc_tools.simulation.start(project_id)


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

Every line of substantive COMcheck logic is reused from
`comcheck_api.ai`, not duplicated.

## Why this shape is the right one

### 1. The Skill folder serves multiple audiences from one location

| Audience | How they use it |
|---|---|
| Local Claude users (PyPI install) | Copy the bundled folder to `~/.claude/skills/` |
| The hosted agent | LangGraph's retrieval node loads it via `comcheck_api.ai.content` |
| Repo-root `CLAUDE.md` | Auto-loads in Claude Code sessions opened against this repo |

If it lived in the agent repo, the local Claude users would have to
reach across repos to get it.

### 2. Tools are versioned with the SDK

When a new operation class is added to `comcheck_api`, the tool
functions in `ai/tools/` update in the same commit. Anyone who bumps
their `comcheck_api` dependency gets the new tools automatically — no
separate release dance.

### 3. The agent repo stays small and focused

It becomes a **deployment + orchestration repo**: LangGraph topology,
infra-as-code, system prompts, eval harness. Not a place where
COMcheck domain logic lives. That separation is healthy — it lets
infra changes happen without touching domain logic and vice versa.

## What goes where: ownership map

| Lives in **`comcheckweb-api-python`** (this repo) | Lives in **agent repo** |
|---|---|
| `comcheck_api/` SDK | LangGraph graph & state definitions |
| `comcheck_api/ai/skill/` (canonical content) | System prompt + prompt iteration |
| `comcheck_api/ai/tools/` (reusable tool functions) | Tool *registration* with LangGraph (`@tool` wrappers) |
| `comcheck_api/ai/content.py` (Skill loader) | Skill *retrieval node* (which docs to load when) |
| `comcheck_api/ai/CLAUDE.md` (generated) | Approval policy nodes |
| Public docs (`docs_site/`) | A2A endpoint code |
| **Unit tests** for tools and content loading | AgentCore deployment config |
|   | Eval harness for chat-style flows |
|   | Internal runbooks |

Two repos, two clear missions:

- **This repo**: "Here is the COMcheck domain SDK and the canonical
  content/tools that go with it."
- **Agent repo**: "Here is the deployed product that uses that SDK
  to provide a hosted chatbot."

## The one discipline rule

**`comcheck_api/ai/tools/` should know nothing about LangGraph.** It
exposes plain Python functions. The agent repo is responsible for
adapting them into `@tool`-decorated LangChain tools.

This keeps the package framework-agnostic. If we ever decide to also
ship a Claude Agent SDK demo, or build a CrewAI integration, or a
CLI agent, they all consume the same plain-Python tool surface and
adapt it to their own framework. No agent-framework dependency leaks
into the SDK package.

```python
# GOOD — framework-agnostic
# comcheck_api/ai/tools/projects.py
def update_project(project_id: str, project_data: dict, *, api_key=None) -> dict:
    """Update a saved COMcheck project."""
    ...

# BAD — leaks LangGraph into the SDK package
from langchain_core.tools import tool
@tool
def update_project(project_id: str, project_data: dict) -> dict:
    ...
```

A `langchain_core` import inside `comcheck_api` would force every
PyPI consumer to pull in LangChain's transitive dependencies. Don't
do it. Adapters belong in the consumer, not the library.

## Phased path forward

### Step 1 — Land the AI substrate in this repo ✅ done

Tracked in [10-approach-2-implementation-plan.md](10-approach-2-implementation-plan.md).
What landed:

- `ai/skill/` content authored (SKILL.md, 3 reference docs, 2
  examples, validate_code.py).
- `ai/tools/` reusable Python functions (lookup, projects,
  simulation, validation).
- `ai/content.py` Skill loader using `importlib.resources`.
- `comcheck_api/ai/CLAUDE.md` generated from `SKILL.md`.

Pending here: unit tests, CI sync check.

### Step 2 — Stand up the agent repo (next, in the agent repo)

- `pyproject.toml` declares `comcheck_api[agent]` dependency.
- LangGraph graph defined.
- Tool wrappers around `comcheck_api.ai.tools.*`.
- Skill retrieval node using `comcheck_api.ai.content`.
- A2A endpoint.
- AgentCore deployment.

The agent repo can start *immediately* — every helper it needs from
this package is already there.

### Step 3 — Iterate together

When the agent reveals a missing tool ("the LLM keeps wanting to
query simulations by date range"), the missing tool gets added to
`comcheck_api/ai/tools/` in this repo, a new version is released,
and the agent's dependency is bumped. Single source of truth pays
off.

## Summary

- **One package** (`comcheck_api`), **two install profiles**
  (SDK only or `[agent]`).
- **One canonical content folder** (`comcheck_api/ai/skill/`) used by
  Claude users and the hosted agent.
- **Strict layering**: SDK ← `ai/`. Never the reverse.
- **Framework-agnostic tool functions** in `ai/tools/` — LangGraph
  adapters live in the agent repo.
- **The agent repo is small and focused**: orchestration, prompts,
  deployment. All COMcheck domain logic stays here.
