"""Tests for project_mechanical_operations."""

import pytest
from uuid import UUID
from pydantic.experimental.missing_sentinel import MISSING

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


def _get_test_hvac_system():
    """Create a minimal test HVAC system."""
    return HVACSystem(description="")


def _get_test_fan_system():
    """Create a minimal test fan system."""
    return FanSystem(description="")


def _get_test_fan():
    """Create a minimal test fan."""
    return Fan(description="")


def _get_test_hvac_plant():
    """Create a minimal test HVAC plant."""
    return HVACPlant(description="")


def _get_test_water_heater():
    """Create a minimal test water heater."""
    return ServiceWaterHeatingSystem(description="")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh(project: ComBuilding) -> ComBuilding:
    return project.model_copy(deep=True)


# ---------------------------------------------------------------------------
# HVAC System Tests
# ---------------------------------------------------------------------------


def test_add_hvac_system_to_project(project: ComBuilding):
    proj = _fresh(project)
    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC System"

    result = mech_ops.add_hvac_system_to_project(proj, hvac_system)

    # Check that hvac was created and system was added
    assert result.hvac is not MISSING
    assert len(result.hvac.hvacSystem) == 1
    assert result.hvac.hvacSystem[0].description == "Test HVAC System"


def test_add_hvac_system_generates_description(project: ComBuilding):
    proj = _fresh(project)
    hvac_system = _get_test_hvac_system()
    hvac_system.description = ""

    result = mech_ops.add_hvac_system_to_project(proj, hvac_system)

    # Should have generated a description like "HVAC System 1"
    assert result.hvac.hvacSystem[0].description.startswith("HVAC System")


def test_add_hvac_system_with_invalid_fan_system_key(project: ComBuilding):
    proj = _fresh(project)
    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    hvac_system.fanSystemKey = "invalid-uuid"

    with pytest.raises(ValueError, match="does not match any existing fan system"):
        mech_ops.add_hvac_system_to_project(proj, hvac_system)


def test_update_hvac_system_in_project(project: ComBuilding):
    proj = _fresh(project)
    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)

    result = mech_ops.update_hvac_system_in_project(proj, "Test HVAC", {"quantity": 5})

    assert result.hvac.hvacSystem[0].quantity == 5


def test_update_hvac_system_rejects_engine_fields(project: ComBuilding):
    proj = _fresh(project)
    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)

    with pytest.raises(ValueError, match="engine-calculated"):
        mech_ops.update_hvac_system_in_project(proj, "Test HVAC", {"requirementAnswer": "test"})


def test_update_hvac_system_not_found(project: ComBuilding):
    proj = _fresh(project)

    with pytest.raises(ValueError, match="not found"):
        mech_ops.update_hvac_system_in_project(proj, "Nonexistent", {"quantity": 5})


def test_remove_hvac_system_from_project(project: ComBuilding):
    proj = _fresh(project)
    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)

    result = mech_ops.remove_hvac_system_from_project(proj, "Test HVAC")

    assert len(result.hvac.hvacSystem) == 0


def test_get_hvac_system_keys_from_project(project: ComBuilding):
    proj = _fresh(project)
    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)

    keys = mech_ops.get_hvac_system_keys_from_project(proj)

    assert len(keys) == 1
    assert keys[0]["description"] == "Test HVAC"
    assert "systemType" in keys[0]
    assert "fanSystemKey" in keys[0]
    assert "fanSystemDescription" in keys[0]


def test_hvac_operations_do_not_mutate_original(project: ComBuilding):
    proj = _fresh(project)
    original_hvac = proj.hvac

    mech_ops.add_hvac_system_to_project(proj, _get_test_hvac_system())

    assert proj.hvac == original_hvac


# ---------------------------------------------------------------------------
# Fan System Tests
# ---------------------------------------------------------------------------


