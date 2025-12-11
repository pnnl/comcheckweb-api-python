"""Project Building Area Operations."""

from typing import Any

from comcheck_api.components.building_area import BuildingAreaListManager
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.types.core_types import ComBuilding, WholeBldgUse


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

    updated_project.lighting.add_subcomponent(new_building_area)

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
    updated_project = project.model_copy(deep=True)

    manager = BuildingAreaListManager(updated_project.lighting.wholeBldgUse)
    manager.modify_one(building_area_key, updates)

    # Reassign the modified list back to the project
    updated_project.lighting.wholeBldgUse = manager.get_all()

    return updated_project
