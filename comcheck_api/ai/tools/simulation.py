"""Simulation tools: start, poll, fetch.

``start_simulation`` consumes the user's COMcheck quota — agents
should require user confirmation before calling. Status and result
fetches are read-only.

These wrappers operate on a *saved* project (i.e., one fetched via
:func:`comcheck_api.ai.tools.projects.get_project`). They return plain
dicts.
"""

from __future__ import annotations

import os
from typing import Any

from comcheck_api import COMcheckClient
from comcheck_api.types.core_types import ComBuilding


def _client(api_key: str | None) -> COMcheckClient:
    key = api_key or os.environ.get("COM_API_KEY")
    if not key:
        raise ValueError(
            "No API key provided. Pass api_key=... or set COM_API_KEY in the environment."
        )
    return COMcheckClient(api_key=key)


def start_simulation(
    project_id: str,
    *,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Kick off a simulation for the saved project at ``project_id``.

    Returns ``{"session_id": "..."}``. Use :func:`get_status` to poll
    and :func:`get_result` to fetch the final metrics.
    """
    with _client(api_key) as client:
        project = client.get_project(project_id, mode="python")
        if project is None:
            raise ValueError(f"No project found with id {project_id!r}")
        session_id = client.start_run_simulation(project)
        return {"session_id": session_id}


def start_simulation_from_data(
    project_data: dict[str, Any] | ComBuilding,
    *,
    project_id: int | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Start a simulation from in-memory project data.

    If ``project_id`` is supplied the project is saved/updated first
    (matches the underlying SDK behavior).
    """
    project = (
        ComBuilding.model_validate(project_data)
        if isinstance(project_data, dict)
        else project_data
    )
    with _client(api_key) as client:
        session_id = client.start_run_simulation(project, project_id=project_id)
        return {"session_id": session_id}


def get_status(session_id: str, *, api_key: str | None = None) -> dict[str, Any]:
    """Return the current status of a simulation session."""
    with _client(api_key) as client:
        return client.get_simulation_status(session_id)


def get_result(session_id: str, *, api_key: str | None = None) -> dict[str, Any]:
    """Return the result of a completed simulation session."""
    with _client(api_key) as client:
        return client.get_simulation_result(session_id)
