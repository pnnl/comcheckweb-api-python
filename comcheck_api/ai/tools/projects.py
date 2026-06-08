"""Project CRUD tools.

Thin wrappers around :class:`comcheck_api.COMcheckClient`. Returns plain
dicts (not Pydantic models) so downstream agents can serialize results
without additional adapters.

Write tools (``update_project``) should be gated behind user approval
in any agent that uses them — they mutate state on the user's COMcheck
account.
"""

from __future__ import annotations

import os
from typing import Any

from comcheck_api import COMcheckClient
from comcheck_api.types.core_types import ComBuilding


def _client(api_key: str | None) -> COMcheckClient:
    """Build a ``COMcheckClient`` using the explicit key or ``COM_API_KEY``."""
    key = api_key or os.environ.get("COM_API_KEY")
    if not key:
        raise ValueError(
            "No API key provided. Pass api_key=... or set COM_API_KEY in the environment."
        )
    return COMcheckClient(api_key=key)


def list_projects(*, api_key: str | None = None) -> list[dict[str, Any]]:
    """List the user's projects."""
    with _client(api_key) as client:
        return client.list_projects()


def get_project(
    project_id: str, *, api_key: str | None = None
) -> dict[str, Any] | None:
    """Fetch a single project by ID, returning the raw JSON dict.

    Returns ``None`` if the project does not exist.
    """
    with _client(api_key) as client:
        return client.get_project(project_id, mode="json")


def update_project(
    project_id: str,
    project_data: dict[str, Any] | ComBuilding,
    *,
    api_key: str | None = None,
) -> dict[str, Any] | None:
    """Update a project on the COMcheck server.

    ``project_data`` may be either a dict (will be validated into a
    ``ComBuilding``) or a ``ComBuilding`` instance.
    """
    if isinstance(project_data, dict):
        project_model = ComBuilding.model_validate(project_data)
    else:
        project_model = project_data

    with _client(api_key) as client:
        return client.update_project(project_id, project_model, mode="json")
