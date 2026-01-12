from dataclasses import dataclass
import os
from typing import Callable

import pytest

from comcheck_api.comcheck_client import COMcheckClient
from comcheck_api.utilities.common import export_to_json
from comcheck_api.types.core_types import *

@pytest.fixture(scope="session")
def api_key() -> str:
    key = os.getenv("COM_API_KEY")
    if not key:
        pytest.skip("COM_API_KEY is not set in environment variables.")
    return key


@pytest.fixture(scope="session")
def client(api_key: str) -> COMcheckClient:
    c = COMcheckClient()
    c.set_api_key(api_key)
    return c


@pytest.fixture(scope="session")
def project_id(client: COMcheckClient) -> str:
    projects = client.list_projects()
    if not projects or not (project_id := projects[0].get("_id")):
        pytest.skip("No projects found for integration tests.")
    # Export initial project state once
    test_project_json = client.get_project(project_id, mode="json")
    os.makedirs("testProjectJson", exist_ok=True)
    export_to_json(test_project_json, "testProjectJson/initialProject.json")
    return project_id

@pytest.fixture
def project(client: COMcheckClient, project_id: str):
    project = client.get_project(project_id)
    assert project is not None
    return project

@dataclass
class ComponentOperationConfig:
    name: str
    path: str
    default_factory: Callable[[], Any]
    add_component_to_project: Callable[[Any, str, Any], Any]
    update_component_in_project: Callable[[Any, str, dict], Any]
    remove_component_from_project: Callable[[Any, str, dict], Any]