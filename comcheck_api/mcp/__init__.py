"""Local stdio MCP server for the comcheck_api package.

Lazy-imports the MCP SDK so users without the ``[mcp]`` extra installed
can still import ``comcheck_api`` cleanly. The server entry point is
``comcheck_api.mcp.server:main``.
"""
