"""Tests for project_interior_lighting_operations."""

import pytest

from comcheck_api.defaults import (
    get_default_interior_space_template,
    get_default_building_area_template,
    get_default_fixture_template,
)
from comcheck_api.project_operations import (
    project_building_area_operations,
    project_interior_lighting_operations as il_ops,
)
from comcheck_api.types.core_types import (
    ActivityTypeOptions,
    ComBuilding,
    LightingTypeOptions,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_project_with_area(project: ComBuilding) -> tuple[ComBuilding, str]:
    """Return a deep-copy of project with one new building area added."""
    proj = project.model_copy(deep=True)
    area = get_default_building_area_template()
    proj = project_building_area_operations.add_building_area_to_project(proj, area)
    return proj, area.key


# ---------------------------------------------------------------------------
# Lifecycle: add / update / remove
# ---------------------------------------------------------------------------


def test_add_interior_space(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    interior_space = get_default_interior_space_template()
    interior_space.areaDescription = "Office space"

    result = il_ops.add_interior_space_to_project(proj, area_key, interior_space)

    keys = il_ops.get_interior_space_keys_from_project(result, area_key)
    descriptions = [k["areaDescription"] for k in keys]
    assert "Office space" in descriptions


def test_add_interior_space_sets_key(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    interior_space = get_default_interior_space_template()

    result = il_ops.add_interior_space_to_project(proj, area_key, interior_space)

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    added = area.activityUse[-1]
    assert added.key == area_key


def test_update_interior_space(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    interior_space = get_default_interior_space_template()
    interior_space.areaDescription = "Conference room"
    proj = il_ops.add_interior_space_to_project(proj, area_key, interior_space)

    result = il_ops.update_interior_space_in_project(
        proj,
        area_key,
        "Conference room",
        {
            "floorArea": 2500.0,
            "activityType": ActivityTypeOptions.ACTIVITY_COMMON_CONFERENCE_HALL,
        },
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    updated_ia = next(
        ia for ia in area.activityUse if ia.areaDescription == "Conference room"
    )
    assert updated_ia.floorArea == 2500.0
    assert (
        updated_ia.activityType == ActivityTypeOptions.ACTIVITY_COMMON_CONFERENCE_HALL
    )


def test_remove_interior_space(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    interior_space = get_default_interior_space_template()
    interior_space.areaDescription = "Storage room"
    proj = il_ops.add_interior_space_to_project(proj, area_key, interior_space)

    result = il_ops.remove_interior_space_from_project(proj, area_key, "Storage room")

    keys = il_ops.get_interior_space_keys_from_project(result, area_key)
    assert "Storage room" not in [k["areaDescription"] for k in keys]


# ---------------------------------------------------------------------------
# Fixture editing via the InteriorSpace payload
# ---------------------------------------------------------------------------


def test_add_fixture_via_interior_space_update(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    interior_space = get_default_interior_space_template()
    interior_space.areaDescription = "Lab"
    proj = il_ops.add_interior_space_to_project(proj, area_key, interior_space)

    fixture = get_default_fixture_template()
    fixture.description = "Lab LED"
    fixture.fixtureWattage = 48.0

    # Retrieve the current activityUse, append the fixture, then update
    whole_use = proj.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == "Lab")

    updated_space = ia.interiorLightingSpace.model_copy(
        deep=True,
        update={"fixture": [fixture]},
    )
    result = il_ops.update_interior_space_in_project(
        proj,
        area_key,
        "Lab",
        {"interiorLightingSpace": updated_space.model_dump(mode="python")},
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == "Lab")
    fixtures = ia.interiorLightingSpace.fixture or []
    assert len(fixtures) == 1
    assert fixtures[0].description == "Lab LED"
    assert fixtures[0].fixtureWattage == 48.0


def test_remove_fixture_by_omitting_from_update(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    interior_space = get_default_interior_space_template()
    interior_space.areaDescription = "Lobby"
    fixture = get_default_fixture_template()
    fixture.description = "Lobby fixture"
    interior_space.interiorLightingSpace = (
        interior_space.interiorLightingSpace.model_copy(
            deep=True, update={"fixture": [fixture]}
        )
    )
    proj = il_ops.add_interior_space_to_project(proj, area_key, interior_space)

    # Update with empty fixture list — effectively removes all fixtures
    result = il_ops.update_interior_space_in_project(
        proj,
        area_key,
        "Lobby",
        {"interiorLightingSpace": {"fixture": []}},
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == "Lobby")
    assert (ia.interiorLightingSpace.fixture or []) == []


def test_fixture_fields_preserved_on_interior_space_update(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    interior_space = get_default_interior_space_template()
    interior_space.areaDescription = "Gym"
    fixture = get_default_fixture_template()
    fixture.description = "Gym LED"
    fixture.lightingType = LightingTypeOptions.LED
    fixture.quantity = 4
    interior_space.interiorLightingSpace = (
        interior_space.interiorLightingSpace.model_copy(
            deep=True, update={"fixture": [fixture]}
        )
    )
    proj = il_ops.add_interior_space_to_project(proj, area_key, interior_space)

    # Update only the floorArea — fixtures must be untouched
    result = il_ops.update_interior_space_in_project(
        proj, area_key, "Gym", {"floorArea": 3000.0}
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == "Gym")
    fixtures = ia.interiorLightingSpace.fixture or []
    assert len(fixtures) == 1
    assert fixtures[0].description == "Gym LED"
    assert fixtures[0].quantity == 4


# ---------------------------------------------------------------------------
# update_fixtures_in_interior_space (batch)
# ---------------------------------------------------------------------------


def _add_space_with_fixtures(
    proj: ComBuilding, area_key: str, area_description: str, fixture_types: list[str]
) -> ComBuilding:
    interior_space = get_default_interior_space_template()
    interior_space.areaDescription = area_description
    fixtures = []
    for fixture_type in fixture_types:
        fixture = get_default_fixture_template()
        fixture.fixtureType = fixture_type
        fixtures.append(fixture)
    interior_space.interiorLightingSpace = (
        interior_space.interiorLightingSpace.model_copy(
            deep=True, update={"fixture": fixtures}
        )
    )
    return il_ops.add_interior_space_to_project(proj, area_key, interior_space)


def _fixture_types(proj: ComBuilding, area_key: str, area_description: str) -> set[str]:
    whole_use = proj.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == area_description)
    return {f.fixtureType for f in ia.interiorLightingSpace.fixture or []}


def test_batch_add_fixtures(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(proj, area_key, "Office", [])

    new_fixture = get_default_fixture_template()
    new_fixture.fixtureType = "Fixture A"

    result = il_ops.update_fixtures_in_interior_space(
        proj, area_key, "Office", upserts=[new_fixture]
    )

    assert _fixture_types(result, area_key, "Office") == {"Fixture A"}


def test_batch_update_existing_fixture_by_fixture_type(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(proj, area_key, "Office", ["Fixture A"])

    replacement = get_default_fixture_template()
    replacement.fixtureType = "Fixture A"
    replacement.fixtureWattage = 99.0

    result = il_ops.update_fixtures_in_interior_space(
        proj, area_key, "Office", upserts=[replacement]
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == "Office")
    fixtures = ia.interiorLightingSpace.fixture
    assert len(fixtures) == 1
    assert fixtures[0].fixtureWattage == 99.0


def test_batch_remove_fixtures(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(
        proj, area_key, "Office", ["Fixture A", "Fixture B"]
    )

    result = il_ops.update_fixtures_in_interior_space(
        proj, area_key, "Office", remove_fixture_types=["Fixture A"]
    )

    assert _fixture_types(result, area_key, "Office") == {"Fixture B"}


def test_batch_add_update_remove_together(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(
        proj, area_key, "Office", ["Fixture A", "Fixture B"]
    )

    updated_b = get_default_fixture_template()
    updated_b.fixtureType = "Fixture B"
    updated_b.quantity = 10
    new_c = get_default_fixture_template()
    new_c.fixtureType = "Fixture C"

    result = il_ops.update_fixtures_in_interior_space(
        proj,
        area_key,
        "Office",
        upserts=[updated_b, new_c],
        remove_fixture_types=["Fixture A"],
    )

    assert _fixture_types(result, area_key, "Office") == {"Fixture B", "Fixture C"}


def test_batch_fixture_other_space_fields_preserved(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(proj, area_key, "Office", ["Fixture A"])
    whole_use = proj.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == "Office")
    ia.interiorLightingSpace.description = "Main office lighting"

    new_fixture = get_default_fixture_template()
    new_fixture.fixtureType = "Fixture D"

    result = il_ops.update_fixtures_in_interior_space(
        proj, area_key, "Office", upserts=[new_fixture]
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    ia = next(ia for ia in area.activityUse if ia.areaDescription == "Office")
    assert ia.interiorLightingSpace.description == "Main office lighting"


def test_batch_fixture_duplicate_upsert_fixture_types_raises(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(proj, area_key, "Office", [])

    dup1 = get_default_fixture_template()
    dup1.fixtureType = "Fixture A"
    dup2 = get_default_fixture_template()
    dup2.fixtureType = "Fixture A"

    with pytest.raises(ValueError, match="Duplicate fixtureType"):
        il_ops.update_fixtures_in_interior_space(
            proj, area_key, "Office", upserts=[dup1, dup2]
        )


def test_batch_fixture_remove_unknown_fixture_type_raises(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(proj, area_key, "Office", ["Fixture A"])

    with pytest.raises(ValueError, match="not found for removal"):
        il_ops.update_fixtures_in_interior_space(
            proj, area_key, "Office", remove_fixture_types=["Nonexistent"]
        )


def test_batch_fixture_does_not_mutate_original(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    proj = _add_space_with_fixtures(proj, area_key, "Office", ["Fixture A"])

    new_fixture = get_default_fixture_template()
    new_fixture.fixtureType = "Fixture B"

    il_ops.update_fixtures_in_interior_space(
        proj, area_key, "Office", upserts=[new_fixture]
    )

    assert _fixture_types(proj, area_key, "Office") == {"Fixture A"}


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_add_interior_space_invalid_building_area(project: ComBuilding):
    with pytest.raises(ValueError, match="not found"):
        il_ops.add_interior_space_to_project(
            project, "nonexistent-key", get_default_interior_space_template()
        )


def test_update_interior_space_not_found(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    with pytest.raises(ValueError, match="not found"):
        il_ops.update_interior_space_in_project(
            proj, area_key, "Nonexistent space", {"floorArea": 100.0}
        )


def test_remove_interior_space_not_found(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    with pytest.raises(ValueError, match="not found"):
        il_ops.remove_interior_space_from_project(proj, area_key, "Nonexistent space")


# ---------------------------------------------------------------------------
# get_interior_space_keys_from_project
# ---------------------------------------------------------------------------


def test_get_interior_space_keys_empty(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    result = il_ops.get_interior_space_keys_from_project(proj, area_key)
    assert result == []


def test_get_interior_space_keys_unknown_area(project: ComBuilding):
    result = il_ops.get_interior_space_keys_from_project(project, "nonexistent-key")
    assert result == []


def test_get_interior_space_keys_returns_all(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    for desc in ["Space A", "Space B"]:
        ia = get_default_interior_space_template()
        ia.areaDescription = desc
        proj = il_ops.add_interior_space_to_project(proj, area_key, ia)

    keys = il_ops.get_interior_space_keys_from_project(proj, area_key)
    descriptions = [k["areaDescription"] for k in keys]
    assert "Space A" in descriptions
    assert "Space B" in descriptions
