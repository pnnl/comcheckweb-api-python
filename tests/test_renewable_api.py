"""Offline tests for the renewable API service and client methods.

Requests are served by an ``httpx.MockTransport``, so no API key or network
access is needed.
"""

import json

import httpx
import pytest

from comcheck_api import COMcheckClient
from comcheck_api.api.api_services import COMCheckApiService
from comcheck_api.defaults import get_default_project_template
from comcheck_api.exceptions import COMCheckHTTPError
from comcheck_api.types.core_types import EnergyCodeOptions

AREA_DATA = {"largestThreeFloorArea": 30000.0, "roofAreaForRenewable": 8000.0}
CAPACITY_DATA = {
    "requiredRenewableCapacity": 120.5,
    "proposedRenewableCapacity": 150.0,
    "requiredOffsiteRenewableProcurementEnergy": None,
    "proposedOffsiteRenewableProcurementEnergy": None,
    "renewableComplianceStatus": "PASS",
}


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


@pytest.fixture
def project():
    project = get_default_project_template()
    project.control.code = EnergyCodeOptions.CEZ_IECC2021
    return project


@pytest.fixture
def requests():
    return []


def _ok(requests, data):
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"message": "ok", "data": data})

    return handler


def test_area_for_renewable_service_posts_project(requests, project):
    service = _make_service(_ok(requests, AREA_DATA))
    project_data = project.model_dump(mode="json")

    result = service.area_for_renewable(project_data)

    assert result["data"] == AREA_DATA
    (request,) = requests
    assert request.method == "POST"
    assert request.url.path.endswith("/renewable/area-for-renewable")
    assert request.headers["x-api-key"] == "test"
    assert json.loads(request.content) == project_data


def test_renewable_capacity_service_posts_project(requests, project):
    service = _make_service(_ok(requests, CAPACITY_DATA))
    project_data = project.model_dump(mode="json")

    result = service.renewable_capacity(project_data)

    assert result["data"] == CAPACITY_DATA
    (request,) = requests
    assert request.method == "POST"
    assert request.url.path.endswith("/renewable/renewable-capacity")
    assert json.loads(request.content) == project_data


def test_renewable_service_maps_http_errors(project):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"_tag": "InvalidBodyException"})

    service = _make_service(handler)
    with pytest.raises(COMCheckHTTPError) as exc_info:
        service.area_for_renewable(project.model_dump(mode="json"))
    assert exc_info.value.status_code == 400

    with pytest.raises(COMCheckHTTPError):
        service.renewable_capacity(project.model_dump(mode="json"))


def test_area_for_renewable_updates_project(requests, project):
    client = _make_client(_ok(requests, AREA_DATA))

    result = client.area_for_renewable(project)

    assert result is project
    assert project.renewable.largestThreeFloorArea == 30000.0
    assert project.renewable.roofAreaForRenewable == 8000.0


def test_area_for_renewable_handles_null_values(requests, project):
    client = _make_client(
        _ok(requests, {"largestThreeFloorArea": None, "roofAreaForRenewable": 0})
    )

    client.area_for_renewable(project)

    assert project.renewable.largestThreeFloorArea is None
    assert project.renewable.roofAreaForRenewable == 0.0


def test_renewable_capacity_updates_project(requests, project):
    client = _make_client(_ok(requests, CAPACITY_DATA))

    result = client.renewable_capacity(project)

    assert result is project
    renewable = project.renewable
    assert renewable.requiredCapacity == 120.5
    assert renewable.proposedCapacity == 150.0
    assert renewable.requiredOffsiteRenewableEnergy is None
    assert renewable.proposedOffsiteRenewableEnergy is None
