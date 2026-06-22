from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Callable, Optional
import uuid

import pytest

from comcheck_api.client import COMcheckClient
from comcheck_api.types.core_types import *
from comcheck_api.utilities.project_utilities import get_id_from_component
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.defaults import (
    get_default_building_area_template,
)
from tests.project_operation_tests.assertions.components import (
    assert_component_added,
    assert_component_removed,
    assert_component_updated,
)

# Committed sample project used to build the offline `project` fixture so the
# operation tests run without a live API call. Live round-trips against the
# real server are opt-in via `--integration` (see `maybe_apply_and_reload`).
SAMPLE_PROJECT_PATH = Path(__file__).parent.parent / "test_data" / "sample_project.json"


@pytest.fixture(scope="session")
def client() -> COMcheckClient:
    """Client for the operation tests.

    Without ``--integration`` the tests never hit the network, so a real API
    key is optional; we set it when present so ``--integration`` runs can reach
    the live server.
    """
    c = COMcheckClient()
    key = os.getenv("COM_API_KEY")
    if key:
        c.set_api_key(key)
    return c


@pytest.fixture(scope="session")
def project(client: COMcheckClient) -> ComBuilding:
    """Load the project model from the committed sample JSON (offline)."""
    data = json.loads(SAMPLE_PROJECT_PATH.read_text())
    project = client._parse_data(data, "python")
    assert project is not None
    return project


@pytest.fixture
def maybe_apply_and_reload(request, monkeypatch):
    if not request.config.getoption("--integration"):
        monkeypatch.setattr(
            "tests.project_operation_tests.conftest.apply_and_reload",
            lambda client, project: project,
        )
        monkeypatch.setattr(
            "tests.project_operation_tests.conftest.project",
            lambda client, project: project,
        )


@dataclass
class ComponentOperationConfig:
    name: str
    path: str
    default_factory: Callable[[], Any]
    add_component_to_project: Callable[..., Any]
    update_component_in_project: Callable[[Any, str, dict], Any]
    remove_component_from_project: Callable[[Any, str], Any]
    updates: dict = field(
        default_factory=lambda: {"description": f"Description {str(uuid.uuid4())}"}
    )


@pytest.fixture(scope="session")
def building_area_key(client: COMcheckClient, project: ComBuilding) -> str:
    existing = project.get_by_path("lighting.wholeBldgUse", [])
    if existing:
        return existing[-1].key

    new_area = get_default_building_area_template()
    updated = apply_and_reload(
        client,
        project_building_area_operations.add_building_area_to_project(
            project, new_area
        ),
    )
    object.__setattr__(project, "lighting", updated.lighting)
    return new_area.key


def apply_and_reload(client: COMcheckClient, project: ComBuilding) -> ComBuilding:
    project_id = getattr(project, "id", None)
    assert project_id, "No project id found"
    result = client.update_project(project_id, project)
    assert isinstance(result, ComBuilding)
    return result


def get_parent_and_child_list(config: ComponentOperationConfig, project: ComBuilding):
    parent_path, child_name = config.path.rsplit(".", 1)

    parent = project.get_by_path(parent_path)
    assert parent, f"No parent assembly at '{parent_path}'"

    child_list = parent.get_by_path(child_name)
    assert isinstance(
        child_list, list
    ), f"Expected child at '{config.path}' to be a list"

    return parent, child_list


def run_flat_assembly_lifecycle(
    *,
    client: COMcheckClient,
    project: ComBuilding,
    config: ComponentOperationConfig,
    building_area_key: Optional[str] = None,
) -> None:
    default_component = config.default_factory()

    # ADD
    if building_area_key:
        project = apply_and_reload(
            client,
            config.add_component_to_project(
                project,
                building_area_key,
                default_component,
            ),
        )
    else:
        project = apply_and_reload(
            client,
            config.add_component_to_project(
                project,
                default_component,
            ),
        )

    target_id = get_id_from_component(default_component)
    assert target_id is not None

    assert_component_added(
        project=project,
        path=config.path,
        component_id=target_id,
        component_name=config.name,
    )

    # UPDATE
    project = apply_and_reload(
        client,
        config.update_component_in_project(
            project,
            target_id,
            config.updates,
        ),
    )
    assert_component_updated(
        project=project,
        path=config.path,
        updates=config.updates,
        component_id=target_id,
        component_name=config.name,
    )

    # REMOVE
    project = apply_and_reload(
        client,
        config.remove_component_from_project(
            project,
            target_id,
        ),
    )
    assert_component_removed(
        project=project,
        path=config.path,
        component_id=target_id,
        component_name=config.name,
    )


def run_nested_assembly_lifecycle(
    *,
    client: COMcheckClient,
    project: ComBuilding,
    config: ComponentOperationConfig,
    building_area_key: str,
) -> None:
    default_component = config.default_factory()
    parent, _ = get_parent_and_child_list(config, project)
    parent.bldgUseKey = building_area_key

    # ADD
    project = apply_and_reload(
        client,
        config.add_component_to_project(
            project,
            building_area_key,
            default_component,
            parent,
        ),
    )

    target_id = get_id_from_component(default_component)
    assert target_id is not None

    assert_component_added(
        project=project,
        path=config.path,
        component_id=target_id,
        component_name=config.name,
    )

    # UPDATE
    project = apply_and_reload(
        client,
        config.update_component_in_project(
            project,
            target_id,
            config.updates,
        ),
    )

    assert_component_updated(
        project=project,
        path=config.path,
        updates=config.updates,
        component_id=target_id,
        component_name=config.name,
    )

    # REMOVE
    project = apply_and_reload(
        client,
        config.remove_component_from_project(
            project,
            target_id,
        ),
    )

    assert_component_removed(
        project=project,
        path=config.path,
        component_id=target_id,
        component_name=config.name,
    )
