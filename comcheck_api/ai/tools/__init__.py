"""Framework-agnostic tool functions wrapping the comcheck_api SDK.

Plain Python functions, hand-typed inputs/outputs, no LangGraph or
Claude Agent SDK imports. Consumers (an external LangGraph agent,
etc.) adapt these into their own framework.
"""

from comcheck_api.ai.tools import lookup, projects, simulation, validation

__all__ = ["lookup", "projects", "simulation", "validation"]
