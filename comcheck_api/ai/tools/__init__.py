"""Framework-agnostic tool functions wrapping the comcheck_api SDK.

Plain Python functions, hand-typed inputs/outputs, no LangGraph /
MCP / Claude Agent SDK imports. Consumers (the MCP server, an
external LangGraph agent, etc.) adapt these into their own framework.

Phase 1 ships skeletons that import cleanly. Real implementations
land in Phase 2.
"""

from comcheck_api.ai.tools import lookup, projects, simulation, validation

__all__ = ["lookup", "projects", "simulation", "validation"]
