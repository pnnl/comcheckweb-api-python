"""Project Exterior Lighting Operations.

Manages exterior lighting at the ExteriorUse granularity.  Each ExteriorUse
carries exactly one (singleton) ExteriorLightingSpace whose fixture[] holds
the fixtures.  There are no fixture-level operations — to add, change, or
remove a fixture, edit the ExteriorUse's exteriorLightingSpace.fixture[] list
and pass the whole ExteriorUse through update_exterior_lighting_area_in_project.

Zone type
---------
exterior compliance requires a real zone type on lighting.exteriorLightingZoneType
(anything other than EXT_ZONE_UNSPECIFIED).  Use
set_exterior_lighting_zone_type_in_project to set it.  Adding an ExteriorUse
while the zone is still EXT_ZONE_UNSPECIFIED emits a warning — it is not a
hard error so the project can be built up incrementally.
"""

import logging
import warnings
from typing import Any

from comcheck_api.types.core_types import (
    ComBuilding,
    ExteriorLightingSpace,
    ExteriorLightingZoneTypeOptions,
    ExteriorUse,
)
from comcheck_api.utilities.project_utilities import _require_exterior_use

logger = logging.getLogger(__name__)


def set_exterior_lighting_zone_type_in_project(
    project: ComBuilding,
    zone_type: ExteriorLightingZoneTypeOptions,
) -> ComBuilding:
    """Set the project-level exterior lighting zone type.

    Args:
        project: The project to modify.
        zone_type: An :class:`~comcheck_api.types.core_types.ExteriorLightingZoneTypeOptions`
            value.  Must not be ``EXT_ZONE_UNSPECIFIED`` — exterior compliance
            cannot be evaluated without a real zone type.

    Returns:
        Updated project with the zone type set.

    Raises:
        TypeError: If zone_type is not an ExteriorLightingZoneTypeOptions member.
        ValueError: If zone_type is EXT_ZONE_UNSPECIFIED.
    """
    if not isinstance(zone_type, ExteriorLightingZoneTypeOptions):
        raise TypeError(
            f"zone_type must be an ExteriorLightingZoneTypeOptions member, "
            f"got {type(zone_type).__name__!r}."
        )
    if zone_type == ExteriorLightingZoneTypeOptions.EXT_ZONE_UNSPECIFIED:
        raise ValueError(
            "EXT_ZONE_UNSPECIFIED is not a valid zone type — exterior compliance "
            "cannot be evaluated without a real zone type. "
            "Choose a value from ExteriorLightingZoneTypeOptions other than "
            "EXT_ZONE_UNSPECIFIED."
        )

    updated_project = project.model_copy(deep=True)
    updated_project.lighting.exteriorLightingZoneType = zone_type
    return updated_project


def add_exterior_lighting_area_to_project(
    project: ComBuilding,
    new_exterior_lighting_area: ExteriorUse,
) -> ComBuilding:
    """Add a new ExteriorUse (exterior lighting space) to the project.

    Fixtures and the singleton ExteriorLightingSpace are carried inside
    new_exterior_lighting_area — populate exteriorLightingSpace.fixture[] before
    passing if you want fixtures on creation.

    Emits a :class:`UserWarning` if the project's
    ``lighting.exteriorLightingZoneType`` is still ``EXT_ZONE_UNSPECIFIED``,
    because exterior compliance cannot be evaluated until a real zone type is
    set.  Call :func:`set_exterior_lighting_zone_type_in_project` to fix it.

    Args:
        project: The project to modify.
        new_exterior_lighting_area: The ExteriorUse to add.

    Returns:
        Updated project with the new ExteriorUse added.
    """
    zone = project.lighting.exteriorLightingZoneType
    if zone == ExteriorLightingZoneTypeOptions.EXT_ZONE_UNSPECIFIED:
        warnings.warn(
            "The project's exterior lighting zone type is EXT_ZONE_UNSPECIFIED. "
            "Exterior compliance cannot be evaluated until a real zone type is set. "
            "Call set_exterior_lighting_zone_type_in_project() to fix this.",
            UserWarning,
            stacklevel=2,
        )

    updated_project = project.model_copy(deep=True)

    new_exterior_lighting_area = new_exterior_lighting_area.model_copy(deep=True)

    # Ensure exteriorLightingSpace is initialised
    if new_exterior_lighting_area.exteriorLightingSpace is None:
        new_exterior_lighting_area = new_exterior_lighting_area.model_copy(
            deep=True,
            update={
                "exteriorLightingSpace": ExteriorLightingSpace(
                    description="",
                    numFixturesAlteredOrAdded=0,
                    postAltTotalWattage=0.0,
                    preAltNumberFixtures=0,
                    preAltTotalWattage=0.0,
                    altExemptType=None,
                    fixture=[],
                )
            },
        )

    updated_project.lighting.append_subcomponent(new_exterior_lighting_area)
    return updated_project


def update_exterior_lighting_area_in_project(
    project: ComBuilding,
    area_description: str,
    updates: dict[str, Any] | ExteriorUse,
) -> ComBuilding:
    """Update an existing ExteriorUse.

    To add, change, or remove fixtures: set the desired
    exteriorLightingSpace.fixture[] on the updates dict (or the full
    ExteriorUse object) before calling this function.

    Args:
        project: The project to modify.
        area_description: The areaDescription of the ExteriorUse to update.
        updates: Partial updates (dict) or full ExteriorUse to apply.

    Returns:
        Updated project with the ExteriorUse modified.
    """
    _require_exterior_use(project, area_description)

    updated_project = project.model_copy(deep=True)
    updated_project.lighting.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=area_description,
        subcomponent_name="exteriorUse",
    )
    return updated_project


def remove_exterior_lighting_area_from_project(
    project: ComBuilding,
    area_description: str,
) -> ComBuilding:
    """Remove an ExteriorUse (and its lighting space + fixtures) from the project.

    Args:
        project: The project to modify.
        area_description: The areaDescription of the ExteriorUse to remove.

    Returns:
        Updated project with the ExteriorUse removed.
    """
    _require_exterior_use(project, area_description)

    updated_project = project.model_copy(deep=True)
    updated_project.lighting.remove_from_subcomponent_list(
        subcomponent_id=area_description,
        subcomponent_name="exteriorUse",
    )
    return updated_project


def get_exterior_lighting_area_keys_from_project(project: ComBuilding) -> list[dict]:
    """Return the areaDescription and exteriorType of all ExteriorUse items.

    Args:
        project: The project to query.

    Returns:
        List of dicts with keys ``areaDescription`` and ``exteriorType``
        for each ExteriorUse in the project.
    """
    exterior_uses = project.get_by_path("lighting.exteriorUse")
    if not isinstance(exterior_uses, list):
        return []
    return [
        {
            "areaDescription": getattr(eu, "areaDescription", None),
            "exteriorType": getattr(eu, "exteriorType", None),
        }
        for eu in exterior_uses
    ]
