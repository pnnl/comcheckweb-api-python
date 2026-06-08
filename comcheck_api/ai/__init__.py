"""AI-facing surface for the comcheck_api package.

Consumed by AI clients and agents (local Claude Code and external
agent repos like the LangGraph hosted chatbot):

- ``ai.skill/`` — canonical Skill folder (SKILL.md + reference docs
  + examples + scripts). Hand-authored.
- ``ai.content`` — runtime loader for the Skill files.

Introspection and validation helpers live on the SDK itself
(``comcheck_api.list_operations``, ``comcheck_api.lookup_type``,
``comcheck_api.validate_project``) — agents call them directly.
"""

from comcheck_api.ai import content

__all__ = ["content"]
