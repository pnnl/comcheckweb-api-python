"""Internal helpers for validating and querying COMcheck project structures."""

from typing import List
from comcheck_api.types.custom_base_model import CustomBaseModel
from comcheck_api.types.core_types import ComBuilding
from comcheck_api.managers.data_manager import DataManager, get_model_info


def _require_unique_area_description(
    project: ComBuilding,
    area_description: str,
    exclude_key: str | float | None = None,
) -> None:
    """Raise if area_description already exists in wholeBldgUse (case-sensitive).

    Args:
        project: The project to check.
        area_description: The description to validate for uniqueness.
        exclude_key: Skip the WholeBldgUse item with this key (used during updates
            so the item being edited doesn't conflict with itself).

    Raises:
        ValueError: If another WholeBldgUse item has the same areaDescription.
    """
    whole_use = project.get_by_path("lighting.wholeBldgUse")
    if not isinstance(whole_use, list):
        return

    for area in whole_use:
        if exclude_key is not None and getattr(area, "key", None) == exclude_key:
            continue
        if getattr(area, "areaDescription", None) == area_description:
            raise ValueError(
                f"areaDescription '{area_description}' already exists in wholeBldgUse."
            )


def _require_building_area(project: ComBuilding, building_area_key: str) -> None:
    """
    Ensure that project.lighting.wholeBldgUse exists and contains the given key.
    """
    whole_use = project.get_by_path("lighting.wholeBldgUse")

    if not isinstance(whole_use, list):
        raise ValueError("No building area (wholeBldgUse) found in project.")

    if not any(getattr(area, "key", None) == building_area_key for area in whole_use):
        raise ValueError(
            f"Building area key '{building_area_key}' not found in lighting.wholeBldgUse."
        )


def _require_activity_use(
    project: ComBuilding, building_area_key: str, area_description: str
) -> None:
    """Ensure the given building area contains an interior space (activityUse) with the given areaDescription."""
    whole_use = project.get_by_path("lighting.wholeBldgUse")
    if not isinstance(whole_use, list):
        raise ValueError("No building areas (wholeBldgUse) found in project.")

    area = next(
        (area for area in whole_use if getattr(area, "key", None) == building_area_key),
        None,
    )
    if area is None:
        raise ValueError(
            f"Building area key '{building_area_key}' not found in lighting.wholeBldgUse."
        )

    interior_spaces = getattr(area, "activityUse", []) or []
    if not any(
        getattr(interior_space, "areaDescription", None) == area_description
        for interior_space in interior_spaces
    ):
        raise ValueError(
            f"InteriorSpace with areaDescription '{area_description}' "
            f"not found in building area '{building_area_key}'."
        )


def _require_exterior_use(project: ComBuilding, area_description: str) -> None:
    """Ensure project.lighting.exteriorUse contains an exterior area (ExteriorUse) with the given areaDescription."""
    exterior_areas = project.get_by_path("lighting.exteriorUse")
    if not isinstance(exterior_areas, list):
        raise ValueError("No exterior uses (lighting.exteriorUse) found in project.")

    if not any(
        getattr(exterior_area, "areaDescription", None) == area_description
        for exterior_area in exterior_areas
    ):
        raise ValueError(
            f"ExteriorArea with areaDescription '{area_description}' "
            f"not found in lighting.exteriorUse."
        )


def find_component_in_component_list(
    components: List[CustomBaseModel], component_id: str
):
    """Find a component by its identifier within a list of components.

    Args:
        components: List of model instances to search through.
        component_id: The identifier value to look up.

    Returns:
        The matching component, or None if not found or the list is empty.
    """
    if not components:
        return None

    component_type = type(components[0])
    component_manager: DataManager = DataManager(
        initial_data=components, model_type=component_type
    )

    return component_manager.get_by_identifier(component_id)


def get_id_from_component(
    component: CustomBaseModel,
) -> str | None:
    """Retrieve the unique identifier value of a component.

    Args:
        component: A model instance whose identifier should be extracted.

    Returns:
        The identifier string, or ``None`` if the identifier attribute is unset.
    """

    identifier, _ = get_model_info(type(component))
    return getattr(component, identifier, None)
