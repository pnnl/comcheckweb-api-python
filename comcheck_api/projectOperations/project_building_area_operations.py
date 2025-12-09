"""Project Building Area Operations."""

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
