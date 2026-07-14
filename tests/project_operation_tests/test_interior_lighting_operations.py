"""Tests for project_interior_lighting_operations."""

import pytest

from comcheck_api.defaults import (
    get_default_interior_lighting_space_template,
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


def test_add_activity_use(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    activity_use = get_default_interior_lighting_space_template()
    activity_use.areaDescription = "Office space"

    result = il_ops.add_interior_lighting_space_to_project(proj, area_key, activity_use)

    keys = il_ops.get_interior_lighting_space_keys_from_project(result, area_key)
    descriptions = [k["areaDescription"] for k in keys]
    assert "Office space" in descriptions


def test_add_activity_use_sets_key(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    activity_use = get_default_interior_lighting_space_template()

    result = il_ops.add_interior_lighting_space_to_project(proj, area_key, activity_use)

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    added = area.activityUse[-1]
    assert added.key == area_key


def test_update_activity_use(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    activity_use = get_default_interior_lighting_space_template()
    activity_use.areaDescription = "Conference room"
    proj = il_ops.add_interior_lighting_space_to_project(proj, area_key, activity_use)

    result = il_ops.update_interior_lighting_space_in_project(
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
    updated_au = next(
        au for au in area.activityUse if au.areaDescription == "Conference room"
    )
    assert updated_au.floorArea == 2500.0
    assert (
        updated_au.activityType == ActivityTypeOptions.ACTIVITY_COMMON_CONFERENCE_HALL
    )


def test_remove_activity_use(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    activity_use = get_default_interior_lighting_space_template()
    activity_use.areaDescription = "Storage room"
    proj = il_ops.add_interior_lighting_space_to_project(proj, area_key, activity_use)

    result = il_ops.remove_interior_lighting_space_from_project(
        proj, area_key, "Storage room"
    )

    keys = il_ops.get_interior_lighting_space_keys_from_project(result, area_key)
    assert "Storage room" not in [k["areaDescription"] for k in keys]


# ---------------------------------------------------------------------------
# Fixture editing via the ActivityUse payload
# ---------------------------------------------------------------------------


def test_add_fixture_via_activity_use_update(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    activity_use = get_default_interior_lighting_space_template()
    activity_use.areaDescription = "Lab"
    proj = il_ops.add_interior_lighting_space_to_project(proj, area_key, activity_use)

    fixture = get_default_fixture_template()
    fixture.description = "Lab LED"
    fixture.fixtureWattage = 48.0

    # Retrieve the current activityUse, append the fixture, then update
    whole_use = proj.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    au = next(au for au in area.activityUse if au.areaDescription == "Lab")

    updated_space = au.interiorLightingSpace.model_copy(
        deep=True,
        update={"fixture": [fixture]},
    )
    result = il_ops.update_interior_lighting_space_in_project(
        proj,
        area_key,
        "Lab",
        {
            "interiorLightingSpace": updated_space.model_dump(
                mode="python", exclude_unset=True
            )
        },
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    au = next(au for au in area.activityUse if au.areaDescription == "Lab")
    fixtures = au.interiorLightingSpace.fixture or []
    assert len(fixtures) == 1
    assert fixtures[0].description == "Lab LED"
    assert fixtures[0].fixtureWattage == 48.0


def test_remove_fixture_by_omitting_from_update(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    activity_use = get_default_interior_lighting_space_template()
    activity_use.areaDescription = "Lobby"
    fixture = get_default_fixture_template()
    fixture.description = "Lobby fixture"
    activity_use.interiorLightingSpace = activity_use.interiorLightingSpace.model_copy(
        deep=True, update={"fixture": [fixture]}
    )
    proj = il_ops.add_interior_lighting_space_to_project(proj, area_key, activity_use)

    # Update with empty fixture list — effectively removes all fixtures
    result = il_ops.update_interior_lighting_space_in_project(
        proj,
        area_key,
        "Lobby",
        {"interiorLightingSpace": {"fixture": []}},
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    au = next(au for au in area.activityUse if au.areaDescription == "Lobby")
    assert (au.interiorLightingSpace.fixture or []) == []


def test_fixture_fields_preserved_on_activity_use_update(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    activity_use = get_default_interior_lighting_space_template()
    activity_use.areaDescription = "Gym"
    fixture = get_default_fixture_template()
    fixture.description = "Gym LED"
    fixture.lightingType = LightingTypeOptions.LED
    fixture.quantity = 4
    activity_use.interiorLightingSpace = activity_use.interiorLightingSpace.model_copy(
        deep=True, update={"fixture": [fixture]}
    )
    proj = il_ops.add_interior_lighting_space_to_project(proj, area_key, activity_use)

    # Update only the floorArea — fixtures must be untouched
    result = il_ops.update_interior_lighting_space_in_project(
        proj, area_key, "Gym", {"floorArea": 3000.0}
    )

    whole_use = result.get_by_path("lighting.wholeBldgUse")
    area = next(a for a in whole_use if a.key == area_key)
    au = next(au for au in area.activityUse if au.areaDescription == "Gym")
    fixtures = au.interiorLightingSpace.fixture or []
    assert len(fixtures) == 1
    assert fixtures[0].description == "Gym LED"
    assert fixtures[0].quantity == 4


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_add_activity_use_invalid_building_area(project: ComBuilding):
    with pytest.raises(ValueError, match="not found"):
        il_ops.add_interior_lighting_space_to_project(
            project, "nonexistent-key", get_default_interior_lighting_space_template()
        )


def test_update_activity_use_not_found(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    with pytest.raises(ValueError, match="not found"):
        il_ops.update_interior_lighting_space_in_project(
            proj, area_key, "Nonexistent space", {"floorArea": 100.0}
        )


def test_remove_activity_use_not_found(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    with pytest.raises(ValueError, match="not found"):
        il_ops.remove_interior_lighting_space_from_project(
            proj, area_key, "Nonexistent space"
        )


# ---------------------------------------------------------------------------
# get_interior_lighting_space_keys_from_project
# ---------------------------------------------------------------------------


def test_get_activity_use_keys_empty(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    result = il_ops.get_interior_lighting_space_keys_from_project(proj, area_key)
    assert result == []


def test_get_activity_use_keys_unknown_area(project: ComBuilding):
    result = il_ops.get_interior_lighting_space_keys_from_project(
        project, "nonexistent-key"
    )
    assert result == []


def test_get_activity_use_keys_returns_all(project: ComBuilding):
    proj, area_key = _fresh_project_with_area(project)
    for desc in ["Space A", "Space B"]:
        au = get_default_interior_lighting_space_template()
        au.areaDescription = desc
        proj = il_ops.add_interior_lighting_space_to_project(proj, area_key, au)

    keys = il_ops.get_interior_lighting_space_keys_from_project(proj, area_key)
    descriptions = [k["areaDescription"] for k in keys]
    assert "Space A" in descriptions
    assert "Space B" in descriptions
