# Option 3: MCP Server Bundled in the PyPI Package

## What it actually is

MCP (Model Context Protocol) is Anthropic's open protocol — now also
adopted by OpenAI, Google, Cursor, Windsurf, Zed, and several IDEs —
for exposing **tools, resources, and prompts** to AI clients. A server
runs as a local subprocess (stdio transport) or HTTP service, and any
MCP-aware client can connect.

For an SDK like COMcheck, an MCP server transforms the package from
"code the model has to remember" into "tools the model can *call*" —
which is dramatically more reliable for code generation.

## You don't host the server — and here's why

The word "server" in MCP is misleading. It does **not** mean a machine
in a data center, listening on a port, accessible over the network.
It means **a Python program** that runs as a **local subprocess on the
user's own machine**, started by their AI client, only while they're
using it.

A more accurate name would be **"tool provider plugin"** or **"local
helper process."** It's closer to a Unix CLI tool than to a web
service.

### MCP transports

| Transport | Where the server runs | Who runs it | Hosting cost to you |
|---|---|---|---|
| **stdio** (default for SDK servers) | Local subprocess on the user's machine | The user's AI client (Claude Code, Cursor, etc.) launches it on session start | **Zero** |
| **HTTP/SSE** | A network-reachable URL | Whoever you point it at | You pay if you host |

For an SDK like `comcheck_api`, you want **stdio**. Always.

### What actually happens

The user does:

```bash
pip install comcheck_api[mcp]
```

That installs the package and registers a console script defined in
`pyproject.toml`:

```toml
[project.scripts]
comcheck-mcp = "comcheck_api.mcp.server:main"
```

After install, `comcheck-mcp` is just a CLI tool on the user's PATH,
exactly like `pip`, `pytest`, or `mypy`. It would start, sit waiting
for input on stdin, and do nothing useful (because there's no MCP
client talking to it). Hit Ctrl+C, it exits. Just like running
`pytest` with no arguments.

Then the user edits their MCP config (one time, in `~/.claude.json`
or wherever):

```json
{
  "mcpServers": {
    "comcheck": {
      "command": "comcheck-mcp"
    }
  }
}
```

Now, **every time the user opens Claude Code**, Claude Code:

1. Reads that config.
2. `fork/exec`s `comcheck-mcp` as a subprocess on the user's local
   machine.
3. Talks to it over stdin/stdout (the "stdio" transport).
4. Kills it when the session ends.

You don't have a server running anywhere. There is no service to keep
up. The "server" is just a Python script that lives in the user's
venv, runs for the duration of their session, and exits.

### Walking through the deployment chain

| Component | Where it lives | Who paid for it | Who runs it |
|---|---|---|---|
| `comcheck_api` package | PyPI (free) | PyPI / open source infra | n/a |
| User's Python interpreter | User's laptop | User | User |
| Installed `comcheck-mcp` script | User's laptop, in their venv | User | Claude Code, on demand |
| Running `comcheck-mcp` process | User's laptop | User's CPU/RAM | Claude Code |
| Claude Code itself | User's laptop | User's Claude subscription | User |
| LLM tokens | Anthropic | User's Claude subscription | n/a |

Notice: **your name does not appear in this table.** You contribute by
uploading a wheel to PyPI — once. From that point on, every cycle of
CPU, every byte of RAM, every token of LLM cost is paid by the user,
on the user's own hardware.

You can't be billed because there's no service of yours running. You
don't have a URL. You don't have a port open. You don't have an
account anywhere.

### The mental shift

Forget the word "server." Substitute "**a Python script that Claude
Code starts up when it needs help with COMcheck-related questions.**"

That script:

- Is part of your PyPI package.
- Runs on the user's machine.
- Talks to the user's local AI tool over pipes.
- Stops when the AI tool stops.
- Never touches infrastructure you own.

If `pip install pytest` doesn't require Pytest's authors to host
anything, `pip install comcheck_api[mcp]` doesn't require you to host
anything either. The architecture is identical.

