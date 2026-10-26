"""Offline tests for the mechanical API service and client methods.

Requests are served by an ``httpx.MockTransport``, so no API key or network
access is needed.
"""

import json

import httpx
import pytest

from comcheck_api import COMcheckClient
from comcheck_api.api.api_services import COMCheckApiService
from comcheck_api.defaults import get_default_project_template
from comcheck_api.exceptions import COMCheckAPIError, COMCheckHTTPError
from comcheck_api.types.api_types import (
    WaterHeaterEfficiency,
    HVACSystemEfficiency,
    EconomizerValidation,
    PlantEfficiency,
    FanSystemComplianceResult,
)
from comcheck_api.types.core_types import (
    EnergyCodeOptions,
    ServiceWaterHeatingSystem,
    HVACSystem,
    HVACPlant,
    FanSystem,
    FanSystemPressureDropCredits,
    Fan,
    HVAC,
    HasPressureDropCredits,
    MISSING,
)


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
    project.hvac = HVAC(
        hvacSystem=[],
        hvacPlant=[],
        fanSystem=[
            FanSystem(
                description="Test Fan System",
                pressureDropCredits=[
                    FanSystemPressureDropCredits(
                        type="PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12",
                    )
                ],
            )
        ],
    )
    return project


@pytest.fixture
def requests():
    return []


def _ok(requests, data):
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"message": "Success", "data": data})

    return handler


# Water heater efficiency tests
def test_water_heater_efficiency_service_single(requests):
    data = {"Water Heater 1": {"minEfficiency": 0.8, "maxEfficiency": 0.95, "efficiencyUnits": "EF"}}
    service = _make_service(_ok(requests, data))
    swh = {"description": "Water Heater 1"}

    result = service.water_heater_efficiency(swh, "CEZ_IECC2024")

    assert result["data"] == data
    (request,) = requests
    assert request.method == "POST"
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/water-heaters/efficiency")
    assert json.loads(request.content) == swh


def test_water_heater_efficiency_service_list_with_query(requests):
    data = {
        "WH1": {"minEfficiency": 0.8, "maxEfficiency": 0.95, "efficiencyUnits": "EF"},
        "WH2": {"minEfficiency": 0.85, "maxEfficiency": 0.98, "efficiencyUnits": "EF"},
    }
    service = _make_service(_ok(requests, data))
    swh_list = [{"description": "WH1"}, {"description": "WH2"}]

    result = service.water_heater_efficiency(swh_list, "CEZ_IECC2024", "WH1")

    assert result["data"] == data
    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/water-heaters/efficiency")
    assert str(request.url).endswith("?waterHeaterName=WH1")
    assert json.loads(request.content) == swh_list


def test_calculate_water_heater_efficiency_single(requests):
    data = {"Water Heater 1": {"minEfficiency": 0.8, "maxEfficiency": 0.95, "efficiencyUnits": "EF"}}
    client = _make_client(_ok(requests, data))
    swh = ServiceWaterHeatingSystem(description="Water Heater 1")

    result = client.calculate_water_heater_efficiency(swh, "CEZ_IECC2024")

    assert isinstance(result, dict)
    assert "Water Heater 1" in result
    assert isinstance(result["Water Heater 1"], WaterHeaterEfficiency)
    assert result["Water Heater 1"].minEfficiency == 0.8
    assert result["Water Heater 1"].efficiencyUnits == "EF"


def test_calculate_water_heater_efficiency_list(requests):
    data = {
        "WH1": {"minEfficiency": 0.8, "maxEfficiency": 0.95, "efficiencyUnits": "EF"},
        "WH2": {"minEfficiency": 0.85, "maxEfficiency": 0.98, "efficiencyUnits": "EF"},
    }
    client = _make_client(_ok(requests, data))
    swh_list = [
        ServiceWaterHeatingSystem(description="WH1"),
        ServiceWaterHeatingSystem(description="WH2"),
    ]

    result = client.calculate_water_heater_efficiency(swh_list, "CEZ_IECC2024")

    assert len(result) == 2
    assert result["WH1"].minEfficiency == 0.8
    assert result["WH2"].minEfficiency == 0.85


