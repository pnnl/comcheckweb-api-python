"""AI-facing surface for the comcheck_api package.

This subpackage provides three things consumed by AI clients and
agents (local Claude Code and external agent repos like the LangGraph
hosted chatbot):

- ``ai.skill/`` — canonical Skill folder (SKILL.md + reference docs
  + examples + scripts). Hand-authored.
- ``ai.content`` — runtime loader for the Skill files.
- ``ai.tools`` — framework-agnostic Python functions wrapping the
  SDK. No LangGraph or Claude Agent SDK imports.

The dependency direction is one-way: ``ai/`` depends on the SDK, but
the SDK never depends on ``ai/``.
"""

from comcheck_api.ai import content, tools

__all__ = ["content", "tools"]
