"""Offline tests for the allowed-wattage and u-value service and client methods.

Requests are served by an ``httpx.MockTransport``, so no API key or network
access is needed.
"""

import json

import httpx
import pytest

from comcheck_api import (
    COMcheckClient,
    project_building_area_operations as ba_ops,
    project_envelope_operations as env_ops,
    project_interior_lighting_operations as il_ops,
)
from comcheck_api.api.api_services import COMCheckApiService
from comcheck_api.defaults import (
    get_default_ag_wall_template,
    get_default_building_area_template,
    get_default_interior_space_template,
    get_default_project_template,
)
from comcheck_api.types.core_types import ActivityTypeOptions, EnergyCodeOptions


def _make_service(handler) -> COMCheckApiService:
    """Build a service whose HTTP client is backed by *handler*."""
    service = COMCheckApiService(api_key="test")
    service._client = httpx.Client(
        base_url=service.base_url,
        headers=service._prepare_headers(),
        transport=httpx.MockTransport(handler),
    )
    return service


def _make_client(handler) -> COMcheckClient:
    client = COMcheckClient(api_key="test")
    client._api_service = _make_service(handler)
    return client


def _ok(requests, data):
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"message": "ok", "data": data})

    return handler


@pytest.fixture
def requests():
    return []


@pytest.fixture
def project():
    project = get_default_project_template()
    project.control.code = EnergyCodeOptions.CEZ_IECC2021

    area = get_default_building_area_template()
    area.areaDescription = "Office Area"
    project = ba_ops.add_building_area_to_project(project, area)

    space = get_default_interior_space_template()
    space.areaDescription = "Open Office"
    space.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
    space.floorArea = 2000.0
    project = il_ops.add_interior_space_to_project(project, area.key, space)
    return project


# ── Interior allowed wattage ────────────────────────────────────────────────


def test_single_space_wattage_sends_whole_project_and_area_description(
    requests, project
):
    client = _make_client(_ok(requests, {"spaceAllowedWattage": 560}))

    result = client.calculate_interior_space_allowed_wattage(project, "Open Office")

    assert result == {"spaceAllowedWattage": 560}
    (request,) = requests
    assert request.method == "POST"
    assert request.url.path.endswith("/CEZ_IECC2021/activity-use/allowed-wattage")
    assert request.url.params["areaDescription"] == "Open Office"
    assert json.loads(request.content) == project.model_dump(mode="json")


def test_single_space_wattage_energy_code_override(requests, project):
    client = _make_client(_ok(requests, {"spaceAllowedWattage": 560}))

    client.calculate_interior_space_allowed_wattage(
        project, "Open Office", energy_code="CEZ_90_1_2022"
    )

    (request,) = requests
    assert request.url.path.endswith("/CEZ_90_1_2022/activity-use/allowed-wattage")


def test_multiple_spaces_wattage_sends_whole_project(requests, project):
    client = _make_client(_ok(requests, {"Open Office": 560}))

    result = client.calculate_interior_spaces_allowed_wattage(project)

    assert result == {"Open Office": 560}
    (request,) = requests
    assert request.method == "POST"
    assert request.url.path.endswith("/CEZ_IECC2021/activity-uses/allowed-wattage")
    assert "areaDescription" not in request.url.params
    assert json.loads(request.content) == project.model_dump(mode="json")


# ── U-values ────────────────────────────────────────────────────────────────


@pytest.fixture
def project_with_wall(project):
    wall = get_default_ag_wall_template()
    area_key = project.lighting.wholeBldgUse[-1].key
    project = env_ops.add_ag_wall_to_project(project, area_key, wall)
    return project


def test_update_uvalues_sends_location(requests, project_with_wall):
    project = project_with_wall
    wall = project.envelope.agWall[0]
    data = {
        "agWall": [
            {
                "assemblyType": wall.assemblyType,
                "propUValue": 0.055,
                "reqUValue": 0.064,
                "effectiveUFactor": 0.06,
            }
        ]
    }
    client = _make_client(_ok(requests, data))
    sent_ag_walls = project.envelope.model_dump(mode="json")["agWall"]

    client.update_uvalues(project)

    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2021/assemblies/uvalues")
    body = json.loads(request.content)
    assert body["location"] == project.location.model_dump(mode="json")
    assert body["agWall"] == sent_ag_walls
    assert wall.propUValue == pytest.approx(0.055)
    assert wall.effectiveUFactor == pytest.approx(0.06)


def test_update_uvalues_keeps_values_when_response_is_null(requests, project_with_wall):
    project = project_with_wall
    wall = project.envelope.agWall[0]
    wall.propUValue = 0.1
    wall.effectiveUFactor = 0.2
    data = {
        "agWall": [
            {
                "assemblyType": wall.assemblyType,
                "propUValue": None,
                "reqUValue": None,
                "effectiveUFactor": None,
            }
        ]
    }
    client = _make_client(_ok(requests, data))

    client.update_uvalues(project)

    assert wall.propUValue == pytest.approx(0.1)
    assert wall.effectiveUFactor == pytest.approx(0.2)