def test_calculate_water_heater_efficiency_duplicate_descriptions():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    swh_list = [
        ServiceWaterHeatingSystem(description="WH1"),
        ServiceWaterHeatingSystem(description="WH1"),
    ]

    with pytest.raises(ValueError, match="unique"):
        client.calculate_water_heater_efficiency(swh_list, "CEZ_IECC2024")


def test_calculate_water_heater_efficiency_name_mismatch():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    swh = ServiceWaterHeatingSystem(description="WH1")

    with pytest.raises(ValueError, match="does not match"):
        client.calculate_water_heater_efficiency(swh, "CEZ_IECC2024", water_heater_name="WH2")


# HVAC system efficiency tests
def test_hvac_system_efficiency_service(requests):
    data = {"HVAC 1": {"minCoolingEfficiency": 13.0, "coolingEfficiencyUnits": "SEER"}}
    service = _make_service(_ok(requests, data))
    hvac = {"description": "HVAC 1"}

    result = service.hvac_system_efficiency(hvac, "CEZ_IECC2024", "HVAC 1")

    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/hvac-systems/efficiency")
    assert str(request.url).endswith("?hvacName=HVAC+1")


def test_calculate_hvac_system_efficiency(requests):
    data = {"HVAC 1": {"minCoolingEfficiency": 13.0, "coolingEfficiencyUnits": "SEER"}}
    client = _make_client(_ok(requests, data))
    hvac = HVACSystem(description="HVAC 1")

    result = client.calculate_hvac_system_efficiency(hvac, "CEZ_IECC2024")

    assert "HVAC 1" in result
    assert isinstance(result["HVAC 1"], HVACSystemEfficiency)
    assert result["HVAC 1"].minCoolingEfficiency == 13.0


def test_calculate_hvac_system_efficiency_duplicate_descriptions():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    hvac_list = [HVACSystem(description="H1"), HVACSystem(description="H1")]

    with pytest.raises(ValueError, match="unique"):
        client.calculate_hvac_system_efficiency(hvac_list, "CEZ_IECC2024")


# Economizer validation tests
def test_hvac_system_economizers_validation_service(requests):
    data = {"HVAC 1": {"complies": True, "coolingCapLimitNoEconomizer": 54000.0}}
    service = _make_service(_ok(requests, data))
    hvac = {"description": "HVAC 1"}

    result = service.hvac_system_economizers_validation(hvac, "CEZ_IECC2024")

    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/hvac-systems/economizers-validation")
    assert json.loads(request.content) == hvac


def test_validate_hvac_system_economizer(requests):
    data = {"HVAC 1": {"complies": True, "coolingCapLimitNoEconomizer": 54000.0}}
    client = _make_client(_ok(requests, data))
    hvac = HVACSystem(description="HVAC 1")

    result = client.validate_hvac_system_economizer(hvac, "CEZ_IECC2024")

    assert isinstance(result, EconomizerValidation)
    assert result.complies is True
    assert result.coolingCapLimitNoEconomizer == 54000.0


def test_validate_hvac_system_economizer_empty_description():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    hvac = HVACSystem(description="")

    with pytest.raises(ValueError, match="cannot be empty"):
        client.validate_hvac_system_economizer(hvac, "CEZ_IECC2024")


# Plant efficiency tests
def test_plant_efficiency_service(requests):
    data = {"Plant 1": {"plantMinHeatingEfficiency": 0.85}}
    service = _make_service(_ok(requests, data))
    plant = {"description": "Plant 1"}

    result = service.plant_efficiency(plant, "CEZ_IECC2024")

    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/plants/efficiency")


def test_calculate_plant_efficiency(requests):
    data = {"Plant 1": {"plantMinHeatingEfficiency": 0.85}}
    client = _make_client(_ok(requests, data))
    plant = HVACPlant(description="Plant 1")

    result = client.calculate_plant_efficiency(plant, "CEZ_IECC2024")

    assert "Plant 1" in result
    assert isinstance(result["Plant 1"], PlantEfficiency)
    assert result["Plant 1"].plantMinHeatingEfficiency == 0.85


