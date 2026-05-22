# Building an Agent on Top of `comcheck_api`

The earlier options ([llms.txt](02-llms-txt.md), [Skill](04-claude-skill.md),
[MCP server](03-mcp-server.md)) make *user-driven* AI tools smarter
about the SDK. An **agent** is a step beyond: given an objective, it
runs autonomously — looping on its own, calling tools, deciding next
steps — until the goal is met.

Concretely, what this enables:

> *"Build me a 5,000 sqft office project in Seattle using ASHRAE
> 90.1-2019, run a simulation, and tell me whether it passes."*

…and the agent independently creates the project, fills in
envelope/lighting/mechanical, kicks off the simulation, polls until
done, fetches the result, and reports back. The user watches but
doesn't babysit each step.

## How an agent relates to what we already designed

The MCP server gets you ~80% of an agent for free.

Claude Code is, itself, an agent. So is Cursor's agent mode, Windsurf,
Cline, etc. They run a loop: **think → call tool → observe → think →
call tool → … until done**. Give them rich tools via your MCP server,
and you've already got a working agent.

So before building anything new, ask: *what does Claude Code with
`comcheck-mcp` already do that you wish were better?* Often the
missing piece is just **write tools** (create_project, run_simulation)
that we'd intentionally gated as opt-in.

That gives three architectures, lightest to heaviest.

## Option A: Use Claude Code (or any agent-mode AI client) + your MCP server ✅ shipped

**The lightest path** — and the one this repo has actually shipped.
The MCP server exposes the following write/state-mutating tools
alongside the read-only ones:

| Tool | What it does |
|---|---|
| `list_projects()` | Lists the user's saved projects |
| `get_project(project_id)` | Fetches one project as JSON |
| `update_project(project_id, project_data)` | Updates a saved project |
| `start_simulation(project_id)` | Kicks off a real simulation |
| `get_simulation_status(session_id)` | Polls a simulation's status |
| `get_simulation_result(session_id)` | Fetches result metrics |

(There's no `create_project` / `delete_project` — the underlying
`COMcheckClient` doesn't expose them; projects are
created/deleted via the COMcheck website UI.)

Once exposed via MCP, the user opens Claude Code and says "update
my project ABC123 with two new south-facing windows and run a sim" —
Claude orchestrates the flow using these tools, asking for
confirmation before destructive operations (per Claude Code's
built-in approval system).

### Pros

- ✅ Already shipped via the MCP server — no further code needed.
- User's existing AI client is the agent — no new UI to learn.
- Approval/safety is handled by the AI client (Claude Code asks before
  writes).
- Works in Cursor, Windsurf, Zed too.

### Cons

- The user has to be in an agent-mode AI client.
- The "agent" is general-purpose — it'll happily help with non-COMcheck
  tasks too. Not a focused product.

## Option B: Build a focused agent on Claude Agent SDK (deprecated)

**Status: not being built in this repo.** A standalone in-package
agent (Claude Agent SDK wrapper) was the original Option B, but the
hosted agent for the COMcheck website is now a LangGraph + A2A +
AgentCore service in a **separate repo** that consumes this package
as a dependency. See
[09-supporting-agent-repo.md](09-supporting-agent-repo.md) for the
two-repo architecture.

The sketch below remains for reference:

A standalone Python agent that lives in your package:

```bash
comcheck-api agent "build a 5000 sqft office in Seattle"
```

Built on Anthropic's [Claude Agent SDK](https://docs.claude.com/api/agent-sdk)
— the same loop logic that powers Claude Code, packaged for embedding
in your own application. You provide:

- **System prompt** — domain expertise: "You are a COMcheck
  assistant. Your job is to help users build code-compliant building
  projects. Use the tools to create projects, run simulations, and
  interpret results."
- **Tools** — defined as Python functions, decorated, calling
  `comcheck_api` directly (or your MCP server, since Agent SDK
  supports MCP tools natively).
- **Approval policy** — which tools auto-run, which require user
  confirmation.
- **Conversation loop** — the SDK runs it for you.

```python
# comcheck_api/agent/main.py (sketch)
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(
    system_prompt=open("agent/SYSTEM.md").read(),
    mcp_servers={"comcheck": {"command": "comcheck-mcp"}},
    permission_mode="acceptEdits",  # auto-allow safe tools, prompt on writes
)

async def run(objective: str):
    async with ClaudeSDKClient(options) as agent:
        await agent.query(objective)
        async for msg in agent.receive_response():
            print(msg)
```

Wired up as a CLI: `comcheck-api agent "build me X"`.

### Pros

- Focused product — branded, scoped, predictable behavior.
- User doesn't need an external AI client; they need an Anthropic API
  key.