### The case where you *would* host

MCP also supports an HTTP transport, which *is* a real network server.
That's for a *single shared MCP server* that many users connect to
over the internet — e.g., to gate access behind your own auth, or to
run something users can't run locally. **You don't want that for this
use case.** A Python SDK wrapper has nothing that needs to be central.

## Activation: who runs the command?

The user **does not** run `comcheck-mcp` themselves. Their AI client
runs it for them, automatically, every time they open the AI client.

### One-time setup (user does this once, ever)

1. `pip install comcheck_api[mcp]` — installs the `comcheck-mcp`
   script.
2. Edit MCP config (e.g., `~/.claude.json`) to add:
   ```json
   "comcheck": { "command": "comcheck-mcp" }
   ```

### Every session, automatically

1. User opens Claude Code (or Cursor, etc.).
2. The client reads its MCP config, sees `comcheck` is registered.
3. The client itself runs `comcheck-mcp` as a subprocess.
4. The MCP server is now active for the entire session.
5. User asks a COMcheck-related question → Claude calls a tool on the
   server.
6. User closes the client → the server subprocess is killed.

The user's mental model: **"After I set this up once, my AI just knows
how to use comcheck_api."**

### Comparison to the other auto-load options

| Option | When does it activate? |
|---|---|
| `llms.txt` | Only when the user (or an agent) explicitly fetches it |
| `CLAUDE.md` (project root) | Auto, every Claude session **in that project** |
| **MCP server** | **Auto, every AI session where it's registered — across all projects** |

MCP server beats `CLAUDE.md` on auto-activation in one important way:
`CLAUDE.md` requires the file in the *current project*. MCP is
**global to the user** — once configured, it activates everywhere
they use that AI client.

## The setup step: configuring `.claude.json`

Yes, the user has to configure their MCP client once. There's no way
around it today. Three ways, in order of friction:

### 1. Hand-edit JSON

Where the file lives depends on the client:

| Client | Config file |
|---|---|
| Claude Code (CLI) | `~/.claude.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS); equivalent on Windows/Linux |
| Cursor | `~/.cursor/mcp.json` or in-app settings |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Zed | `~/.config/zed/settings.json` (under `context_servers`) |

High friction; technical users only.

### 2. Use the client's CLI helper

Claude Code:

```bash
claude mcp add comcheck comcheck-mcp
```

Cursor, Windsurf, and others have similar UI/CLI affordances. Most
users today will use these helpers rather than hand-editing JSON.

### 3. Provide a setup script (recommended)

Add a console script to your package:

```bash
comcheck-api setup-mcp
```

…that detects which AI clients the user has installed, asks which to
register with, and writes the config for them. Eliminates almost all
the friction.

User's full setup becomes:

```bash
pip install comcheck_api[mcp]
comcheck-api setup-mcp
```

Two commands, no JSON editing, no config-file hunting.

## Building the `comcheck-api setup-mcp` flow

### `pyproject.toml` changes

```toml
[project.optional-dependencies]
mcp = ["mcp>=1.0"]

