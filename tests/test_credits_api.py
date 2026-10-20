"""Offline tests for the energy credit API service and client methods.

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
from comcheck_api.types.api_types import EnergyCreditResult
from comcheck_api.types.core_types import EnergyCodeOptions

CREDITS_DATA = {
    "energyCredits": [
        {
            "creditType": "EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ENHANCED_ROOF_R10",
            "bldgUseKey": "area-1",
            "category": "regular",
            "value": 3.2,
        },
        {
            "creditType": "EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ELECTRIC_STORAGE",
            "bldgUseKey": "area-1",
            "category": "renewable_load",
            "value": 4.0,
        },
    ],
    "proposed": 3.2,
    "required": 10,
    "proposedRenewableAndLoadMgmt": 4.0,
    "requiredRenewableAndLoadMgmt": 5,
    "warnings": [],
    "userAlerts": [
        {
            "level": "error",
            "category": "energy_credit",
            "message": "Insufficient energy credits: 3.2 proposed, 10 required (deficit: 6.8)",
        }
    ],
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
    project.control.code = EnergyCodeOptions.CEZ_IECC2024
    return project


@pytest.fixture
def requests():
    return []


def _ok(requests, data):
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"message": "Success", "data": data})

    return handler


def test_update_energy_credits_service_posts_project(requests, project):
    service = _make_service(_ok(requests, CREDITS_DATA))
    project_data = project.model_dump(mode="json")

    result = service.update_energy_credits(project_data)

    assert result["data"] == CREDITS_DATA
    (request,) = requests
    assert request.method == "POST"
    assert request.url.path.endswith("/update-energy-credits")
    assert request.headers["x-api-key"] == "test"
    assert json.loads(request.content) == project_data


def test_update_energy_credits_service_maps_http_errors(project):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"_tag": "InvalidBodyException"})

    service = _make_service(handler)
    with pytest.raises(COMCheckHTTPError) as exc_info:
        service.update_energy_credits(project.model_dump(mode="json"))
    assert exc_info.value.status_code == 400


def test_calculate_energy_credits_returns_result(requests, project):
    client = _make_client(_ok(requests, CREDITS_DATA))
    before = project.model_dump(mode="json")

    result = client.calculate_energy_credits(project)

    assert isinstance(result, EnergyCreditResult)
    assert [credit.creditType for credit in result.energyCredits] == [
        "EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ENHANCED_ROOF_R10",
        "EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ELECTRIC_STORAGE",
    ]
    assert result.energyCredits[0].bldgUseKey == "area-1"
    assert result.energyCredits[0].value == 3.2
    assert result.proposed == 3.2
    assert result.required == 10.0
    assert result.requiredRenewableAndLoadMgmt == 5.0
    assert result.userAlerts[0].level == "error"
    assert result.passes is False
    assert project.model_dump(mode="json") == before


def test_calculate_energy_credits_handles_missing_data(requests, project):
    client = _make_client(_ok(requests, None))

    result = client.calculate_energy_credits(project)

    assert result.energyCredits == []
    assert result.proposed is None
    assert result.passes is None


@pytest.mark.parametrize(
    ("totals", "passes"),
    [
        ({"proposed": 10, "required": 10}, True),
        ({"proposed": 9.9, "required": 10}, False),
        (
            {
                "proposed": 12,
                "required": 10,
                "proposedRenewableAndLoadMgmt": 0,
                "requiredRenewableAndLoadMgmt": 0,
            },
            True,
        ),
        (
            {
                "proposed": 12,
                "required": 10,
                "proposedRenewableAndLoadMgmt": 4,
                "requiredRenewableAndLoadMgmt": 5,
            },
            False,
        ),
    ],
)
def test_energy_credit_result_passes(totals, passes):
    assert EnergyCreditResult.model_validate(totals).passes is passes