- You control the system prompt, tool surface, approval policy.
- Same `comcheck-mcp` tools serve both Claude Code users and the
  standalone agent.
- Can ship as part of the PyPI package.

### Cons

- Now you depend on `claude-agent-sdk` and an Anthropic API key.
- User pays per-token directly to Anthropic (vs. via their
  Claude/Cursor subscription).
- More code to maintain (~200–500 lines beyond the MCP server).

### Effort

~3–5 days on top of the MCP server work.

### Module layout

```
comcheck_api/
  agent/
    __init__.py
    main.py              # ClaudeSDKClient + ClaudeAgentOptions wiring
    SYSTEM.md            # the system prompt (loaded at runtime)
    permissions.py       # per-tool approval policy
    cli.py               # comcheck-api agent <objective> entry point
```

`main.py` is the runtime — async generator that yields messages.
`SYSTEM.md` is editable as Markdown so prompt iteration doesn't
require code changes. `permissions.py` declares which tools are
auto-allowed vs. which require confirmation.

## Option C: Hosted agent service

A SaaS where users sign in, type natural-language goals, and the
agent runs on your servers using your API keys to LLMs.

Included for completeness, but **don't recommend for v1** unless
there's a specific reason to centralize (shared project libraries,
team collaboration, monetization). Cost, complexity, ops burden,
billing — all the downsides of [Option 7 from the original
landscape](01-options-overview.md#7-web-app--saas), plus the burden
of executing real COMcheck API calls on behalf of users (their API
keys, your liability).

## Recommendation

**Option A is shipped.** The hosted chatbot path goes to the LangGraph
agent repo (see [09](09-supporting-agent-repo.md)), not Option B.

In other words: **the MCP server is the substrate. Option A is "let
any agent use the substrate." The hosted agent repo is "ship our own
agent on top of the substrate."** Same substrate either way.

## What the UX looks like (Option A — using Claude Code)

The user starts from a project they already created on the COMcheck
website. The agent updates it and runs a sim:

```
User (in Claude Code):
  My project ID is abc123. Add south- and west-facing walls of 1500
  sqft each, plus a 200 sqft south window, then run a simulation
  and tell me if it passes.

Claude:
  Fetching the existing project...
  → calls get_project("abc123")

  I'll add the walls and window using the operation modules,
  then push the update.
  → calls update_project("abc123", {... merged project data ...})

  Running simulation...
  → calls start_simulation("abc123")
  Session: sess_xyz. Polling...
  → calls get_simulation_status("sess_xyz")  [×3 until complete]
  → calls get_simulation_result("sess_xyz")

  Result: PASS with 3.2% margin.
  Want me to walk through where the margin comes from?
```

Same outcome. Different shell.

## Engineering considerations

These apply to either option, and they're the *real* engineering, not
the agent loop itself.

### 1. API key handling

Real projects = real impact on the user's PNNL account. The agent
needs the user's `COM_API_KEY` from the env. Never log it. Never
include it in tool results. Make sure the agent's reasoning text
doesn't accidentally print it back to the user.

### 2. Approval gates for destructive actions

- `create_project` / `update_project` — usually safe.
- `delete_project` — always confirm.
- `start_simulation` — confirm because it costs quota and queue time.
- `update_project` on a *shared* project — confirm because other
  people may depend on it.

Claude Agent SDK has built-in `permission_mode` and per-tool approval
callbacks. Wire these up; don't trust the model to self-restrict.

### 3. State — the polling loop

A simulation takes minutes. The agent needs to either (a) block and
poll, or (b) submit, return a session ID, and let the user re-invoke
later with "check on session X". For an interactive CLI, blocking is
fine. For Claude Code, blocking is fine too — but cap the wait
(~5 min) to avoid hanging the session. Provide a separate
`comcheck-api status <session>` command for after-the-fact checks.

### 4. Idempotency

What if the agent crashes mid-build? It might have created project
`abc123` with envelope but no mechanical. The agent should be able to
*resume* — list its in-flight projects, see what's missing, complete
them. This is harder than it looks; the simplest version is to log
every action with timestamps and ids, and have a
`comcheck-api agent resume` command.

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
| MCP server with read tools | ✅ done | Claude Code helps users *write* SDK code |
| MCP server with simulation + project-mutation tools | ✅ done | Claude Code becomes a working agent (Option A) |
| Standalone in-package agent | ❌ deprecated | (Option B — superseded by the agent repo) |
| Hosted chatbot for the COMcheck website | ⏳ in agent repo | LangGraph + A2A + AgentCore. See [09-supporting-agent-repo.md](09-supporting-agent-repo.md). |

The first two stages are shipped from this repo. The hosted chatbot
lives in the separate agent repo and consumes this package's
`ai/tools/` + Skill content as a dependency.