[project.scripts]
comcheck-mcp = "comcheck_api.mcp.server:main"
comcheck-api = "comcheck_api.cli:main"
```

The `[mcp]` extra keeps the MCP dependency out of the way for users
who only want the SDK — they get a lean install. Power users opt in.

### What `comcheck-api setup-mcp` does

Roughly 80–150 lines of Python:

1. **Detect installed clients.** Check for the existence of each
   config file:
   - `~/.claude.json` → Claude Code
   - `~/Library/Application Support/Claude/claude_desktop_config.json`
     → Claude Desktop
   - `~/.cursor/mcp.json` → Cursor
   - `~/.codeium/windsurf/mcp_config.json` → Windsurf

2. **Prompt for each detected client:**
   ```
   Found Claude Code. Register comcheck-mcp? [Y/n]
   Found Cursor.      Register comcheck-mcp? [Y/n]
   ```

3. **Update each config safely.** The critical word is *safely* —
   these files often have existing MCP servers. Don't overwrite. Read
   JSON, merge under `mcpServers.comcheck`, write back.

4. **Verify the script is on PATH.** `shutil.which("comcheck-mcp")`.

5. **Tell them what's next.** "Restart your AI client(s) to activate
   the comcheck tools."

A `--dry-run` flag that prints what would change saves a lot of
support tickets.

### Edge cases worth handling

| Case | What to do |
|---|---|
| Config file doesn't exist yet | Create it with just your entry — don't error |
| Config file has `comcheck` already registered | Ask before overwriting; offer `--force` |
| Config file is malformed JSON | Refuse to touch it; tell the user |
| User is in a venv but config is in `~` | Fine — but use the absolute `comcheck-mcp` path in the config so it works even when their venv isn't activated |
| Windows path separators | Use `pathlib.Path` throughout |
| User wants to uninstall | A `comcheck-api setup-mcp --remove` flag |

### The `command:` value matters

Subtle but important: when writing the config, **use the absolute
path** to `comcheck-mcp`, not the bare name:

```json
{
  "mcpServers": {
    "comcheck": {
      "command": "/Users/alice/.venv/bin/comcheck-mcp"
    }
  }
}
```

Why: Claude Code/Desktop launches the subprocess with their own
environment, which may not have the user's venv activated. The bare
`comcheck-mcp` won't be on PATH from Claude Code's perspective.
Looking up `shutil.which("comcheck-mcp")` at setup time and writing
the absolute path solves this. **It's the #1 reason MCP servers
"don't work" for users.**

### Sketch of the CLI structure

```
comcheck_api/
  cli.py                 # the comcheck-api entry point
  mcp/
    __init__.py
    server.py            # the comcheck-mcp entry point (FastMCP server)
    setup.py             # the setup_mcp() function
    clients.py           # per-client config-file logic
```

`comcheck-api` becomes the general CLI surface — `setup-mcp` is the
first subcommand, but it can grow later (`comcheck-api init` for the
`CLAUDE.md` copy, `comcheck-api version`, etc.).

#### What `clients.py` does (per-client config-file logic)

This file knows the **boring, fiddly details of every supported AI
client**. Each client gets its own small adapter.

```python
# comcheck_api/mcp/clients.py
from dataclasses import dataclass
from pathlib import Path
import json, platform

@dataclass
class MCPClient:
    """Describes how one AI client stores its MCP config."""
    name: str                  # human-readable: "Claude Code"
    config_path: Path          # where the config file lives
    config_section: tuple      # JSON path: ("mcpServers",) or ("context_servers",)

def all_clients() -> list[MCPClient]:
    """Return every supported client with its config-file path."""
    home = Path.home()
    system = platform.system()
    return [
        MCPClient(
            name="Claude Code",
            config_path=home / ".claude.json",
            config_section=("mcpServers",),
        ),
        MCPClient(
            name="Claude Desktop",
            config_path=_claude_desktop_path(home, system),
            config_section=("mcpServers",),
        ),
        MCPClient(
            name="Cursor",
            config_path=home / ".cursor" / "mcp.json",
            config_section=("mcpServers",),
        ),
        MCPClient(
            name="Windsurf",
            config_path=home / ".codeium" / "windsurf" / "mcp_config.json",
            config_section=("mcpServers",),
        ),
        MCPClient(
            name="Zed",
            config_path=home / ".config" / "zed" / "settings.json",
            config_section=("context_servers",),
        ),
    ]

def detect_installed() -> list[MCPClient]:
    return [c for c in all_clients() if c.config_path.exists()]