def test_calculate_plant_efficiency_duplicate_descriptions():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    plant_list = [HVACPlant(description="P1"), HVACPlant(description="P1")]

    with pytest.raises(ValueError, match="unique"):
        client.calculate_plant_efficiency(plant_list, "CEZ_IECC2024")


# Fan pressure drop credit tests
def test_fan_pressure_drop_credit_service(requests):
    data = {"pressureDropCredit": 0.35}
    service = _make_service(_ok(requests, data))
    credit = {"deviceType": "FILTER"}

    result = service.fan_pressure_drop_credit(credit, "CEZ_IECC2024", "PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12")

    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/fan-systems/fan-pressure-credit")
    assert "fanPressureCreditType=PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12" in str(request.url)
    assert json.loads(request.content) == credit


def test_calculate_fan_pressure_drop_credit(requests):
    data = {"pressureDropCredit": 0.35}
    client = _make_client(_ok(requests, data))
    credit = FanSystemPressureDropCredits(type="PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12")

    result = client.calculate_fan_pressure_drop_credit(credit, "CEZ_IECC2024")

    assert result == 0.35
    (request,) = requests
    # Check that type was sent as query param, not in body
    body = json.loads(request.content)
    assert "type" not in body


def test_calculate_fan_pressure_drop_credit_unspecified_type():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    credit = FanSystemPressureDropCredits(type="PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED")

    with pytest.raises(ValueError, match="UNSPECIFIED"):
        client.calculate_fan_pressure_drop_credit(credit, "CEZ_IECC2024")


# Fan system compliance tests
def test_fan_system_compliance_service(requests):
    data = {
        "hasPressureDropCredits": True,
        "complyMethod": "FAN_SYSTEM_MOTOR_NAMEPLATE_HP",
        "complies": True,
        "complianceMessage": "Complies",
        "proposed": 5.0,
        "maxAllowed": 10.0,
    }
    service = _make_service(_ok(requests, data))
    fan_system = {"description": "Fan System 1"}

    result = service.fan_system_compliance(fan_system, "CEZ_IECC2024")

    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/fan-systems/compliance")
    assert json.loads(request.content) == fan_system


def test_check_fan_system_compliance(requests):
    data = {
        "hasPressureDropCredits": True,
        "complyMethod": "FAN_SYSTEM_MOTOR_NAMEPLATE_HP",
        "complies": True,
        "complianceMessage": "Complies",
        "proposed": 5.0,
        "maxAllowed": 10.0,
    }
    client = _make_client(_ok(requests, data))
    fan_system = FanSystem(description="Fan System 1")

    result = client.check_fan_system_compliance(fan_system, "CEZ_IECC2024")

    assert isinstance(result, FanSystemComplianceResult)
    assert result.complies is True
    assert result.proposed == 5.0


# Fan maximum allowable HP tests
def test_fan_maximum_allowable_hp_service(requests):
    data = {"maxNameplateHp": 7.5}
    service = _make_service(_ok(requests, data))
    fan = {"motorHp": 5.0}

    result = service.fan_maximum_allowable_hp(fan, "CEZ_IECC2024")

    (request,) = requests
    assert request.url.path.endswith("/CEZ_IECC2024/mechanical/fan-systems/maximum-allowable-hp")


def test_calculate_fan_maximum_allowable_hp(requests):
    data = {"maxNameplateHp": 7.5}
    client = _make_client(_ok(requests, data))
    fan = Fan(motorHp=5.0)

    result = client.calculate_fan_maximum_allowable_hp(fan, "CEZ_IECC2024")

    assert result == 7.5


