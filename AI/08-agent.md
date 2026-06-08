# Building an Agent on Top of `comcheck_api`

The Skill makes *user-driven* AI tools smarter about the SDK. An
**agent** is a step beyond: given an objective, it runs autonomously —
looping on its own, calling tools, deciding next steps — until the
goal is met.

Concretely, what this enables:

> *"Build me a 5,000 sqft office project in Seattle using ASHRAE
> 90.1-2019, run a simulation, and tell me whether it passes."*

…and the agent independently updates the project, fills in
envelope/lighting/mechanical, kicks off the simulation, polls until
done, fetches the result, and reports back. The user watches but
doesn't babysit each step.

## How an agent uses what we ship

This repo provides two things an agent can consume directly:

1. **The Skill content** under `comcheck_api/ai/skill/` — domain
   instructions, reference docs, and worked examples that teach an
   LLM how to drive the SDK correctly.
2. **The framework-agnostic tool functions** under
   `comcheck_api/ai/tools/` — plain Python functions an agent can
   wrap as LangGraph nodes, Claude Agent SDK tools, or any other
   framework's tool format.

The hosted-chatbot agent for the COMcheck website is a **LangGraph +
A2A + AgentCore** service in a separate repository. It depends on
this package and consumes both the Skill content and the tool
functions. See [09-supporting-agent-repo.md](09-supporting-agent-repo.md)
for the two-repo architecture.

## Available tool surface

The framework-agnostic tools in
[`comcheck_api/ai/tools/`](../comcheck_api/ai/tools/) cover:

| Module | What it does |
|---|---|
| `lookup` | `list_operations()`, `lookup_type(name)`, `search_docs(query)` |
| `projects` | `list_projects()`, `get_project(id)`, `update_project(id, data)` |
| `simulation` | `start_simulation(project_id)`, `get_status(session_id)`, `get_result(session_id)` |
| `validation` | `validate_code(code)`, `dry_run_project(json)` |

(There's no `create_project` / `delete_project` — the underlying
`COMcheckClient` doesn't expose them; projects are created/deleted
via the COMcheck website UI.)

## Engineering considerations for any agent

These apply regardless of which framework wraps the tools.

### 1. API key handling

Real projects = real impact on the user's PNNL account. The agent
needs the user's `COM_API_KEY` from the env. Never log it. Never
include it in tool results. Make sure the agent's reasoning text
doesn't accidentally print it back to the user.

### 2. Approval gates for destructive actions

- `update_project` — usually safe; confirm on shared projects.
- `start_simulation` — confirm because it costs quota and queue time.

The agent framework should provide per-tool approval hooks. Wire them
up; don't trust the model to self-restrict.

### 3. State — the polling loop

A simulation takes minutes. The agent needs to either (a) block and
poll, or (b) submit, return a session ID, and let the user re-invoke
later with "check on session X". For an interactive chat, blocking
is fine — but cap the wait (~5 min) to avoid hanging the session.

### 4. Idempotency

What if the agent crashes mid-build? The simplest version is to log
every action with timestamps and ids, and provide a way to resume.

### 5. Cost transparency

Every agent turn = LLM tokens. A long conversation can be hundreds of
thousands of tokens. The agent should report token usage at the end,
or stream a running counter. Users hate surprise bills.

### 6. Domain prompt quality

The agent's quality is dominated by the system prompt: how it scopes
the project, when it asks for clarification, how it interprets
ambiguous building specs (e.g., "open office" — is that 200 sqft of
"Office: Open" plus a corridor, or is it the entire 5000 sqft?).
Energy modeling has a thousand small assumptions; the agent will be
only as smart as the prompt teaches it to be. Plan to iterate.

## Where this fits in the roadmap

| Stage | Status | What it enables |
|---|---|---|
| Skill content | ✅ done | Claude users get domain-aware help via progressive disclosure |
| Framework-agnostic tool functions | ✅ done | Any agent framework can wrap them |
| Hosted chatbot for the COMcheck website | ⏳ in agent repo | LangGraph + A2A + AgentCore. See [09-supporting-agent-repo.md](09-supporting-agent-repo.md). |

Skill content and tool functions are shipped from this repo. The
hosted chatbot lives in the separate agent repo and consumes
`comcheck_api.ai.skill/` + `comcheck_api.ai.tools/` as a dependency.