def test_add_fan_system_to_project(project: ComBuilding):
    proj = _fresh(project)
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan System"

    result = mech_ops.add_fan_system_to_project(proj, fan_system)

    # Check that hvac was created and fan system was added
    assert result.hvac is not MISSING
    assert len(result.hvac.fanSystem) == 1
    assert result.hvac.fanSystem[0].description == "Test Fan System"
    # Check that a UUID was generated
    assert result.hvac.fanSystem[0].fanSystemKey is not None


def test_add_fan_system_generates_uuid(project: ComBuilding):
    proj = _fresh(project)
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    fan_system.fanSystemKey = None  # No UUID provided

    result = mech_ops.add_fan_system_to_project(proj, fan_system)

    # Should have generated a valid UUID
    uuid_str = result.hvac.fanSystem[0].fanSystemKey
    assert uuid_str is not None
    # Verify it's a valid UUID
    UUID(uuid_str)


def test_add_fan_system_replaces_duplicate_uuid(project: ComBuilding):
    proj = _fresh(project)

    # Add first fan system
    fan1 = _get_test_fan_system()
    fan1.description = "Fan 1"
    proj = mech_ops.add_fan_system_to_project(proj, fan1)

    # Try to add second fan system with same UUID
    fan2 = _get_test_fan_system()
    fan2.description = "Fan 2"
    fan2.fanSystemKey = proj.hvac.fanSystem[0].fanSystemKey

    result = mech_ops.add_fan_system_to_project(proj, fan2)

    # UUIDs should be different
    assert result.hvac.fanSystem[0].fanSystemKey != result.hvac.fanSystem[1].fanSystemKey


def test_update_fan_system_in_project(project: ComBuilding):
    proj = _fresh(project)
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    result = mech_ops.update_fan_system_in_project(proj, "Test Fan", {"description": "Updated Fan"})

    assert result.hvac.fanSystem[0].description == "Updated Fan"


def test_update_fan_system_rejects_fan_system_key(project: ComBuilding):
    proj = _fresh(project)
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    with pytest.raises(ValueError, match="identity fields"):
        mech_ops.update_fan_system_in_project(proj, "Test Fan", {"fanSystemKey": "new-uuid"})



def test_update_fan_system_rejects_fan_system_key_in_model(project: ComBuilding):
    """A model update is checked too, not only a dict update."""
    proj = mech_ops.add_fan_system_to_project(
        _fresh(project), FanSystem(description="Test Fan")
    )

    with pytest.raises(ValueError, match="identity fields"):
        mech_ops.update_fan_system_in_project(
            proj, "Test Fan", FanSystem(fanSystemKey="new-uuid")
        )


def test_update_fan_system_accepts_unchanged_copy(project: ComBuilding):
    """Passing back an edited copy keeps the same fanSystemKey and is allowed."""
    proj = mech_ops.add_fan_system_to_project(
        _fresh(project), FanSystem(description="Test Fan")
    )
    edited = proj.hvac.fanSystem[0].model_copy(update={"description2": "3 areas"})

    proj = mech_ops.update_fan_system_in_project(proj, "Test Fan", edited)

    assert proj.hvac.fanSystem[0].description2 == "3 areas"


def test_update_hvac_system_rejects_unknown_fan_system_key_in_model(project: ComBuilding):
    proj = mech_ops.add_hvac_system_to_project(
        _fresh(project), HVACSystem(description="RTU 1")
    )

    with pytest.raises(ValueError, match="does not match any existing fan system"):
        mech_ops.update_hvac_system_in_project(
            proj, "RTU 1", HVACSystem(fanSystemKey="not-a-fan-system")
        )


def test_assign_fan_system_without_key_raises(project: ComBuilding):
    proj = mech_ops.add_hvac_system_to_project(
        _fresh(project), HVACSystem(description="RTU 1")
    )
    proj = mech_ops.add_fan_system_to_project(proj, FanSystem(description="Fan Sys"))
    proj.hvac.fanSystem[0].fanSystemKey = None

    with pytest.raises(ValueError, match="has no fanSystemKey"):
        mech_ops.assign_fan_system_to_hvac_system(proj, "RTU 1", "Fan Sys")

