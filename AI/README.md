# AI Approaches for the COMcheck API Python Client

This folder captures the design and planning for the AI-facing layer
of the `comcheck_api` PyPI package. The shipped approach is:

- A **Claude Skill** under `comcheck_api/ai/skill/` — domain
  instructions, reference docs, and worked examples that teach an
  LLM how to drive the SDK.
- **First-class introspection / validation helpers on the SDK
  itself** — `comcheck_api.list_operations()`,
  `comcheck_api.lookup_type()`, `comcheck_api.validate_project()`.
  Typed Pydantic returns; usable from any Python code (notebooks,
  IDE plugins, agents).
- A generated **`CLAUDE.md`** at `comcheck_api/ai/CLAUDE.md` and at
  the repo root — auto-loaded in Claude Code sessions.

The goal is a single canonical content source (the Skill folder)
that powers both local Claude users and an external hosted agent
repo, without leaking framework dependencies into the SDK.

## Implementation status

| Component | Status | Source |
|---|---|---|
| Skill content | ✅ shipped | [`comcheck_api/ai/skill/`](../comcheck_api/ai/skill/) |
| Skill loader (`importlib.resources`) | ✅ shipped | [`comcheck_api/ai/content.py`](../comcheck_api/ai/content.py) |
| `list_operations`, `lookup_type` (typed) | ✅ shipped | [`comcheck_api/introspection.py`](../comcheck_api/introspection.py) |
| `validate_project` (typed) | ✅ shipped | [`comcheck_api/validation.py`](../comcheck_api/validation.py) |
| `CLAUDE.md` (generated from `SKILL.md`) | ✅ shipped | [`comcheck_api/ai/CLAUDE.md`](../comcheck_api/ai/CLAUDE.md) |
| `[agent]` extra | ✅ shipped | [`pyproject.toml`](../pyproject.toml) |
| Unit tests + CI sync check | ⏳ pending | — |
| LangGraph + A2A + AgentCore agent | ⏳ in agent repo | (separate repository) |

## Contents

- [claude-skill.md](claude-skill.md) — Deep dive on packaging
  the SDK as a Claude Skill: structure, progressive-disclosure
  loading model, distribution.
- [agent.md](agent.md) — Agent landscape: how an external
  agent consumes the Skill content and the SDK's introspection /
  validation helpers, and the engineering considerations any agent
  must handle (API keys, approval gates, polling, idempotency,
  cost).
- [supporting-agent-repo.md](supporting-agent-repo.md) —
  Chosen architecture for supporting an external agent repo
  (LangGraph + A2A + AgentCore): expand this package with `ai/`
  (Skill content + loader), keep introspection/validation on the
  SDK proper, ownership map between the two repos.
- [implementation-plan.md](implementation-plan.md)
  — Concrete implementation plan with current phase status: scope,
  layout, dependency rules, what landed, and what remains
  (tests + CI).
