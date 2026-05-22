# Supporting an External Agent Repo

The agent (LangGraph + A2A + AWS AgentCore — see [08-agent.md](08-agent.md))
will live in a **separate repository**. This `comcheckweb-api-python`
package becomes a **dependency** of the agent repo. The question this
doc answers: *what should this package expose so the agent repo has
an easy time consuming it?*

**Decision: Approach 2** — expand this package to ship SDK + Skill +
reusable tool functions + MCP server, with strict internal layering.

## What "support agent development" means

Three things the agent repo will need from this package:

1. **The SDK itself** — `import comcheck_api` (already done; that's
   the package's job).
2. **Knowledge content** — the Skill folder (`SKILL.md`,
   `reference/*.md`, `examples/*.py`) so the agent can load it as
   Skill-style progressive-disclosure context.
3. **Tools** — Python functions the agent's LangGraph nodes can call
   (`create_project`, `lookup_type`, `validate_code`, etc.).

Each of these has a cleanest place to live, and the choice has
implications.

## The three approaches considered

### Approach 1: Keep this package SDK-only, ship knowledge separately

Status quo on the package. The agent repo:

- `pip install comcheck_api` → gets the SDK.
- Maintains its own copy of the Skill folder.
- Defines its own LangGraph tool wrappers around `comcheck_api`.

**Pros**: SDK package stays minimal, no AI-specific concerns leak in.

**Cons**: The Skill folder is the canonical content source we agreed
on. Forking it into the agent repo means **two places to update**
every time the SDK changes. Drift is guaranteed within months.

**Verdict**: Don't do this. Defeats the "single source of truth"
pattern.

### Approach 2 (CHOSEN): Expand this package — SDK + Skill + tools + MCP

Everything we've discussed for the public PyPI release stays here.
The agent repo:

- `pip install comcheck_api[mcp,agent]` → gets the SDK, the Skill
  folder, and reusable tool/knowledge helpers.
- Imports `comcheck_api.ai.skill` as a path; loads
  progressive-disclosure content.
- Imports `comcheck_api.ai.tools` for ready-made tool functions;
  wraps them in LangGraph nodes.

```python
# in the agent repo
from comcheck_api.ai.skill import skill_path, load_reference
from comcheck_api.ai.tools import create_project, start_simulation, lookup_type

# LangGraph-side
@tool
def cc_create_project(spec: dict) -> dict:
    return create_project(spec)
```

**Pros**:

- One source of truth for SDK + content + tool surface.
- Agent repo is tiny — just LangGraph orchestration, prompts,
  deployment. The substantive COMcheck logic lives where it belongs.
- Same package serves the public PyPI release and the hosted agent.
- When you ship a new version of `comcheck_api`, both consumers get
  the update via standard dependency bumps.

**Cons**:

- The package grows beyond "just an SDK" — adds `ai/`, `mcp/`
  subpackages.
- Optional dependencies need careful handling so users who only want
  the SDK don't pull in MCP/agent extras.

**Verdict**: This is the right shape, with discipline (see below).

### Approach 3: Split into two packages

Two PyPI packages: `comcheck-api` (SDK) + `comcheck-api-ai` (knowledge
+ tools). The SDK package stays pure. A second package depends on it
and bundles Skill + tools + MCP server.

The agent repo: `pip install comcheck-api-ai` → transitively gets the
SDK.

**Pros**:

- Cleaner separation of concerns.
- Engineers who only want the SDK never see AI plumbing.

**Cons**:

- Two packages to release in lockstep.
- More distribution overhead.
- Harder to keep tools in sync with SDK changes (every refactor of
  `comcheck_api` requires a coordinated release of
  `comcheck-api-ai`).
- Premature for a project at this scale.

**Verdict**: Reasonable for a mature ecosystem. Premature now.
Consider in v3+ if the AI surface grows substantially.

## The chosen design: Approach 2, structured carefully

**Keep one package, with optional extras and a clear internal
layering.**

### Layered structure inside `comcheck_api`

```
comcheck_api/
  __init__.py                    # SDK surface (existing)
  client/                        # SDK (existing)
  project_operations/            # SDK (existing)
  types/                         # SDK (existing)
  ...

  ai/                            # ★ new top-level subpackage
    __init__.py
    skill/                       # canonical content (Markdown + examples)
      SKILL.md
      reference/
      examples/
      scripts/
    content.py                   # Python helpers to load Skill files
    tools/                       # ready-made tool functions
      __init__.py
      lookup.py                  # lookup_type, list_operations, search_docs
      projects.py                # create/update/delete (write tools)
      simulation.py              # start, status, result
      validation.py              # validate_code, dry_run_project
    CLAUDE.md                    # generated from SKILL.md

  mcp/                           # MCP server (depends on ai/)
    server.py
    setup.py
    clients.py

  cli.py                         # comcheck-api CLI
```

### The dependency direction is strict and one-way

```
mcp/ ──▶ ai/tools/ ──▶ comcheck_api SDK (existing)
           ▲
           │
       ai/skill/ (data files, no code dep)
```

`ai/` depends on the SDK. `mcp/` depends on `ai/`. The SDK never
depends on `ai/` or `mcp/`. This means:

- A user who runs `pip install comcheck_api` gets the SDK and
  nothing else costly.
- A user who runs `pip install comcheck_api[mcp]` gets MCP plumbing.
- The agent repo runs `pip install comcheck_api[agent]` and gets the
  SDK + `ai/` (skill content + reusable tool functions) — but NOT
  MCP plumbing, since the agent doesn't need it.

### Optional dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
mcp = ["mcp>=1.0"]
agent = []   # no extra deps; just signals intent and pulls in the ai/ surface
agent-langgraph = ["langchain-core>=0.3"]   # adapters if we choose to ship them
all = ["comcheck_api[mcp,agent]"]
```

### Shipping the Skill folder in the wheel

`pyproject.toml` already needs to include the data files:

```toml
[tool.hatch.build.targets.wheel]
packages = ["comcheck_api"]
include = ["comcheck_api/ai/skill/**/*"]
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
def create_project(spec: dict) -> dict:
    """Create a new COMcheck project. Returns project ID."""
    return cc_tools.projects.create_project(spec)

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

### 1. The Skill folder serves three audiences from one location

| Audience | How they use it |
|---|---|
| Local Claude users (PyPI install) | `comcheck-api install-skill` copies it to `~/.claude/skills/` |
| Local IDE users via MCP | The MCP server reads it for tool resources/prompts |
| The hosted agent | LangGraph's retrieval node loads it via `comcheck_api.ai.content` |

If it lived in the agent repo, the first two audiences would have to
reach across repos to get it. If it lived only in the SDK package,
the agent repo would have to bundle a copy.

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

### 4. Public PyPI users and the hosted agent get parity

The same tool implementations that power the hosted chatbot also
power Claude Code users running locally with `comcheck-mcp`. Same
code path, same behavior, same bug fixes. No "the hosted version
works but the local version is broken" surprises.

## What goes where: ownership map

| Lives in **`comcheckweb-api-python`** (this repo) | Lives in **agent repo** |
|---|---|
| `comcheck_api/` SDK | LangGraph graph & state definitions |
| `comcheck_api/ai/skill/` (canonical content) | System prompt + prompt iteration |
| `comcheck_api/ai/tools/` (reusable tool functions) | Tool *registration* with LangGraph (`@tool` wrappers) |
| `comcheck_api/ai/content.py` (Skill loader) | Skill *retrieval node* (which docs to load when) |
| `comcheck_api/mcp/` (MCP server) | Approval policy nodes |
| `comcheck-api` CLI (`init`, `setup-mcp`) | A2A endpoint code |
| `llms.txt` / `llms-full.txt` build pipeline | AgentCore deployment config |
| `CLAUDE.md` / `cursor.rules` | Eval harness for chat-style flows |
| Public docs (`docs_site/`) | Internal runbooks |
| **Unit tests** for tools and content loading | **Integration tests** for the full graph |

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
- `mcp/` server with 11 tools, Skill resources, and a connection
  prompt.
- `CLAUDE.md`, `llms.txt`, `llms-full.txt`, `.cursor/rules/` generated
  from the same content via `scripts/build_ai_assets.py`.
- `comcheck-api` CLI: `setup-mcp`, `install-skill`, `init`,
  `setup-ai`.

Pending here: unit tests, MCP smoke test, CI sync check.

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
and the agent's dependency is bumped. Local MCP users get the same
new tool automatically. Single source of truth pays off.

## Summary

- **One package** (`comcheck_api`), **three optional install profiles**
  (SDK only, `[mcp]`, `[agent]`).
- **One canonical content folder** (`comcheck_api/ai/skill/`) used by
  three surfaces (PyPI install, MCP server, hosted agent).
- **Strict layering**: SDK ← `ai/` ← `mcp/`. Never the reverse.
- **Framework-agnostic tool functions** in `ai/tools/` — LangGraph
  adapters live in the agent repo.
- **The agent repo is small and focused**: orchestration, prompts,
  deployment. All COMcheck domain logic stays here.