def read_config(client: MCPClient) -> dict: ...
def write_config(client: MCPClient, config: dict) -> None: ...
def add_server(client: MCPClient, name: str, command: str) -> dict: ...
def remove_server(client: MCPClient, name: str) -> dict: ...
```

What this gives you:

- **One source of truth** for each client's quirks. If Cursor changes
  its config path next year, you fix one line in this file.
- **Easily testable** — each function takes a path and JSON, no UI
  involved. Unit tests are trivial.
- **Easy to extend** — adding "Continue" or "Aider" is a new entry in
  `all_clients()`, not a new branch in your CLI code.

#### What `setup.py` does (the `setup_mcp()` orchestration)

This is the **user-facing flow**. It uses `clients.py` as a library
and adds the interaction layer on top.

> Note: this file is named `setup.py` because it implements the
> `setup-mcp` subcommand. Despite the name, it has **nothing to do
> with the legacy Python `setup.py` packaging file** — `pyproject.toml`
> is the build config. Could be renamed `setup_mcp.py` to avoid
> confusion.

```python
# comcheck_api/mcp/setup.py
import shutil
from comcheck_api.mcp import clients

def setup_mcp(
    server_name: str = "comcheck",
    dry_run: bool = False,
    force: bool = False,
    yes: bool = False,
) -> int:
    """Register comcheck-mcp with each detected AI client."""

    # 1. Find the absolute path to the comcheck-mcp executable.
    command = shutil.which("comcheck-mcp")
    if command is None:
        print("ERROR: 'comcheck-mcp' not found on PATH.")
        return 1

    # 2. Detect installed clients.
    detected = clients.detect_installed()
    if not detected:
        print("No MCP-aware AI clients detected.")
        return 1

    # 3. For each, ask + write.
    for client in detected:
        if not _confirm(f"Register {server_name} with {client.name}?", yes):
            continue
        existing = clients.read_config(client)
        section = existing.get(client.config_section[0], {})
        if server_name in section and not force:
            if not _confirm(f"  already registered. Overwrite?", yes):
                continue
        new_config = clients.add_server(client, server_name, command)
        if dry_run:
            print(f"  [dry-run] would write {client.config_path}")
        else:
            clients.write_config(client, new_config)
            print(f"  → wrote {client.config_path}")

    print("\nDone. Restart your AI client(s) to activate.")
    return 0
```

What this gives you:

- **All the user-facing prompts and flags live here**, not scattered.
- **All the JSON-mangling lives in `clients.py`**, where it's testable
  in isolation.
- **`cli.py` is a thin wrapper** that just parses arguments and calls
  `setup_mcp(...)`.

#### Call graph

```
comcheck-api setup-mcp        [user runs]
  ↓
cli.py main()                 [parses args]
  ↓
mcp/setup.py setup_mcp()      [user interaction + orchestration]
  ↓
mcp/clients.py *              [config-file mechanics]
```

#### Why split rather than one file?

For v1 you could put everything in one ~150-line file and it'd be
fine. The split pays off when:

- **Testing**: `clients.py` is pure functions over paths and dicts —
  100% testable without mocking `input()`. `setup.py`'s flow can be
  tested with a fake stdin.
- **Adding a new client**: a contributor only needs to touch
  `clients.py`. They don't need to understand the whole CLI flow.
- **Reusing the logic**: a year from now you might add
  `comcheck-api remove-mcp`, `comcheck-api status`, or a one-shot
  `comcheck-api setup-ai`. They'll all want to call into `clients.py`
  without duplicating code.

| File | What it knows | What it doesn't know |
|---|---|---|
| `clients.py` | Where each AI client stores its MCP config; how to read/merge/write that JSON | Whether the user said yes; whether `--dry-run` is set; how to print messages |
| `setup.py` | The user-facing flow: detect, prompt, confirm, write, report | The OS-specific path of Claude Desktop's config; whether Zed uses `context_servers` |
| `cli.py` | Argument parsing | Anything substantive |

### What the user experience looks like

```
$ pip install comcheck_api[mcp]
Successfully installed comcheck_api-1.x.x mcp-1.x.x

