"""Project Building Area Operations."""

from typing import Any

from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.types.core_types import ComBuilding, WholeBldgUse

from comcheck_api.utilities.project_utilities import _require_building_area


def add_building_area_to_project(
    project: ComBuilding, new_building_area: WholeBldgUse
) -> ComBuilding:
    """Add a new building area to the project using buildingAreaListManager.

    Args:
        project: The project object to modify
        new_building_area: The building area object to add

    Returns:
        Updated project object with the building area added

    """

    updated_project = project.model_copy(deep=True)

    # Ensure interiorLightingSpace is initialized
    if new_building_area.interiorLightingSpace is None:
        new_building_area.interiorLightingSpace = (
            DEFAULT_BUILDING_AREA.interiorLightingSpace.model_copy(deep=True)
        )

    updated_project.lighting.append_subcomponent(new_building_area)

    return updated_project


def update_building_area_in_project(
    project: ComBuilding, building_area_key: str, updates: dict[str, Any] | WholeBldgUse
) -> ComBuilding:
    """Update an existing building area in the project using buildingAreaListManager.

    Args:
        project: The project object to modify
        building_area_key: The key of the building area to update
        updates: Partial updates (dict) or full building area object to apply

    Returns:
        Updated project object with the building area updated

    """
    _require_building_area(project, building_area_key)

    updated_project = project.model_copy(deep=True)

    updated_project.lighting.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=building_area_key, subcomponent_name="wholeBldgUse")

    return updated_project

def remove_building_area_from_project(
    project: ComBuilding, building_area_key: str) -> ComBuilding:
    """Remove an existing building area in the project.

    Args:
        project: The project object to modify
        building_area_key: The key of the building area to update

    Returns:
        Updated project object with the building area removed

    """
    _require_building_area(project, building_area_key)

    updated_project = project.model_copy(deep=True)

    updated_project.lighting.remove_from_subcomponent_list(subcomponent_id=building_area_key, subcomponent_name="wholeBldgUse")

    return updated_project

def get_building_area_keys_from_project(project: ComBuilding) -> list[dict]:
    """
    Extract valid building area identifiers from a COMcheck project.

    This function retrieves the `lighting.wholeBldgUse` field from the provided
    project and returns a list of dictionaries containing each area's unique key
    and description.

    Args:
        project (ComBuilding): The COMcheck project object.

    Returns:
        list[dict]: A list of dictionaries with the shape:
            {
                "key": <area key>,
                "areaDescription": <area description>
            }
    """
    whole_use = project.get_by_path("lighting.wholeBldgUse")

    if not isinstance(whole_use, list):
        return []

    return [
        {"key": getattr(area, "key"), "areaDescription": getattr(area, "areaDescription")}
        for area in whole_use
        if getattr(area, "key", None) is not None and getattr(area, "areaDescription", None) is not None
    ]