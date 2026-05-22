# AI Approaches for the COMcheck API Python Client

This folder captures the discussion and planning for adding an AI-powered
layer on top of the `comcheck_api` PyPI package. The goal is to let users
generate Python code that builds COMcheck projects and runs simulations
through natural-language prompts, and to support an external agent repo
that powers a hosted chatbot on the COMcheck website.

## Implementation status

| Component | Status | Source |
|---|---|---|
| Skill content | ✅ shipped | [`comcheck_api/ai/skill/`](../comcheck_api/ai/skill/) |
| Skill loader (`importlib.resources`) | ✅ shipped | [`comcheck_api/ai/content.py`](../comcheck_api/ai/content.py) |
| Framework-agnostic tool functions | ✅ shipped | [`comcheck_api/ai/tools/`](../comcheck_api/ai/tools/) |
| MCP server (11 tools + resources + prompt) | ✅ shipped | [`comcheck_api/mcp/server.py`](../comcheck_api/mcp/server.py) |
| `comcheck-api` CLI (`setup-mcp`, `init`, etc.) | ✅ shipped | [`comcheck_api/cli.py`](../comcheck_api/cli.py) |
| Build pipeline (llms.txt, CLAUDE.md, cursor.rules) | ✅ shipped | [`scripts/build_ai_assets.py`](../scripts/build_ai_assets.py) |
| `[mcp]` and `[agent]` extras + console scripts | ✅ shipped | [`pyproject.toml`](../pyproject.toml) |
| Unit tests + MCP smoke test in CI | ⏳ pending | — |
| LangGraph + A2A + AgentCore agent | ⏳ in agent repo | (separate repository) |

For the concrete plan that was actually built, see
[10-approach-2-implementation-plan.md](10-approach-2-implementation-plan.md).
For the broader option landscape and earlier exploration, see the docs
below in numerical order.

## Contents

- [01-options-overview.md](01-options-overview.md) — Full landscape of
  ways to deliver SDK knowledge to AI tools (10 options across 4
  categories).
- [02-llms-txt.md](02-llms-txt.md) — Deep dive on the `llms.txt`
  convention: structure, generation, and distribution.
- [03-mcp-server.md](03-mcp-server.md) — Deep dive on bundling an MCP
  server in the PyPI package: tool surface, distribution, and
  security.
- [04-claude-skill.md](04-claude-skill.md) — Deep dive on packaging the
  SDK as a Claude Skill: structure, distribution, and tradeoffs.
- [05-comparison.md](05-comparison.md) — Side-by-side comparison of
  `llms.txt`, Claude Skill, and MCP Server, with recommendations and
  token-usage analysis.
- [06-rag-and-s3-vectors.md](06-rag-and-s3-vectors.md) — Earlier
  discussion on RAG-based architectures and S3 Vectors as a store
  (superseded by the chosen architecture).
- [07-implementation-plan.md](07-implementation-plan.md) — Original
  unified plan for shipping `llms.txt` + Skill + MCP server from one
  source of content. Phase status updated to reflect what landed; see
  doc 10 for the concrete plan.
- [08-agent.md](08-agent.md) — Agent options landscape. Option A
  (Claude Code + MCP server) shipped via the MCP server here; the
  hosted-chatbot path moved to a separate agent repo (see doc 09).
- [09-supporting-agent-repo.md](09-supporting-agent-repo.md) — Chosen
  approach for supporting an external agent repo (LangGraph + A2A +
  AgentCore): expand this package with `ai/` and `mcp/` subpackages,
  shared Skill folder + framework-agnostic tool functions, ownership
  map between the two repos.
- [10-approach-2-implementation-plan.md](10-approach-2-implementation-plan.md)
  — Concrete implementation plan with current phase status: scope,
  layout, dependency rules, what landed in Phases 1–5, and what
  remains (tests + CI).

## Quick start

```bash
# From this repo, with the package in editable install:
pip install -e '.[mcp]'

# Generate llms.txt, CLAUDE.md, etc. from the Skill source:
python scripts/build_ai_assets.py

# Set up everything for a Claude / Cursor user:
comcheck-api setup-ai

# Or run subcommands individually:
comcheck-api setup-mcp        # register comcheck-mcp with detected AI clients
comcheck-api install-skill    # copy the Skill into ~/.claude/skills/
comcheck-api init [path]      # drop CLAUDE.md and .cursor/rules into a project
```