def test_update_fan_system_rejects_engine_fields(project: ComBuilding):
    proj = _fresh(project)
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    with pytest.raises(ValueError, match="engine-calculated"):
        mech_ops.update_fan_system_in_project(proj, "Test Fan", {"complies": True})

    with pytest.raises(ValueError, match="engine-calculated"):
        mech_ops.update_fan_system_in_project(proj, "Test Fan", {"complianceMessage": "test"})


def test_remove_fan_system_clears_hvac_references(project: ComBuilding):
    proj = _fresh(project)

    # Add a fan system
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)
    fan_key = proj.hvac.fanSystem[0].fanSystemKey

    # Add an HVAC system and assign the fan system
    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)
    proj = mech_ops.assign_fan_system_to_hvac_system(proj, "Test HVAC", "Test Fan")

    # Verify the link
    assert proj.hvac.hvacSystem[0].fanSystemKey == fan_key

    # Remove the fan system
    result = mech_ops.remove_fan_system_from_project(proj, "Test Fan")

    # Check that fanSystemKey was cleared on HVAC system
    assert result.hvac.hvacSystem[0].fanSystemKey is None


def test_get_fan_system_keys_from_project(project: ComBuilding):
    proj = _fresh(project)
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    keys = mech_ops.get_fan_system_keys_from_project(proj)

    assert len(keys) == 1
    assert keys[0]["description"] == "Test Fan"
    assert "fanSystemKey" in keys[0]
    assert "complyMethod" in keys[0]


# ---------------------------------------------------------------------------
# Fan System Assignment Tests
# ---------------------------------------------------------------------------


def test_assign_fan_system_to_hvac_system(project: ComBuilding):
    proj = _fresh(project)

    # Add fan system and HVAC system
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)

    # Assign
    result = mech_ops.assign_fan_system_to_hvac_system(proj, "Test HVAC", "Test Fan")

    # Check the link
    fan_key = result.hvac.fanSystem[0].fanSystemKey
    assert result.hvac.hvacSystem[0].fanSystemKey == fan_key


def test_assign_fan_system_can_unassign(project: ComBuilding):
    proj = _fresh(project)

    # Add and assign
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)
    proj = mech_ops.assign_fan_system_to_hvac_system(proj, "Test HVAC", "Test Fan")

    # Unassign
    result = mech_ops.assign_fan_system_to_hvac_system(proj, "Test HVAC", None)

    assert result.hvac.hvacSystem[0].fanSystemKey is None


def test_get_hvac_system_keys_includes_fan_description(project: ComBuilding):
    proj = _fresh(project)

    # Add fan system and HVAC system
    fan_system = _get_test_fan_system()
    fan_system.description = "Supply Fan 1"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    hvac_system = _get_test_hvac_system()
    hvac_system.description = "Test HVAC"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac_system)
    proj = mech_ops.assign_fan_system_to_hvac_system(proj, "Test HVAC", "Supply Fan 1")

    keys = mech_ops.get_hvac_system_keys_from_project(proj)

    assert keys[0]["fanSystemDescription"] == "Supply Fan 1"


# ---------------------------------------------------------------------------
# Fan Tests (nested in FanSystem)
# ---------------------------------------------------------------------------


def test_add_fan_to_fan_system(project: ComBuilding):
    proj = _fresh(project)

    # Add fan system first
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan System"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    # Add a fan
    fan = _get_test_fan()
    fan.description = "Test Fan"
    result = mech_ops.add_fan_to_fan_system(proj, "Test Fan System", fan)

    # Check
    assert len(result.hvac.fanSystem[0].fan) == 1
    assert result.hvac.fanSystem[0].fan[0].description == "Test Fan"


def test_update_fan_in_fan_system(project: ComBuilding):
    proj = _fresh(project)

    # Add fan system and fan
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan System"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    fan = _get_test_fan()
    fan.description = "Test Fan"
    proj = mech_ops.add_fan_to_fan_system(proj, "Test Fan System", fan)

    # Update the fan
    result = mech_ops.update_fan_in_fan_system(
        proj, "Test Fan System", "Test Fan", {"description": "Updated Fan"}
    )

    assert result.hvac.fanSystem[0].fan[0].description == "Updated Fan"


