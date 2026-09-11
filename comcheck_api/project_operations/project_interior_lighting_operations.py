"""Project Interior Lighting Operations.

Manages interior lighting at the InteriorSpace granularity.  In the COMcheck
API schema, an interior lighting space is represented by the ``ActivityUse``
model (``lighting.wholeBldgUse[i].activityUse[]``).  Each InteriorSpace carries
exactly one (singleton) InteriorLightingSpace whose fixture[] holds the
fixtures.  Fixtures can be batch added, updated, and/or removed via
update_fixtures_in_interior_space, matched by fixtureType (the
schema-documented uniqueness key for fixtures within a lighting space, not
id).  You can also edit the InteriorSpace's interiorLightingSpace.fixture[]
list directly and pass the whole InteriorSpace through
update_interior_space_in_project.
"""

from typing import Any

from comcheck_api.constants.interior_lighting_constants import (
    DEFAULT_INTERIOR_SPACE_AREA,
)
from comcheck_api.types.common_types import InteriorSpace
from comcheck_api.types.core_types import ComBuilding, Fixture, WholeBldgUse
from comcheck_api.utilities.project_utilities import (
    _require_activity_use,
    merge_fixtures,
)


def _find_building_area(project: ComBuilding, building_area_key: str) -> WholeBldgUse:
    """Return the WholeBldgUse with the given key, or raise."""
    whole_use = project.lighting.wholeBldgUse if project.lighting else []
    area = next(
        (area for area in whole_use if area.key == building_area_key),
        None,
    )
    if area is None:
        raise ValueError(
            f"Building area key '{building_area_key}' not found in lighting.wholeBldgUse."
        )
    return area


def add_interior_space_to_project(
    project: ComBuilding,
    building_area_key: str,
    new_interior_space: InteriorSpace,
) -> ComBuilding:
    """Add a new InteriorSpace (interior lighting space) to a building area.

    Each interior lighting space is stored as an ``ActivityUse`` object in the
    COMcheck API schema (``lighting.wholeBldgUse[i].activityUse[]``),
    aliased as :class:`~comcheck_api.types.common_types.InteriorSpace`.

    Fixtures and the singleton InteriorLightingSpace are carried inside
    new_interior_space — populate interiorLightingSpace.fixture[] before
    passing if you want fixtures on creation.  The activityUse.key is
    automatically set to building_area_key.

    Args:
        project: The project to modify.
        building_area_key: Key of the WholeBldgUse to add the InteriorSpace to.
        new_interior_space: The :class:`~comcheck_api.types.common_types.InteriorSpace`
            to add (represents one interior lighting space in the web app).
            Use :func:`~comcheck_api.defaults.get_default_interior_space_template`
            as a starting point.

    Returns:
        Updated project with the new InteriorSpace added.
    """
    updated_project = project.model_copy(deep=True)

    area = _find_building_area(updated_project, building_area_key)

    # Ensure the activityUse.key matches its parent building area key
    new_interior_space = new_interior_space.model_copy(
        deep=True, update={"key": building_area_key}
    )

    # Ensure interiorLightingSpace is initialized
    if new_interior_space.interiorLightingSpace is None:
        new_interior_space = new_interior_space.model_copy(
            deep=True,
            update={
                "interiorLightingSpace": DEFAULT_INTERIOR_SPACE_AREA.interiorLightingSpace.model_copy(
                    deep=True
                )
            },
        )

    area.append_subcomponent(new_interior_space)

    return updated_project


def update_interior_space_in_project(
    project: ComBuilding,
    building_area_key: str,
    area_description: str,
    updates: dict[str, Any] | InteriorSpace,
) -> ComBuilding:
    """Update an existing InteriorSpace (interior lighting space) in a building area.

    To add, change, or remove fixtures: set the desired
    interiorLightingSpace.fixture[] on the updates dict (or the full
    InteriorSpace object) before calling this function.

    Args:
        project: The project to modify.
        building_area_key: Key of the WholeBldgUse that owns this InteriorSpace.
        area_description: The ``areaDescription`` of the
            :class:`~comcheck_api.types.common_types.InteriorSpace` to update.
        updates: Partial updates (dict) or a full
            :class:`~comcheck_api.types.common_types.InteriorSpace` to apply.

    Returns:
        Updated project with the InteriorSpace modified.
    """
    _require_activity_use(project, building_area_key, area_description)

    updated_project = project.model_copy(deep=True)
    area = _find_building_area(updated_project, building_area_key)

    area.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=area_description,
        subcomponent_name="activityUse",
    )

    return updated_project


