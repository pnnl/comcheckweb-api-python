# AI Approaches for the COMcheck API Python Client

This folder captures the discussion and planning for adding an AI-powered
layer on top of the `comcheck_api` PyPI package. The goal is to let users
generate Python code that builds COMcheck projects and runs simulations
through natural-language prompts.

## Contents

- [01-options-overview.md](01-options-overview.md) — Full landscape of ways
  to deliver SDK knowledge to AI tools (10 options across 4 categories).
- [02-llms-txt.md](02-llms-txt.md) — Deep dive on the `llms.txt`
  convention: structure, generation, and distribution.
- [03-mcp-server.md](03-mcp-server.md) — Deep dive on bundling an MCP
  server in the PyPI package: tool surface, distribution, and security.
- [04-claude-skill.md](04-claude-skill.md) — Deep dive on packaging the
  SDK as a Claude Skill: structure, distribution, and tradeoffs.
- [05-comparison.md](05-comparison.md) — Side-by-side comparison of
  `llms.txt`, Claude Skill, and MCP Server, with recommendations and
  token-usage analysis.
- [06-rag-and-s3-vectors.md](06-rag-and-s3-vectors.md) — Earlier
  discussion on RAG-based architectures and S3 Vectors as a store.
- [07-implementation-plan.md](07-implementation-plan.md) — Unified plan
  that ships all three (`llms.txt`, Skill, MCP server) from a single
  source of content, with phased build steps, user on-ramps, and
  benefits.
