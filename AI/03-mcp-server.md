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

## Recommended tool surface

Group the tools by what the model needs at each stage of building a
project:

### Discovery / lookup

- `list_operations()` → returns the registered operation classes
  (`BuildingArea`, `Envelope`, ...) with one-line summaries.
- `lookup_type(name: str)` → returns a Pydantic model's fields, types,
  defaults, and constraints. Reads directly from the installed package
  via reflection — always in sync with the version installed.
- `search_docs(query: str, k: int = 5)` → keyword + (optional) vector
  search over the docs and examples. Even pure BM25 over the docs
  corpus is useful.

### Code generation helpers

- `get_skeleton(scenario: str)` → returns a vetted starter snippet for
  common scenarios ("envelope_only", "full_project_with_simulation",
  "lighting_only"). These are *gold-standard* templates you control.
- `get_example(name: str)` → returns the contents of a file from
  `examples/`.

### Validation (the killer feature)

- `validate_code(code: str)` → executes the user's draft in a
  subprocess against a *mock* `COMcheckClient`. Returns import errors,
  type errors, missing required fields. **This is what makes the
  difference vs. plain RAG** — the model gets a real feedback loop and
  self-corrects.
- `dry_run_project(project_json: dict)` → validates the JSON against
  the existing `jsonschema` definitions without hitting the real API.

### Live API (optional, opt-in)

- `start_simulation(project_json, api_key)` and
  `get_simulation_result(session_id, api_key)` → calls the real
  backend. Keep these gated behind an env var so casual sessions don't
  burn the user's quota.

## What the implementation looks like

The Anthropic `mcp` Python SDK is straightforward — a server is ~100
lines for a basic version:

```python
# comcheck_api/mcp/server.py  (sketch)
from mcp.server.fastmcp import FastMCP
from comcheck_api import COMcheckClient
from comcheck_api.types import ...  # for reflection

mcp = FastMCP("comcheck")

@mcp.tool()
def lookup_type(name: str) -> dict:
    """Return field-level schema for a Pydantic model in the SDK."""
    ...

@mcp.tool()
def validate_code(code: str) -> dict:
    """Run code in a sandbox with a mocked client; return errors."""
    ...

def main():
    mcp.run()
```

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

### Operational responsibility

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
