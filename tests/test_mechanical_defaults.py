"""Tests for mechanical defaults templates."""

import pytest
from uuid import UUID

from comcheck_api.defaults import (
    get_default_project_template,
    get_default_hvac_system_template,
    get_default_fan_system_template,
    get_default_fan_template,
    get_default_hvac_plant_template,
    get_default_water_heater_template,
)
from comcheck_api.project_operations import (
    project_mechanical_operations as mech_ops,
)
from comcheck_api.types.core_types import (
    ComBuilding,
    HVACSystem,
    FanSystem,
    Fan,
    HVACPlant,
    ServiceWaterHeatingSystem,
)


@pytest.fixture
def project() -> ComBuilding:
    """Return a fresh default project for each test."""
    return get_default_project_template()


def _fresh(project: ComBuilding) -> ComBuilding:
    return project.model_copy(deep=True)


# ---------------------------------------------------------------------------
# HVAC System Template Tests
# ---------------------------------------------------------------------------


def test_hvac_system_template_returns_fresh_copy():
    """Test that get_default_hvac_system_template returns independent copies."""
    template1 = get_default_hvac_system_template()
    template2 = get_default_hvac_system_template()

    # Mutate the first template
    template1.description = "Modified"
    template1.quantity = 999

    # Second template should be unaffected
    assert template2.description == ""
    assert template2.quantity == 1


def test_hvac_system_template_validates():
    """Test that the HVAC system template passes validation."""
    template = get_default_hvac_system_template()
    assert isinstance(template, HVACSystem)
    # Should be able to create a new instance from the template's dict
    HVACSystem.model_validate(template.model_dump())


def test_hvac_system_template_auto_naming(project: ComBuilding):
    """Test that adding two HVAC systems with empty description generates auto names."""
    proj = _fresh(project)

    # Add first HVAC system
    hvac1 = get_default_hvac_system_template()
    proj = mech_ops.add_hvac_system_to_project(proj, hvac1)

    # Add second HVAC system
    hvac2 = get_default_hvac_system_template()
    proj = mech_ops.add_hvac_system_to_project(proj, hvac2)

    # Check that both got auto-generated names
    assert proj.hvac.hvacSystem[0].description == "HVAC System 1"
    assert proj.hvac.hvacSystem[1].description == "HVAC System 2"


# ---------------------------------------------------------------------------
# Fan System Template Tests
# ---------------------------------------------------------------------------


def test_fan_system_template_returns_fresh_copy():
    """Test that get_default_fan_system_template returns independent copies."""
    template1 = get_default_fan_system_template()
    template2 = get_default_fan_system_template()

    # Mutate the first template
    template1.description = "Modified"
    template1.pressureDropCredits.append({"type": "test"})

    # Second template should be unaffected
    assert template2.description == ""
    assert len(template2.pressureDropCredits) == 0


def test_fan_system_template_validates():
    """Test that the fan system template passes validation."""
    template = get_default_fan_system_template()
    assert isinstance(template, FanSystem)
    # Should be able to create a new instance from the template's dict
    FanSystem.model_validate(template.model_dump())


def test_fan_system_template_auto_naming_and_uuid(project: ComBuilding):
    """Test that adding two fan systems with empty description generates auto names and UUIDs."""
    proj = _fresh(project)

    # Add first fan system
    fan_sys1 = get_default_fan_system_template()
    proj = mech_ops.add_fan_system_to_project(proj, fan_sys1)

    # Add second fan system
    fan_sys2 = get_default_fan_system_template()
    proj = mech_ops.add_fan_system_to_project(proj, fan_sys2)

    # Check that both got auto-generated names
    assert proj.hvac.fanSystem[0].description == "Fan System 1"
    assert proj.hvac.fanSystem[1].description == "Fan System 2"

    # Check that both got unique UUIDs
    uuid1 = proj.hvac.fanSystem[0].fanSystemKey
    uuid2 = proj.hvac.fanSystem[1].fanSystemKey
    assert uuid1 is not None
    assert uuid2 is not None
    assert uuid1 != uuid2
    # Verify they are valid UUIDs
    UUID(uuid1)
    UUID(uuid2)


# ---------------------------------------------------------------------------
# Fan Template Tests
# ---------------------------------------------------------------------------


def test_fan_template_returns_fresh_copy():
    """Test that get_default_fan_template returns independent copies."""
    template1 = get_default_fan_template()
    template2 = get_default_fan_template()

    # Mutate the first template
    template1.description = "Modified"
    template1.volume = 999.0

    # Second template should be unaffected
    assert template2.description == ""
    assert template2.volume == 0.0