def test_remove_fan_from_fan_system(project: ComBuilding):
    proj = _fresh(project)

    # Add fan system and fan
    fan_system = _get_test_fan_system()
    fan_system.description = "Test Fan System"
    proj = mech_ops.add_fan_system_to_project(proj, fan_system)

    fan = _get_test_fan()
    fan.description = "Test Fan"
    proj = mech_ops.add_fan_to_fan_system(proj, "Test Fan System", fan)

    # Remove the fan
    result = mech_ops.remove_fan_from_fan_system(proj, "Test Fan System", "Test Fan")

    assert len(result.hvac.fanSystem[0].fan) == 0


# ---------------------------------------------------------------------------
# HVAC Plant Tests
# ---------------------------------------------------------------------------


def test_add_hvac_plant_to_project(project: ComBuilding):
    proj = _fresh(project)
    plant = _get_test_hvac_plant()
    plant.description = "Test Plant"

    result = mech_ops.add_hvac_plant_to_project(proj, plant)

    assert result.hvac is not MISSING
    assert len(result.hvac.hvacPlant) == 1
    assert result.hvac.hvacPlant[0].description == "Test Plant"


def test_update_hvac_plant_in_project(project: ComBuilding):
    proj = _fresh(project)
    plant = _get_test_hvac_plant()
    plant.description = "Test Plant"
    proj = mech_ops.add_hvac_plant_to_project(proj, plant)

    result = mech_ops.update_hvac_plant_in_project(proj, "Test Plant", {"quantity": 3})

    assert result.hvac.hvacPlant[0].quantity == 3


def test_update_hvac_plant_rejects_engine_fields(project: ComBuilding):
    proj = _fresh(project)
    plant = _get_test_hvac_plant()
    plant.description = "Test Plant"
    proj = mech_ops.add_hvac_plant_to_project(proj, plant)

    with pytest.raises(ValueError, match="engine-calculated"):
        mech_ops.update_hvac_plant_in_project(proj, "Test Plant", {"requirementAnswer": "test"})


def test_remove_hvac_plant_from_project(project: ComBuilding):
    proj = _fresh(project)
    plant = _get_test_hvac_plant()
    plant.description = "Test Plant"
    proj = mech_ops.add_hvac_plant_to_project(proj, plant)

    result = mech_ops.remove_hvac_plant_from_project(proj, "Test Plant")

    assert len(result.hvac.hvacPlant) == 0


def test_get_hvac_plant_keys_from_project(project: ComBuilding):
    proj = _fresh(project)
    plant = _get_test_hvac_plant()
    plant.description = "Test Plant"
    proj = mech_ops.add_hvac_plant_to_project(proj, plant)

    keys = mech_ops.get_hvac_plant_keys_from_project(proj)

    assert len(keys) == 1
    assert keys[0]["description"] == "Test Plant"
    assert "plantType" in keys[0]
    assert "systemType" in keys[0]


# ---------------------------------------------------------------------------
# Water Heater Tests
# ---------------------------------------------------------------------------


def test_add_water_heater_to_project(project: ComBuilding):
    proj = _fresh(project)
    swh = _get_test_water_heater()
    swh.description = "Test Water Heater"

    result = mech_ops.add_water_heater_to_project(proj, swh)

    assert result.swhSystem is not MISSING
    assert len(result.swhSystem) == 1
    assert result.swhSystem[0].description == "Test Water Heater"


def test_add_water_heater_when_missing(project: ComBuilding):
    proj = _fresh(project)
    # Ensure swhSystem is MISSING
    proj.swhSystem = MISSING

    swh = _get_test_water_heater()
    swh.description = "Test Water Heater"

    result = mech_ops.add_water_heater_to_project(proj, swh)

    # Should have initialized to a list with one item
    assert isinstance(result.swhSystem, list)
    assert len(result.swhSystem) == 1


