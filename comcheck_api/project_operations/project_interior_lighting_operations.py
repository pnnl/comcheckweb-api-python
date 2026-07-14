"""Project Interior Lighting Operations.

Manages interior lighting at the ActivityUse granularity.  In the COMcheck
API schema, an interior lighting space is represented by the ``ActivityUse``
model (``lighting.wholeBldgUse[i].activityUse[]``).  Each ActivityUse carries
exactly one (singleton) InteriorLightingSpace whose fixture[] holds the
fixtures.  There are no fixture-level operations — to add, change, or remove a
fixture, edit the ActivityUse's interiorLightingSpace.fixture[] list and pass
the whole ActivityUse through update_interior_lighting_space_in_project.
"""

from typing import Any

from comcheck_api.constants.interior_lighting_constants import (
    DEFAULT_INTERIOR_LIGHTING_SPACE_AREA,
)
from comcheck_api.types.core_types import ActivityUse, ComBuilding
from comcheck_api.utilities.project_utilities import _require_activity_use


def _find_building_area(project: ComBuilding, building_area_key: str):
    """Return the WholeBldgUse with the given key, or raise."""
    whole_use = project.get_by_path("lighting.wholeBldgUse") or []
    area = next(
        (a for a in whole_use if getattr(a, "key", None) == building_area_key), None
    )
    if area is None:
        raise ValueError(
            f"Building area key '{building_area_key}' not found in lighting.wholeBldgUse."
        )
    return area


def add_interior_lighting_space_to_project(
    project: ComBuilding,
    building_area_key: str,
    new_activity_use: ActivityUse,
) -> ComBuilding:
    """Add a new interior lighting space (``ActivityUse``) to a building area.

    Each interior lighting space is stored as an ``ActivityUse`` object in the
    COMcheck API schema (``lighting.wholeBldgUse[i].activityUse[]``).

    Fixtures and the singleton InteriorLightingSpace are carried inside
    new_activity_use — populate interiorLightingSpace.fixture[] before
    passing if you want fixtures on creation.  The activityUse.key is
    automatically set to building_area_key.

    Args:
        project: The project to modify.
        building_area_key: Key of the WholeBldgUse to add the ActivityUse to.
        new_activity_use: The :class:`~comcheck_api.types.core_types.ActivityUse`
            to add (represents one interior lighting space in the web app).
            Use :func:`~comcheck_api.defaults.get_default_interior_lighting_space_template`
            as a starting point.

    Returns:
        Updated project with the new ActivityUse added.
    """
    updated_project = project.model_copy(deep=True)

    area = _find_building_area(updated_project, building_area_key)

    # Ensure the activityUse.key matches its parent building area key
    new_activity_use = new_activity_use.model_copy(
        deep=True, update={"key": building_area_key}
    )

    # Ensure interiorLightingSpace is initialized
    if new_activity_use.interiorLightingSpace is None:
        new_activity_use = new_activity_use.model_copy(
            deep=True,
            update={
                "interiorLightingSpace": DEFAULT_INTERIOR_LIGHTING_SPACE_AREA.interiorLightingSpace.model_copy(
                    deep=True
                )
            },
        )

    area.append_subcomponent(new_activity_use)

    return updated_project


def update_interior_lighting_space_in_project(
    project: ComBuilding,
    building_area_key: str,
    area_description: str,
    updates: dict[str, Any] | ActivityUse,
) -> ComBuilding:
    """Update an existing interior lighting space (``ActivityUse``) in a building area.

    To add, change, or remove fixtures: set the desired
    interiorLightingSpace.fixture[] on the updates dict (or the full
    ActivityUse object) before calling this function.

    Args:
        project: The project to modify.
        building_area_key: Key of the WholeBldgUse that owns this ActivityUse.
        area_description: The ``areaDescription`` of the
            :class:`~comcheck_api.types.core_types.ActivityUse` to update.
        updates: Partial updates (dict) or a full
            :class:`~comcheck_api.types.core_types.ActivityUse` to apply.

    Returns:
        Updated project with the ActivityUse modified.
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


def remove_interior_lighting_space_from_project(
    project: ComBuilding,
    building_area_key: str,
    area_description: str,
) -> ComBuilding:
    """Remove an interior lighting space (``ActivityUse``) and its fixtures from a building area.

    Args:
        project: The project to modify.
        building_area_key: Key of the WholeBldgUse that owns this ActivityUse.
        area_description: The ``areaDescription`` of the
            :class:`~comcheck_api.types.core_types.ActivityUse` to remove.

    Returns:
        Updated project with the ActivityUse removed.
    """
    _require_activity_use(project, building_area_key, area_description)

    updated_project = project.model_copy(deep=True)
    area = _find_building_area(updated_project, building_area_key)

    area.remove_from_subcomponent_list(
        subcomponent_id=area_description,
        subcomponent_name="activityUse",
    )

    return updated_project


def get_interior_lighting_space_keys_from_project(
    project: ComBuilding, building_area_key: str
) -> list[dict]:
    """Return identifying fields for all interior lighting spaces (``ActivityUse`` items) in a building area.

    Args:
        project: The project to query.
        building_area_key: Key of the WholeBldgUse to query.

    Returns:
        List of dicts with keys ``areaDescription`` and ``activityType``
        for each :class:`~comcheck_api.types.core_types.ActivityUse` in the
        building area.
    """
    whole_use = project.get_by_path("lighting.wholeBldgUse")
    if not isinstance(whole_use, list):
        return []

    area = next(
        (a for a in whole_use if getattr(a, "key", None) == building_area_key), None
    )
    if area is None:
        return []

    activity_uses = getattr(area, "activityUse", []) or []
    return [
        {
            "areaDescription": getattr(au, "areaDescription", None),
            "activityType": getattr(au, "activityType", None),
        }
        for au in activity_uses
    ]