# Project write-back tests
def test_update_fan_system_compliance(requests, project):
    data = {
        "hasPressureDropCredits": True,
        "complyMethod": "FAN_SYSTEM_MOTOR_NAMEPLATE_HP",
        "complies": True,
        "complianceMessage": "Complies",
        "proposed": 5.0,
        "maxAllowed": 10.0,
    }
    client = _make_client(_ok(requests, data))
    before = project.model_dump(mode="json")

    result = client.update_fan_system_compliance(project, "Test Fan System")

    assert result is project
    fan_system = project.hvac.fanSystem[0]
    assert fan_system.complies is True
    assert fan_system.complianceMessage == "Complies"
    assert fan_system.complyMethod == "FAN_SYSTEM_MOTOR_NAMEPLATE_HP"
    assert fan_system.hasPressureDropCredits == HasPressureDropCredits.int_1


def test_update_fan_system_compliance_not_found(requests, project):
    client = _make_client(_ok(requests, {}))

    with pytest.raises(ValueError, match="not found"):
        client.update_fan_system_compliance(project, "Nonexistent")


def test_update_fan_system_compliance_no_hvac():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    project = get_default_project_template()
    project.hvac = MISSING

    with pytest.raises(ValueError, match="no hvac"):
        client.update_fan_system_compliance(project, "Test")


def test_update_fan_pressure_drop_credits(requests, project):
    data = {"pressureDropCredit": 0.35}
    client = _make_client(_ok(requests, data))

    result = client.update_fan_pressure_drop_credits(project, "Test Fan System")

    assert result is project
    fan_system = project.hvac.fanSystem[0]
    assert fan_system.pressureDropCredits[0].pressureDropCredit == 0.35


def test_update_fan_pressure_drop_credits_not_found(requests, project):
    client = _make_client(_ok(requests, {}))

    with pytest.raises(ValueError, match="not found"):
        client.update_fan_pressure_drop_credits(project, "Nonexistent")


def test_update_fan_pressure_drop_credits_no_hvac():
    client = _make_client(lambda r: httpx.Response(200, json={}))
    project = get_default_project_template()
    project.hvac = MISSING

    with pytest.raises(ValueError, match="no hvac"):
        client.update_fan_pressure_drop_credits(project, "Test")


# Error handling tests
def test_mechanical_service_maps_http_errors():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"_tag": "InvalidBodyException"})

    service = _make_service(handler)

    with pytest.raises(COMCheckHTTPError) as exc_info:
        service.water_heater_efficiency({}, "CEZ_IECC2024")
    assert exc_info.value.status_code == 400

    with pytest.raises(COMCheckHTTPError):
        service.hvac_system_efficiency({}, "CEZ_IECC2024")

    with pytest.raises(COMCheckHTTPError):
        service.hvac_system_economizers_validation({}, "CEZ_IECC2024")

    with pytest.raises(COMCheckHTTPError):
        service.plant_efficiency({}, "CEZ_IECC2024")

    with pytest.raises(COMCheckHTTPError):
        service.fan_pressure_drop_credit({}, "CEZ_IECC2024", "TYPE")

    with pytest.raises(COMCheckHTTPError):
        service.fan_system_compliance({}, "CEZ_IECC2024")

    with pytest.raises(COMCheckHTTPError):
        service.fan_maximum_allowable_hp({}, "CEZ_IECC2024")


def test_calculate_fan_maximum_allowable_hp_missing_value_raises(requests):
    """A response without maxNameplateHp raises instead of returning 0."""
    client = _make_client(_ok(requests, {}))

    with pytest.raises(COMCheckAPIError):
        client.calculate_fan_maximum_allowable_hp(Fan(description="Fan 1"), "CEZ_IECC2024")


def test_validate_hvac_system_economizer_string_capacity(requests):
    """Capacity fields are documented as strings in the OpenAPI spec."""
    data = {"HVAC 1": {"coolingCapLimitNoEconomizer": "54,000 Btu/h", "complies": True}}
    client = _make_client(_ok(requests, data))

    result = client.validate_hvac_system_economizer(
        HVACSystem(description="HVAC 1"), "CEZ_IECC2024"
    )

    assert result.coolingCapLimitNoEconomizer == "54,000 Btu/h"
