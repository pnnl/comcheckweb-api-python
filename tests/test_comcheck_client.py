"""Live tests for COMcheckClient.

These hit the real COMcheck Web API and need a valid ``COM_API_KEY``. They
skip (rather than fail) when no key is set or the key is rejected, so the
offline suite stays green; provide a valid key to exercise them.
"""

import os

import pytest
from dotenv import load_dotenv

from comcheck_api import (
    project_building_area_operations as ba_ops,
    project_interior_lighting_operations as il_ops,
)
from comcheck_api.client import COMcheckClient
from comcheck_api.defaults import (
    get_default_building_area_template,
    get_default_interior_space_template,
    get_default_project_template,
)
from comcheck_api.exceptions import COMCheckHTTPError
from comcheck_api.types.core_types import ActivityTypeOptions, EnergyCodeOptions

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def client():
    """Fixture to create and configure COMcheckClient."""
    api_key = os.getenv("COM_API_KEY")
    if not api_key:
        pytest.skip("COM_API_KEY is not set; skipping live client tests.")

    client = COMcheckClient()
    client.set_api_key(api_key)
    return client


def test_fetch_project_list(client: COMcheckClient):
    """Test fetching the project list."""
    try:
        project_list = client.list_projects()
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise
    assert isinstance(project_list, list)


def test_fetch_single_project(client: COMcheckClient):
    """Test fetching a single project if any exist."""
    try:
        project_list = client.list_projects()
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise

    if project_list and project_list[0].get("_id"):
        project = client.get_project(project_list[0]["_id"])
        assert project is not None
    else:
        # If no projects exist, just pass the test
        assert True


def _project_with_interior_spaces():
    """Default project with one building area holding two interior spaces."""
    project = get_default_project_template()
    project.control.code = EnergyCodeOptions.CEZ_90_1_2022

    area = get_default_building_area_template()
    area.areaDescription = "Office Area"
    project = ba_ops.add_building_area_to_project(project, area)

    first = get_default_interior_space_template()
    first.areaDescription = "Open Office"
    first.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
    first.floorArea = 2000.0
    project = il_ops.add_interior_space_to_project(project, area.key, first)

    second = get_default_interior_space_template()
    second.areaDescription = "Conference Room"
    second.activityType = ActivityTypeOptions.ACTIVITY_COMMON_CONFERENCE_HALL
    second.floorArea = 500.0
    project = il_ops.add_interior_space_to_project(project, area.key, second)
    return project


def test_calculate_interior_space_allowed_wattage(client: COMcheckClient):
    """Test calculating allowed wattage for a single InteriorSpace in a project."""
    project = _project_with_interior_spaces()

    try:
        result = client.calculate_interior_space_allowed_wattage(
            project, "Open Office"
        )
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise
    assert isinstance(result, dict)
    assert "spaceAllowedWattage" in result


def test_calculate_interior_spaces_allowed_wattage(client: COMcheckClient):
    """Test calculating allowed wattage for every InteriorSpace in a project."""
    project = _project_with_interior_spaces()

    try:
        result = client.calculate_interior_spaces_allowed_wattage(project)
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise
    assert isinstance(result, dict)
    assert "Open Office" in result
    assert "Conference Room" in result


def test_area_for_renewable(client: COMcheckClient):
    """Test calculating renewable areas for a default project."""
    project = get_default_project_template()
    project.control.code = EnergyCodeOptions.CEZ_IECC2021

    try:
        result = client.area_for_renewable(project)
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise
    assert result is project


def test_renewable_capacity(client: COMcheckClient):
    """Test calculating renewable capacity for a default project."""
    project = get_default_project_template()
    project.control.code = EnergyCodeOptions.CEZ_IECC2021

    try:
        result = client.renewable_capacity(project)
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise
    assert result is project