def remove_interior_space_from_project(
    project: ComBuilding,
    building_area_key: str,
    area_description: str,
) -> ComBuilding:
    """Remove an InteriorSpace (interior lighting space) and its fixtures from a building area.

    Args:
        project: The project to modify.
        building_area_key: Key of the WholeBldgUse that owns this InteriorSpace.
        area_description: The ``areaDescription`` of the
            :class:`~comcheck_api.types.common_types.InteriorSpace` to remove.

    Returns:
        Updated project with the InteriorSpace removed.
    """
    _require_activity_use(project, building_area_key, area_description)

    updated_project = project.model_copy(deep=True)
    area = _find_building_area(updated_project, building_area_key)

    area.remove_from_subcomponent_list(
        subcomponent_id=area_description,
        subcomponent_name="activityUse",
    )

    return updated_project


def update_fixtures_in_interior_space(
    project: ComBuilding,
    building_area_key: str,
    area_description: str,
    upserts: list[Fixture | dict] = [],
    remove_fixture_types: list[str] = [],
) -> ComBuilding:
    """Batch add, update, and/or remove fixtures on an interior lighting space.

    Fixtures are matched by ``fixtureType`` (the schema-documented uniqueness
    key for fixtures within a lighting space), not ``id``. Removals are
    applied first; each upsert then replaces the existing fixture with the
    same fixtureType, or is appended as new.

    Args:
        project: The project to modify.
        building_area_key: Key of the WholeBldgUse that owns this InteriorSpace.
        area_description: The areaDescription of the InteriorSpace to update.
        upserts: Fixtures to add or update, matched by fixtureType.
        remove_fixture_types: fixtureType values of fixtures to remove.

    Returns:
        Updated project with the InteriorSpace's fixture[] list modified.

    Raises:
        ValueError: If two upserts share a fixtureType, or a
            remove_fixture_types entry does not match any current fixture.
    """
    _require_activity_use(project, building_area_key, area_description)

    updated_project = project.model_copy(deep=True)
    area = _find_building_area(updated_project, building_area_key)
    interior_space = next(
        space for space in area.activityUse if space.areaDescription == area_description
    )

    updated_fixtures = merge_fixtures(
        current_fixtures=interior_space.interiorLightingSpace.fixture or [],
        upserts=upserts,
        remove_fixture_types=remove_fixture_types,
    )

    # interiorLightingSpace must be dumped in full — update_subcomponent_list
    # merges at the ActivityUse level, so a partial {"fixture": [...]} dict
    # would wholesale-replace interiorLightingSpace and wipe its other fields.
    updated_space = interior_space.interiorLightingSpace.model_copy(
        deep=True, update={"fixture": updated_fixtures}
    )

    area.update_subcomponent_list(
        subcomponent_updates={
            "interiorLightingSpace": updated_space.model_dump(mode="python")
        },
        subcomponent_id=area_description,
        subcomponent_name="activityUse",
    )

    return updated_project


def get_interior_space_keys_from_project(
    project: ComBuilding, building_area_key: str
) -> list[dict]:
    """Return identifying fields for all InteriorSpace items in a building area.

    Args:
        project: The project to query.
        building_area_key: Key of the WholeBldgUse to query.

    Returns:
        List of dicts with keys ``areaDescription`` and ``activityType``
        for each :class:`~comcheck_api.types.common_types.InteriorSpace` in the
        building area.
    """
    whole_use = project.get_by_path("lighting.wholeBldgUse")
    if not isinstance(whole_use, list):
        return []

    area = next(
        (area for area in whole_use if getattr(area, "key", None) == building_area_key),
        None,
    )
    if area is None:
        return []

    interior_spaces = getattr(area, "activityUse", []) or []
    return [
        {
            "areaDescription": getattr(interior_space, "areaDescription", None),
            "activityType": getattr(interior_space, "activityType", None),
        }
        for interior_space in interior_spaces
    ]
