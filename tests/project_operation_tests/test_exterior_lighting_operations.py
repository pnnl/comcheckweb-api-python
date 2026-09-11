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
# update_fixtures_in_exterior_area (batch)
# ---------------------------------------------------------------------------


def _add_area_with_fixtures(
    proj: ComBuilding, area_description: str, fixture_types: list[str]
) -> ComBuilding:
    ea = get_default_exterior_area_template()
    ea.areaDescription = area_description
    fixtures = []
    for fixture_type in fixture_types:
        fixture = get_default_fixture_template()
        fixture.fixtureType = fixture_type
        fixtures.append(fixture)
    ea.exteriorLightingSpace = ea.exteriorLightingSpace.model_copy(
        deep=True, update={"fixture": fixtures}
    )
    return el_ops.add_exterior_area_to_project(proj, ea)


def _fixture_types(proj: ComBuilding, area_description: str) -> set[str]:
    exterior_areas = proj.get_by_path("lighting.exteriorUse")
    area = next(e for e in exterior_areas if e.areaDescription == area_description)
    return {f.fixtureType for f in area.exteriorLightingSpace.fixture or []}


def test_batch_add_fixtures(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", [])

    new_fixture = get_default_fixture_template()
    new_fixture.fixtureType = "Fixture A"

    result = el_ops.update_fixtures_in_exterior_area(
        proj, "Canopy", upserts=[new_fixture]
    )

    assert _fixture_types(result, "Canopy") == {"Fixture A"}


def test_batch_update_existing_fixture_by_fixture_type(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", ["Fixture A"])

    replacement = get_default_fixture_template()
    replacement.fixtureType = "Fixture A"
    replacement.fixtureWattage = 99.0

    result = el_ops.update_fixtures_in_exterior_area(
        proj, "Canopy", upserts=[replacement]
    )

    exterior_areas = result.get_by_path("lighting.exteriorUse")
    area = next(e for e in exterior_areas if e.areaDescription == "Canopy")
    fixtures = area.exteriorLightingSpace.fixture
    assert len(fixtures) == 1
    assert fixtures[0].fixtureWattage == 99.0


def test_batch_remove_fixtures(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", ["Fixture A", "Fixture B"])

    result = el_ops.update_fixtures_in_exterior_area(
        proj, "Canopy", remove_fixture_types=["Fixture A"]
    )

    assert _fixture_types(result, "Canopy") == {"Fixture B"}


def test_batch_add_update_remove_together(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", ["Fixture A", "Fixture B"])

    updated_b = get_default_fixture_template()
    updated_b.fixtureType = "Fixture B"
    updated_b.quantity = 10
    new_c = get_default_fixture_template()
    new_c.fixtureType = "Fixture C"

    result = el_ops.update_fixtures_in_exterior_area(
        proj,
        "Canopy",
        upserts=[updated_b, new_c],
        remove_fixture_types=["Fixture A"],
    )

    assert _fixture_types(result, "Canopy") == {"Fixture B", "Fixture C"}


def test_batch_fixture_other_space_fields_preserved(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", ["Fixture A"])
    exterior_areas = proj.get_by_path("lighting.exteriorUse")
    area = next(e for e in exterior_areas if e.areaDescription == "Canopy")
    area.exteriorLightingSpace.description = "Canopy lighting"

    new_fixture = get_default_fixture_template()
    new_fixture.fixtureType = "Fixture D"

    result = el_ops.update_fixtures_in_exterior_area(
        proj, "Canopy", upserts=[new_fixture]
    )

    exterior_areas = result.get_by_path("lighting.exteriorUse")
    area = next(e for e in exterior_areas if e.areaDescription == "Canopy")
    assert area.exteriorLightingSpace.description == "Canopy lighting"


def test_batch_fixture_duplicate_upsert_fixture_types_raises(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", [])

    dup1 = get_default_fixture_template()
    dup1.fixtureType = "Fixture A"
    dup2 = get_default_fixture_template()
    dup2.fixtureType = "Fixture A"

    with pytest.raises(ValueError, match="Duplicate fixtureType"):
        el_ops.update_fixtures_in_exterior_area(proj, "Canopy", upserts=[dup1, dup2])


def test_batch_fixture_remove_unknown_fixture_type_raises(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", ["Fixture A"])

    with pytest.raises(ValueError, match="not found for removal"):
        el_ops.update_fixtures_in_exterior_area(
            proj, "Canopy", remove_fixture_types=["Nonexistent"]
        )


def test_batch_fixture_does_not_mutate_original(project: ComBuilding):
    proj = el_ops.set_exterior_lighting_zone_type_in_project(
        _fresh(project), ExteriorLightingZoneTypeOptions.EXT_ZONE_RURAL
    )
    proj = _add_area_with_fixtures(proj, "Canopy", ["Fixture A"])

    new_fixture = get_default_fixture_template()
    new_fixture.fixtureType = "Fixture B"

    el_ops.update_fixtures_in_exterior_area(proj, "Canopy", upserts=[new_fixture])

    assert _fixture_types(proj, "Canopy") == {"Fixture A"}


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
