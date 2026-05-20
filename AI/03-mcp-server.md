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

## Distribution

Add to `pyproject.toml`:

```toml
[project.scripts]
comcheck-mcp = "comcheck_api.mcp.server:main"

[project.optional-dependencies]
mcp = ["mcp>=1.0"]
```

Users install with:

```bash
pip install comcheck_api[mcp]
```

Then they add to `~/.claude.json` (Claude Code),
`claude_desktop_config.json`, or whatever their host uses:

```json
{
  "mcpServers": {
    "comcheck": {
      "command": "comcheck-mcp"
    }
  }
}
```

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

## Security note

`validate_code` runs untrusted (model-generated) Python. Run it in a
subprocess with a short timeout, no network, and a mocked HTTP layer.
For a public package, this matters — don't `exec()` in-process.
