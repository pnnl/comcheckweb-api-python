# AI Approaches for the COMcheck API Python Client

This folder captures the design and planning for the AI-facing layer
of the `comcheck_api` PyPI package. The shipped approach is:

- A **Claude Skill** under `comcheck_api/ai/skill/` — domain
  instructions, reference docs, and worked examples that teach an
  LLM how to drive the SDK.
- A **framework-agnostic tool surface** under
  `comcheck_api/ai/tools/` — plain Python functions an external
  agent (LangGraph, Claude Agent SDK, etc.) can wrap.
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
| Framework-agnostic tool functions | ✅ shipped | [`comcheck_api/ai/tools/`](../comcheck_api/ai/tools/) |
| `CLAUDE.md` (generated from `SKILL.md`) | ✅ shipped | [`comcheck_api/ai/CLAUDE.md`](../comcheck_api/ai/CLAUDE.md) |
| `[agent]` extra | ✅ shipped | [`pyproject.toml`](../pyproject.toml) |
| Unit tests + CI sync check | ⏳ pending | — |
| LangGraph + A2A + AgentCore agent | ⏳ in agent repo | (separate repository) |

## Contents

- [04-claude-skill.md](04-claude-skill.md) — Deep dive on packaging
  the SDK as a Claude Skill: structure, progressive-disclosure
  loading model, distribution.
- [08-agent.md](08-agent.md) — Agent landscape: how an external
  agent consumes the Skill content and the framework-agnostic tool
  functions, and the engineering considerations any agent must
  handle (API keys, approval gates, polling, idempotency, cost).
- [09-supporting-agent-repo.md](09-supporting-agent-repo.md) —
  Chosen architecture for supporting an external agent repo
  (LangGraph + A2A + AgentCore): expand this package with `ai/`,
  shared Skill folder + framework-agnostic tool functions,
  ownership map between the two repos.
- [10-approach-2-implementation-plan.md](10-approach-2-implementation-plan.md)
  — Concrete implementation plan with current phase status: scope,
  layout, dependency rules, what landed, and what remains
  (tests + CI).