def test_fan_template_validates():
    """Test that the fan template passes validation."""
    template = get_default_fan_template()
    assert isinstance(template, Fan)
    # Should be able to create a new instance from the template's dict
    Fan.model_validate(template.model_dump())


def test_fan_template_auto_naming(project: ComBuilding):
    """Test that adding two fans to a fan system with empty description generates auto names."""
    proj = _fresh(project)

    # Create a fan system first
    fan_sys = get_default_fan_system_template()
    proj = mech_ops.add_fan_system_to_project(proj, fan_sys)

    fan_system_desc = proj.hvac.fanSystem[0].description

    # Add first fan
    fan1 = get_default_fan_template()
    proj = mech_ops.add_fan_to_fan_system(proj, fan_system_desc, fan1)

    # Add second fan
    fan2 = get_default_fan_template()
    proj = mech_ops.add_fan_to_fan_system(proj, fan_system_desc, fan2)

    # Check that both got auto-generated names
    assert proj.hvac.fanSystem[0].fan[0].description == "Fan 1"
    assert proj.hvac.fanSystem[0].fan[1].description == "Fan 2"


# ---------------------------------------------------------------------------
# HVAC Plant Template Tests
# ---------------------------------------------------------------------------


def test_hvac_plant_template_returns_fresh_copy():
    """Test that get_default_hvac_plant_template returns independent copies."""
    template1 = get_default_hvac_plant_template()
    template2 = get_default_hvac_plant_template()

    # Mutate the first template
    template1.description = "Modified"
    template1.quantity = 999

    # Second template should be unaffected
    assert template2.description == ""
    assert template2.quantity == 1


def test_hvac_plant_template_validates():
    """Test that the HVAC plant template passes validation."""
    template = get_default_hvac_plant_template()
    assert isinstance(template, HVACPlant)
    # Should be able to create a new instance from the template's dict
    HVACPlant.model_validate(template.model_dump())


def test_hvac_plant_template_auto_naming(project: ComBuilding):
    """Test that adding two plants with empty description generates auto names."""
    proj = _fresh(project)

    # Add first plant
    plant1 = get_default_hvac_plant_template()
    proj = mech_ops.add_hvac_plant_to_project(proj, plant1)

    # Add second plant
    plant2 = get_default_hvac_plant_template()
    proj = mech_ops.add_hvac_plant_to_project(proj, plant2)

    # Check that both got auto-generated names
    assert proj.hvac.hvacPlant[0].description == "Plant 1"
    assert proj.hvac.hvacPlant[1].description == "Plant 2"


# ---------------------------------------------------------------------------
# Water Heater Template Tests
# ---------------------------------------------------------------------------


def test_water_heater_template_returns_fresh_copy():
    """Test that get_default_water_heater_template returns independent copies."""
    template1 = get_default_water_heater_template()
    template2 = get_default_water_heater_template()

    # Mutate the first template
    template1.description = "Modified"
    template1.quantity = 999

    # Second template should be unaffected
    assert template2.description == ""
    assert template2.quantity == 1


def test_water_heater_template_validates():
    """Test that the water heater template passes validation."""
    template = get_default_water_heater_template()
    assert isinstance(template, ServiceWaterHeatingSystem)
    # Should be able to create a new instance from the template's dict
    ServiceWaterHeatingSystem.model_validate(template.model_dump())


def test_water_heater_template_auto_naming(project: ComBuilding):
    """Test that adding two water heaters with empty description generates auto names."""
    proj = _fresh(project)

    # Add first water heater
    wh1 = get_default_water_heater_template()
    proj = mech_ops.add_water_heater_to_project(proj, wh1)

    # Add second water heater
    wh2 = get_default_water_heater_template()
    proj = mech_ops.add_water_heater_to_project(proj, wh2)

    # Check that both got auto-generated names
    assert proj.swhSystem[0].description == "Water Heater 1"
    assert proj.swhSystem[1].description == "Water Heater 2"


def test_templates_match_ui_defaults():
    """Spot-check values taken from the UI's Add dialogs."""
    from comcheck_api.types.core_types import (
        CoolingEquipmentTypeOptions,
        HeatPumpPoolHeater,
    )

    hvac_system = get_default_hvac_system_template()
    assert hvac_system.coolingEquipment == CoolingEquipmentTypeOptions.NO_COOLING_EQUIPMENT
    assert hvac_system.propCoolingEquipEfficiency == 0.0

    water_heater = get_default_water_heater_template()
    assert water_heater.heatPumpPoolHeater == HeatPumpPoolHeater.int_0
    assert water_heater.inputRating == 75.0