$ comcheck-api setup-mcp
COMcheck MCP setup
Detected AI clients:
  ✓ Claude Code      (~/.claude.json)
  ✓ Cursor           (~/.cursor/mcp.json)
  ✗ Claude Desktop   (not installed)
  ✗ Windsurf         (not installed)

Register comcheck-mcp with Claude Code? [Y/n] y
  → Wrote ~/.claude.json
Register comcheck-mcp with Cursor? [Y/n] y
  → Wrote ~/.cursor/mcp.json

Done. Restart your AI client(s) to activate the comcheck tools.
```

About as clean as PyPI distribution allows today.

## Tool surface (as shipped)

The MCP server exposes 11 tools, plus Skill content as MCP resources
and a connection-time prompt.

### Discovery / lookup (read-only)

- `list_operations()` → enumerates public functions in
  `project_building_area_operations` and
  `project_envelope_operations` via `inspect`. Returns 26 functions
  with signatures and docstring summaries. Always in sync with the
  installed SDK.
- `lookup_type(name: str)` → reflects a Pydantic model from
  `comcheck_api.types`. Returns
  `{kind: "model", fields: [{name, type, required, default, description}, ...]}`
  for `BaseModel` subclasses, or
  `{kind: "enum", members: [...]}` for StrEnum classes.
- `search_docs(query: str, k: int = 5)` → BM25 ranking over Skill
  content (paragraph-chunked). Returns scored snippets.

### Project tools (write tools — host should gate)

- `list_projects()` → returns the user's saved projects.
- `get_project(project_id)` → fetches one saved project as a JSON
  dict.
- `update_project(project_id, project_data)` → mutates an existing
  saved project. Confirm before calling.

The underlying SDK does **not** expose `create_project` or
`delete_project` — projects are created/deleted via the COMcheck
website UI; the SDK reads/updates already-saved projects only.

### Simulation tools

- `start_simulation(project_id)` → kicks off a real compliance
  simulation against the user's COMcheck quota. Confirm before
  calling. Returns `{"session_id": "..."}`.
- `get_simulation_status(session_id)` → polls a session's status.
- `get_simulation_result(session_id)` → fetches result metrics
  (`performanceRating`, `proposedBpf`, `baselineBpf`, etc.).

### Validation (the killer feature)

- `validate_code(code, run=False)` → static syntax + import check by
  default; with `run=True` runs the user's draft in a sandboxed
  subprocess (network blocked, COMcheck HTTP service mocked, 5-second
  timeout). Returns structured errors. **This is what makes the
  difference vs. plain RAG** — the model gets a real feedback loop
  and self-corrects.
- `dry_run_project(project_json)` → validates JSON against the
  `ComBuilding` Pydantic model. Returns Pydantic errors as
  structured `[{loc, msg, type}]`.

### Resources and prompts

- `comcheck://skill/SKILL.md` resource — full SKILL.md text.
- `comcheck://skill/reference/<name>` resources — each reference doc.
- `comcheck://skill/examples/<name>` resources — each example file.
- `use_comcheck` prompt — SKILL.md body (frontmatter stripped) for
  hosts that surface MCP prompts at connection time.

## Implementation

See [`comcheck_api/mcp/server.py`](../comcheck_api/mcp/server.py) for
the actual server. Sketch:

```python
from mcp.server.fastmcp import FastMCP
from comcheck_api.ai import content
from comcheck_api.ai.tools import lookup, projects, simulation, validation

mcp = FastMCP("comcheck")

@mcp.tool()
def lookup_type(name: str) -> dict:
    return lookup.lookup_type(name)

@mcp.tool()
def validate_code(code: str, run: bool = False) -> dict:
    return validation.validate_code(code, run=run)

# ... other tools, resources, prompts ...

def main():
    mcp.run()
```

The server lazy-imports `mcp` so users without the `[mcp]` extra can
still import `comcheck_api` cleanly.

## Realistic tradeoffs

