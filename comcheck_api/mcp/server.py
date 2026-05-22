"""Stdio MCP server entry point.

Exposes the framework-agnostic ``ai/tools/`` functions as MCP tools,
the Skill reference Markdown files as MCP resources, and the SKILL.md
body as an MCP prompt.

Imports of the ``mcp`` package are deferred to ``main()`` so that
users who installed ``comcheck_api`` without the ``[mcp]`` extra can
still import the rest of the package cleanly.
"""

from __future__ import annotations

import sys


def main() -> None:
    """Console-script entry point for ``comcheck-mcp``."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        sys.stderr.write(
            "comcheck-mcp requires the [mcp] extra.\n"
            "Install with: pip install 'comcheck_api[mcp]'\n"
        )
        sys.exit(1)

    from comcheck_api.ai import content
    from comcheck_api.ai.tools import lookup, projects, simulation, validation

    mcp = FastMCP("comcheck")

    # --- Read-only lookup tools ---

    @mcp.tool()
    def list_operations() -> list[dict]:
        """List public functions in the project operation modules."""
        return lookup.list_operations()

    @mcp.tool()
    def lookup_type(name: str) -> dict:
        """Return field-level schema for a Pydantic model in comcheck_api.types."""
        return lookup.lookup_type(name)

    @mcp.tool()
    def search_docs(query: str, k: int = 5) -> list[dict]:
        """Search Skill content (reference + examples) for ``query``."""
        return lookup.search_docs(query, k=k)

    # --- Project tools (write tools — agent should require approval) ---

    @mcp.tool()
    def list_projects() -> list[dict]:
        """List the user's COMcheck projects."""
        return projects.list_projects()

    @mcp.tool()
    def get_project(project_id: str) -> dict | None:
        """Fetch a single COMcheck project by ID."""
        return projects.get_project(project_id)

    @mcp.tool()
    def update_project(project_id: str, project_data: dict) -> dict | None:
        """Update a COMcheck project. Requires user approval."""
        return projects.update_project(project_id, project_data)

    # --- Simulation tools ---

    @mcp.tool()
    def start_simulation(project_id: str) -> dict:
        """Start a compliance simulation for a saved project. Costs quota."""
        return simulation.start_simulation(project_id)

    @mcp.tool()
    def get_simulation_status(session_id: str) -> dict:
        """Get the current status of a simulation session."""
        return simulation.get_status(session_id)

    @mcp.tool()
    def get_simulation_result(session_id: str) -> dict:
        """Get the result metrics of a completed simulation session."""
        return simulation.get_result(session_id)

    # --- Validation tools ---

    @mcp.tool()
    def validate_code(code: str, run: bool = False) -> dict:
        """Compile-check + import-check generated Python; optionally sandboxed-run."""
        return validation.validate_code(code, run=run)

    @mcp.tool()
    def dry_run_project(project_json: dict) -> dict:
        """Validate project JSON against the ComBuilding Pydantic model."""
        return validation.dry_run_project(project_json)

    # --- Resources (Skill content as fetchable URIs) ---

    @mcp.resource("comcheck://skill/SKILL.md")
    def skill_body() -> str:
        return content.read_skill_body()

    for ref_name in content.list_references():

        def _make(_name: str):
            @mcp.resource(f"comcheck://skill/reference/{_name}")
            def _resource() -> str:
                return content.read_reference(_name)

            return _resource

        _make(ref_name)

    for ex_name in content.list_examples():

        def _make_ex(_name: str):
            @mcp.resource(f"comcheck://skill/examples/{_name}")
            def _resource() -> str:
                return content.read_example(_name)

            return _resource

        _make_ex(ex_name)

    # --- Prompts (the Skill body as connection-time guidance) ---

    @mcp.prompt()
    def use_comcheck() -> str:
        """How to use the comcheck_api package correctly."""
        return content.read_skill_body_only()

    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