def test_update_water_heater_in_project(project: ComBuilding):
    proj = _fresh(project)
    swh = _get_test_water_heater()
    swh.description = "Test Water Heater"
    proj = mech_ops.add_water_heater_to_project(proj, swh)

    result = mech_ops.update_water_heater_in_project(proj, "Test Water Heater", {"quantity": 2})

    assert result.swhSystem[0].quantity == 2


def test_update_water_heater_rejects_engine_fields(project: ComBuilding):
    proj = _fresh(project)
    swh = _get_test_water_heater()
    swh.description = "Test Water Heater"
    proj = mech_ops.add_water_heater_to_project(proj, swh)

    with pytest.raises(ValueError, match="engine-calculated"):
        mech_ops.update_water_heater_in_project(proj, "Test Water Heater", {"requirementAnswer": "test"})


def test_remove_water_heater_from_project(project: ComBuilding):
    proj = _fresh(project)
    swh = _get_test_water_heater()
    swh.description = "Test Water Heater"
    proj = mech_ops.add_water_heater_to_project(proj, swh)

    result = mech_ops.remove_water_heater_from_project(proj, "Test Water Heater")

    assert len(result.swhSystem) == 0


def test_get_water_heater_keys_from_project(project: ComBuilding):
    proj = _fresh(project)
    swh = _get_test_water_heater()
    swh.description = "Test Water Heater"
    proj = mech_ops.add_water_heater_to_project(proj, swh)

    keys = mech_ops.get_water_heater_keys_from_project(proj)

    assert len(keys) == 1
    assert keys[0]["description"] == "Test Water Heater"
    assert "swhSystemType" in keys[0]
    assert "fuelType" in keys[0]


# ---------------------------------------------------------------------------
# Round-trip and validation tests
# ---------------------------------------------------------------------------


def test_mechanical_round_trip(project: ComBuilding):
    """Build a project with all four mechanical lists, dump, and validate."""
    proj = _fresh(project)

    # Add HVAC system
    hvac = _get_test_hvac_system()
    hvac.description = "RTU-1"
    proj = mech_ops.add_hvac_system_to_project(proj, hvac)

    # Add fan system
    fan_sys = _get_test_fan_system()
    fan_sys.description = "Supply Fan"
    proj = mech_ops.add_fan_system_to_project(proj, fan_sys)

    # Add fan to fan system
    fan = _get_test_fan()
    fan.description = "Fan 1"
    proj = mech_ops.add_fan_to_fan_system(proj, "Supply Fan", fan)

    # Assign fan system to HVAC
    proj = mech_ops.assign_fan_system_to_hvac_system(proj, "RTU-1", "Supply Fan")

    # Add plant
    plant = _get_test_hvac_plant()
    plant.description = "Chiller 1"
    proj = mech_ops.add_hvac_plant_to_project(proj, plant)

    # Add a water heater
    swh = _get_test_water_heater()
    swh.description = "Water Heater 1"
    proj = mech_ops.add_water_heater_to_project(proj, swh)

    # Round-trip through JSON
    dumped = proj.model_dump(mode="json")
    reloaded = ComBuilding.model_validate(dumped)

    # Verify structure
    assert reloaded.hvac.hvacSystem[0].description == "RTU-1"
    assert reloaded.hvac.fanSystem[0].description == "Supply Fan"
    assert len(reloaded.hvac.fanSystem[0].fan) == 1
    assert reloaded.hvac.hvacPlant[0].description == "Chiller 1"
    assert reloaded.swhSystem[0].description == "Water Heater 1"

    # Verify the fan system link exists and matches
    # Note: fanSystemKey should be a valid UUID string
    original_fan_key = proj.hvac.fanSystem[0].fanSystemKey
    reloaded_fan_key = reloaded.hvac.fanSystem[0].fanSystemKey
    reloaded_hvac_key = reloaded.hvac.hvacSystem[0].fanSystemKey

    # Both should have the same UUID
    assert original_fan_key is not None
    assert reloaded_fan_key == original_fan_key
    assert reloaded_hvac_key == original_fan_key