- **Quality lift**: the biggest of any option here. With
  `validate_code` in the loop, the model can iteratively fix its own
  output — pass-rates on a code-gen eval typically jump from "decent"
  to "near-perfect."
- **Effort**: ~1 week for a solid v1. Mostly time spent on the
  validation sandbox (need to mock the network client cleanly so
  executing user-generated code is safe).
- **Surface area**: maintain a tool API and the docs corpus, but they
  piggyback on what already exists in the package.
- **Reach**: works in Claude Desktop, Claude Code, Cursor, Windsurf,
  Zed, Continue, OpenAI's MCP support, and anything else that joins
  the protocol — which is now most major AI coding tools.

## What "running a local MCP server" really means

The phrase "local MCP server" sounds bigger than what actually happens.
It does **not** mean a long-running daemon, a system service, or
something the user starts and stops. It means: **a Python process
exists for as long as the user's AI client is open.** That process is
a child of the AI client, not a standalone service.

```
Claude Code (parent process)
└── comcheck-mcp (child process, started automatically)
```

When the user closes Claude Code:

```
Claude Code → exits → kills its children → comcheck-mcp exits
```

The lifetime of the MCP server is **exactly the lifetime of the AI
client**. Open Claude Code → comcheck-mcp starts. Close Claude Code →
comcheck-mcp ends. Nothing is left running.

### What it looks like on the user's machine

If the user runs `ps` while Claude Code is open:

```
$ ps -ef | grep comcheck
zhuy571   45821 12345  python /Users/zhuy571/.venv/bin/comcheck-mcp
```

One Python process. Idle most of the time (no CPU usage when nothing
is happening). Talks to Claude Code over a pair of pipes
(stdin/stdout). Wakes up only when Claude calls a tool, then goes
back to sleep.

### Resource consumption

| Resource | Typical usage |
|---|---|
| Memory | ~30–60 MB (mostly Python interpreter + your package import) |
| CPU | ~0% idle, brief spikes when a tool is called |
| Network | None — talks to AI client over pipes, not over the network |
| Ports | None — stdio transport doesn't use ports |
| Disk | None at runtime |

It's lighter than a single browser tab.

### "But isn't 'always running' a security risk?"

The natural worry: "Is something always running on my machine? Can it
be exploited?"

What's actually happening:

- **Not always running.** Only while the AI client is open. Quit the
  AI client, the server quits too.
- **No network exposure.** It listens on stdin from one specific
  parent process. There's no port, no socket, no way for anything
  else to talk to it. The phrase "local server" makes people think
  "listening on localhost:8080" — that's *not* what's happening here.
  There is no server that can be reached with `curl`.
- **Sandboxed by stdio.** Even a malicious tool scanning the system
  would find no socket to attack. The two processes communicate over
  a private file descriptor pair created at fork time.

The closest mental model: a **plugin loaded by Claude Code that
happens to live in a separate Python process for isolation**. Not a
server in any traditional sense.

### Why a separate process at all (vs. just `import`-ing the package)?

Reasonable question. Three reasons MCP uses subprocesses:

1. **Language independence.** MCP servers can be Python, Node, Go,
   Rust, anything. Claude Code is written in JavaScript/TypeScript;
   it can't `import` a Python package directly. Stdio + JSON-RPC is
   the lingua franca.
2. **Isolation.** A crash in your MCP server doesn't take down the AI
   client. A `validate_code` tool running untrusted Python lives in
   its own process tree.
3. **Permissions.** The user can grant/revoke per-server tool access
   without affecting the AI client itself.

So "local MCP server" is really "Python plugin running as a
subprocess for isolation reasons." The word "server" is doing too
much heavy lifting in the name.

### Lifecycle in VS Code (Claude Code extension)

In VS Code with the Claude Code extension, the lifecycle ties to the
**extension's session**, not the chat panel visibility:

