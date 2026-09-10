"""Tests for project_exterior_lighting_operations."""

import pytest

from comcheck_api.defaults import (
    get_default_exterior_area_template,
    get_default_fixture_template,
)
from comcheck_api.project_operations import (
    project_exterior_lighting_operations as el_ops,
)
from comcheck_api.types.core_types import (
    ComBuilding,
    ExteriorLightingZoneTypeOptions,
    ExteriorUseTypeOptions,
    LightingTypeOptions,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh(project: ComBuilding) -> ComBuilding:
    return project.model_copy(deep=True)


# ---------------------------------------------------------------------------
# set_exterior_lighting_zone_type_in_project
# ---------------------------------------------------------------------------


def test_set_zone_type(project: ComBuilding):
    result = el_ops.set_exterior_lighting_zone_type_in_project(
        project, ExteriorLightingZoneTypeOptions.EXT_ZONE_METRO_COMMERCIAL
    )
    assert (
        result.lighting.exteriorLightingZoneType
        == ExteriorLightingZoneTypeOptions.EXT_ZONE_METRO_COMMERCIAL
    )


def test_set_zone_type_rejects_unspecified(project: ComBuilding):
    with pytest.raises(ValueError, match="EXT_ZONE_UNSPECIFIED"):
        el_ops.set_exterior_lighting_zone_type_in_project(
            project, ExteriorLightingZoneTypeOptions.EXT_ZONE_UNSPECIFIED
        )


def test_set_zone_type_rejects_non_enum(project: ComBuilding):
    with pytest.raises(TypeError):
        el_ops.set_exterior_lighting_zone_type_in_project(project, "EXT_ZONE_RURAL")


def test_set_zone_type_does_not_mutate_original(project: ComBuilding):
    proj = _fresh(project)
    original_zone = proj.lighting.exteriorLightingZoneType
    el_ops.set_exterior_lighting_zone_type_in_project(
        proj, ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    assert proj.lighting.exteriorLightingZoneType == original_zone


# ---------------------------------------------------------------------------
# add_exterior_area_to_project
# ---------------------------------------------------------------------------


def test_add_exterior_area(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    ea = get_default_exterior_area_template()
    ea.areaDescription = "Parking lot"

    result = el_ops.add_exterior_area_to_project(proj, ea)

    keys = el_ops.get_exterior_area_keys_from_project(result)
    assert any(k["areaDescription"] == "Parking lot" for k in keys)


def test_add_exterior_area_warns_when_zone_unspecified(project: ComBuilding):
    proj = _fresh(project)
    # Force zone to unspecified directly
    proj.lighting.exteriorLightingZoneType = (
        ExteriorLightingZoneTypeOptions.EXT_ZONE_UNSPECIFIED
    )

    ea = get_default_exterior_area_template()
    ea.areaDescription = "Entry"

    with pytest.warns(UserWarning, match="EXT_ZONE_UNSPECIFIED"):
        el_ops.add_exterior_area_to_project(proj, ea)


def test_add_exterior_area_does_not_mutate_original(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    original_count = len(proj.lighting.exteriorUse)
    ea = get_default_exterior_area_template()
    el_ops.add_exterior_area_to_project(proj, ea)
    assert len(proj.lighting.exteriorUse) == original_count


# ---------------------------------------------------------------------------
# update_exterior_area_in_project
# ---------------------------------------------------------------------------


def test_update_exterior_area(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    ea = get_default_exterior_area_template()
    ea.areaDescription = "Loading dock"
    proj = el_ops.add_exterior_area_to_project(proj, ea)

    result = el_ops.update_exterior_area_in_project(
        proj,
        "Loading dock",
        {
            "useQuantity": 500.0,
            "exteriorType": ExteriorUseTypeOptions.EXTERIOR_LOADING_DOCK,
        },
    )

    exterior_areas = result.get_by_path("lighting.exteriorUse")
    updated = next(e for e in exterior_areas if e.areaDescription == "Loading dock")
    assert updated.useQuantity == 500.0
    assert updated.exteriorType == ExteriorUseTypeOptions.EXTERIOR_LOADING_DOCK


def test_update_exterior_area_not_found(project: ComBuilding):
    with pytest.raises(ValueError, match="not found"):
        el_ops.update_exterior_area_in_project(
            _fresh(project), "Nonexistent", {"useQuantity": 100.0}
        )


# ---------------------------------------------------------------------------
# remove_exterior_area_from_project
# ---------------------------------------------------------------------------


def test_remove_exterior_area(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    ea = get_default_exterior_area_template()
    ea.areaDescription = "Walkway"
    proj = el_ops.add_exterior_area_to_project(proj, ea)

    result = el_ops.remove_exterior_area_from_project(proj, "Walkway")

    keys = el_ops.get_exterior_area_keys_from_project(result)
    assert not any(k["areaDescription"] == "Walkway" for k in keys)


def test_remove_exterior_area_not_found(project: ComBuilding):
    with pytest.raises(ValueError, match="not found"):
        el_ops.remove_exterior_area_from_project(_fresh(project), "Nonexistent")


# ---------------------------------------------------------------------------
# Fixture editing via the ExteriorArea payload
# ---------------------------------------------------------------------------


def test_add_fixture_via_exterior_area_update(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    ea = get_default_exterior_area_template()
    ea.areaDescription = "Canopy"
    proj = el_ops.add_exterior_area_to_project(proj, ea)

    fixture = get_default_fixture_template()
    fixture.description = "Canopy LED"
    fixture.fixtureWattage = 60.0

    exterior_areas = proj.get_by_path("lighting.exteriorUse")
    added_ea = next(e for e in exterior_areas if e.areaDescription == "Canopy")
    updated_space = added_ea.exteriorLightingSpace.model_copy(
        deep=True, update={"fixture": [fixture]}
    )
    result = el_ops.update_exterior_area_in_project(
        proj,
        "Canopy",
        {"exteriorLightingSpace": updated_space.model_dump(mode="python")},
    )

    exterior_areas = result.get_by_path("lighting.exteriorUse")
    updated_ea = next(e for e in exterior_areas if e.areaDescription == "Canopy")
    fixtures = updated_ea.exteriorLightingSpace.fixture or []
    assert len(fixtures) == 1
    assert fixtures[0].description == "Canopy LED"
    assert fixtures[0].fixtureWattage == 60.0


def test_fixture_fields_preserved_on_exterior_area_update(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    ea = get_default_exterior_area_template()
    ea.areaDescription = "Plaza"
    fixture = get_default_fixture_template()
    fixture.description = "Plaza LED"
    fixture.quantity = 6
    ea.exteriorLightingSpace = ea.exteriorLightingSpace.model_copy(
        deep=True, update={"fixture": [fixture]}
    )
    proj = el_ops.add_exterior_area_to_project(proj, ea)

    # Update only useQuantity — fixtures must be untouched
    result = el_ops.update_exterior_area_in_project(
        proj, "Plaza", {"useQuantity": 800.0}
    )

    exterior_areas = result.get_by_path("lighting.exteriorUse")
    updated_ea = next(e for e in exterior_areas if e.areaDescription == "Plaza")
    fixtures = updated_ea.exteriorLightingSpace.fixture or []
    assert len(fixtures) == 1
    assert fixtures[0].description == "Plaza LED"
    assert fixtures[0].quantity == 6


def test_remove_fixture_by_omitting_from_update(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    ea = get_default_exterior_area_template()
    ea.areaDescription = "Driveway"
    fixture = get_default_fixture_template()
    fixture.description = "Driveway LED"
    ea.exteriorLightingSpace = ea.exteriorLightingSpace.model_copy(
        deep=True, update={"fixture": [fixture]}
    )
    proj = el_ops.add_exterior_area_to_project(proj, ea)

    result = el_ops.update_exterior_area_in_project(
        proj, "Driveway", {"exteriorLightingSpace": {"fixture": []}}
    )

    exterior_areas = result.get_by_path("lighting.exteriorUse")
    updated_ea = next(e for e in exterior_areas if e.areaDescription == "Driveway")
    assert (updated_ea.exteriorLightingSpace.fixture or []) == []


# ---------------------------------------------------------------------------
# get_exterior_area_keys_from_project
# ---------------------------------------------------------------------------


def test_get_exterior_area_keys_empty(project: ComBuilding):
    proj = _fresh(project)
    proj.lighting.exteriorUse = []
    result = el_ops.get_exterior_area_keys_from_project(proj)
    assert result == []


def test_get_exterior_area_keys_returns_all(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    for desc in ["Entry A", "Entry B"]:
        ea = get_default_exterior_area_template()
        ea.areaDescription = desc
        proj = el_ops.add_exterior_area_to_project(proj, ea)

    keys = el_ops.get_exterior_area_keys_from_project(proj)
    descriptions = [k["areaDescription"] for k in keys]
    assert "Entry A" in descriptions
    assert "Entry B" in descriptions