| User action | `comcheck-mcp` process? |
|---|---|
| Opens VS Code | Not yet running |
| Activates Claude Code extension (opens chat panel) | **Started** |
| Hides the chat panel but keeps VS Code open | **Still running** |
| Switches to a different VS Code workspace | Depends — extension may restart, killing and respawning |
| Closes VS Code | Killed |
| Reloads window (`Cmd+Shift+P → Reload Window`) | Killed and respawned |

So if the user opens VS Code in the morning, activates Claude Code,
and doesn't close VS Code all day, `comcheck-mcp` is alive all day.

#### Why this is fine in practice

1. **Idle ~all the time.** The process is blocked on `read()` from
   stdin, waiting for the next message from Claude Code. CPU 0%.
   Memory stays at its initial ~30–60 MB (no allocations between tool
   calls, no leaks). Compare to other things VS Code keeps running:
   TypeScript LSP often uses 500 MB+, Copilot, Docker, etc.
   `comcheck-mcp` is one of the lightest things in your process tree.
2. **Scoped to one VS Code window.** Three windows = three
   `comcheck-mcp` processes, each ~30–60 MB. Even a power user with
   five windows is at maybe 150–300 MB total for *all* MCP servers
   across *all* their workspaces.
3. **Dies cleanly.** When VS Code exits or reloads, the extension
   exits, and any subprocess it spawned is killed via signal
   propagation. No orphan, no zombie, no leftover service.

#### Real concerns to watch for

| Concern | Mitigation |
|---|---|
| Memory if user has 10+ MCP servers | Keep imports lean; lazy-import heavy deps inside tool functions, not at module top-level. A lean server starts in <100 ms and uses <50 MB. |
| Stale state after `pip install --upgrade comcheck_api` | The running server is still the *old* version until the user reloads the VS Code window. Document it: "After upgrading, reload your VS Code window." |
| Sleeping laptops | Process is suspended/resumed cleanly. No issue for a stateless server. |

#### What's *not* happening

To put the worry to rest, here's what an "always-running" process
would do that this one doesn't:

- ❌ Listen on a network port → no, stdio only
- ❌ Accept connections from other processes → no, only from its
  parent
- ❌ Run scheduled tasks or polling → no, purely reactive
- ❌ Phone home or send telemetry → no (you control the code)
- ❌ Auto-update itself → no, just a Python file in a venv
- ❌ Survive after the AI client closes → no, killed with parent

It's a **reactive subprocess**, not a "service."

### A user's day, concretely

```
09:00  Opens VS Code, activates Claude Code extension
       → comcheck-mcp starts (~50 MB RAM, 0% CPU)

10:30  Asks Claude: "build me an envelope assembly"
       → Claude calls lookup_type("EnvelopeAssembly")
       → comcheck-mcp wakes, returns 300 tokens of schema (~5 ms work)
       → goes back to idle

12:00  Lunch — VS Code stays open, chat panel hidden
       → comcheck-mcp still running, ~50 MB RAM, 0% CPU

14:00  Asks: "validate this code"
       → comcheck-mcp spawns sandboxed subprocess, returns errors
       → goes back to idle

18:00  Closes VS Code
       → comcheck-mcp is killed
```

Total CPU time consumed by `comcheck-mcp` over a 9-hour day: probably
under 5 seconds. Total memory: 50 MB the whole time. Invisible unless
the user looks for it.

## Operational responsibility

There's one operational thing you do own: **package quality**. If
`comcheck-mcp` crashes on startup, every user's AI session shows a
broken MCP server. So the package should have:

- A startup smoke test in CI.
- Clean error messages if the user's Python env is misconfigured.
- A version check / compatibility matrix as the SDK evolves.

That's standard PyPI package hygiene, not "hosting." No servers, no
SLAs, no oncall.

## Security note

`validate_code` runs untrusted (model-generated) Python. Run it in a
subprocess with a short timeout, no network, and a mocked HTTP layer.
For a public package, this matters — don't `exec()` in-process.
