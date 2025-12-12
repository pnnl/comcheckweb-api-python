"""Project Envelope Operations."""

import copy
from typing import Any, Union, cast

from comcheck_api.components.envelope.ag_wall import AgWallListManager
from comcheck_api.components.envelope.bg_wall import BgWallListManager
from comcheck_api.components.envelope.door import DoorListManager
from comcheck_api.components.envelope.floor import FloorListManager
from comcheck_api.components.envelope.roof import RoofListManager
from comcheck_api.components.envelope.skylight import SkylightListManager
from comcheck_api.components.envelope.window import WindowListManager
from comcheck_api.types.core_types import (
    AgWall,
    BgWall,
    ComBuilding,
    Door,
    Floor,
    Roof,
    Skylight,
    ThermalBridgeCategoryOptions,
    ThermalBridgeComplianceTypeOptions,
    ThermalBridgeTypeOptions,
    Window,
    Envelope,
)
from comcheck_api.utilities.data_manager import T


# TODO: assemblyType needs to be set properly and uniquely.


def add_roof_to_project(
    project: ComBuilding, building_area_key: str, new_roof: Roof
) -> ComBuilding:
    """Add a new roof to the envelope in any project object using RoofListManager.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        new_roof: The roof object to add

    Returns:
        Updated project object with the roof added

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """
    # Deep clone to avoid mutating the original project
    _require_building_area(project, building_area_key)

    updated_project = project.model_copy(deep=True)

    new_roof.bldgUseKey = building_area_key
    updated_project.envelope.add_subcomponent(new_roof)

    return updated_project


def update_roof_in_project(
    project: ComBuilding, roof_assembly_type: str, updates: dict[str, Any] | Roof
) -> ComBuilding:
    """Update a roof in the project's envelope.

    Args:
        project: The project object to modify
        roof_assembly_type: The assemblyType of the roof to update in project.envelope.roof list
        updates: Partial updates (dict) or full Roof object to apply

    Returns:
        Updated project object with the roof added
    """
    updated_project = project.model_copy(deep=True)

    manager = RoofListManager(updated_project.envelope.roof)
    manager.modify_one(roof_assembly_type, updates)

    updated_project.envelope.roof = manager.get_all()

    return updated_project


def add_ag_wall_to_project(
    project: ComBuilding, building_area_key: str, new_ag_wall: AgWall
) -> ComBuilding:
    """Add a new agWall to the envelope in any project object using AgWallListManager.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        new_ag_wall: The agWall object to add

    Returns:
        Updated project object with the agWall added

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """

    _require_building_area(project, building_area_key)

    updated_project = project.model_copy(deep=True)

    new_ag_wall.bldgUseKey = building_area_key
    updated_project.envelope.add_subcomponent(new_ag_wall)

    return updated_project


def add_bg_wall_to_project(
    project: ComBuilding, building_area_key: str, new_bg_wall: BgWall
) -> ComBuilding:
    """Add a new bgWall to the envelope in any project object using BgWallListManager.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        new_bg_wall: The bgWall object to add

    Returns:
        Updated project object with the bgWall added

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """
    _require_building_area(project, building_area_key)

    updated_project = project.model_copy(deep=True)

    new_bg_wall.bldgUseKey = building_area_key
    updated_project.envelope.add_subcomponent(new_bg_wall)

    return updated_project


def add_floor_to_project(
    project: ComBuilding, building_area_key: str, new_floor: Floor
) -> ComBuilding:
    """Add a new floor to the envelope in any project object using FloorListManager.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        new_floor: The floor object to add

    Returns:
        Updated project object with the floor added

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """
    _require_building_area(project, building_area_key)

    updated_project = project.model_copy(deep=True)

    new_floor.bldgUseKey = building_area_key
    updated_project.envelope.add_subcomponent(new_floor)

    return updated_project


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


# *********** Assemblies or Components attached to wall or roof ***********


def add_skylight_to_project(
    project: ComBuilding,
    building_area_key: str,
    new_skylight: Skylight,
    roof: Roof | None = None,
) -> ComBuilding:
    """Add a new skylight to a specific roof in the envelope.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        new_skylight: The skylight object to add
        roof: The roof object to which the skylight will be added (required for non-alteration projects)

    Returns:
        Updated project object with the skylight added to the specified roof

    Raises:
        ValueError: If buildingAreaKey is not found or if roof's bldgUseKey doesn't match buildingAreaKey
    """
    updated_project = project.model_copy(deep=True)

    _require_building_area(project, building_area_key)

    # Set the building area key on the new skylight
    new_skylight.bldgUseKey = building_area_key

    if updated_project.projectType != "ALTERATION":
        if roof is None:
            raise ValueError("Roof must be specified for non-alteration projects.")

        if (roof_use_key := getattr(roof, "bldgUseKey", None)) != building_area_key:
            raise ValueError(
                f"Roof's bldgUseKey '{roof_use_key}' does not match buildingAreaKey '{building_area_key}'."
            )

        roofs = updated_project.get_by_path("envelope.roof")
        if isinstance(roofs, list):
            roof_index = next(
                (
                    i
                    for i, r in enumerate(roofs)
                    if getattr(r, "assemblyType") == getattr(roof, "assemblyType")
                ),
                -1,
            )
            if roof_index == -1:
                raise ValueError("Specified roof not found in project.")

            roof_manager = RoofListManager(roofs)
            updated_roof = roof_manager.add_new_skylight(
                roofs[roof_index], new_skylight
            )
            updated_project.envelope.roof[roof_index] = updated_roof
        else:
            raise ValueError("Envelope roof list not found or invalid in project.")
    else:
        # Alteration projects: orphaned skylights
        skylight_to_add = new_skylight.model_copy(
            update={"bldgUseKey": building_area_key}
        )

        envelope = getattr(updated_project, "envelope", None)
        if envelope is None:
            raise ValueError("Envelope not found in project.")

        skylight_manager = SkylightListManager(getattr(envelope, "skylight", []))
        updated_skylight_list = skylight_manager.add_new(skylight_to_add)
        updated_project.envelope.skylight = updated_skylight_list

    return updated_project


def add_window_to_project(
    project: ComBuilding,
    building_area_key: str,
    new_window: Window,
    wall: AgWall | BgWall | None = None,
) -> ComBuilding:
    """Add a new window to a wall (AgWall or BgWall) in the envelope.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        new_window: The window object to add
        wall: The AgWall or BgWall object to which the window will be added - required for non-alteration projects

    Returns:
        Updated project object with the window added to the specified wall

    Raises:
        ValueError: If buildingAreaKey is not found or if wall's bldgUseKey doesn't match buildingAreaKey
    """
    updated_project = project.model_copy(deep=True)

    _require_building_area(project, building_area_key)
    new_window.bldgUseKey = building_area_key

    if updated_project.projectType != "ALTERATION":
        if not wall:
            raise ValueError(
                "Wall (AgWall or BgWall) must be specified for non-alteration projects."
            )

        if (wall_use_key := getattr(wall, "bldgUseKey")) != building_area_key:
            raise ValueError(
                f"Wall's bldgUseKey '{wall_use_key}' does not match buildingAreaKey '{building_area_key}'."
            )

        ag_wall = updated_project.get_by_path("envelope.agWall")
        if isinstance(ag_wall, list):
            ag_wall_index = next(
                (
                    i
                    for i, w in enumerate(ag_wall)
                    if getattr(w, "assemblyType") == getattr(wall, "assemblyType")
                ),
                -1,
            )
            if ag_wall_index != -1:
                ag_wall_manager = AgWallListManager(updated_project.envelope.agWall)
                updated_ag_wall = ag_wall_manager.add_new_window(
                    updated_project.envelope.agWall[ag_wall_index], new_window
                )
                updated_project.envelope.agWall[ag_wall_index] = updated_ag_wall
                return updated_project

        # Try to find in bgWall array
        bg_wall = updated_project.get_by_path("envelope.bgWall")
        if isinstance(bg_wall, list):
            bg_wall_index = next(
                (
                    i
                    for i, w in enumerate(bg_wall)
                    if getattr(w, "assemblyType") == getattr(wall, "assemblyType")
                ),
                -1,
            )
            if bg_wall_index != -1:
                bg_wall_manager = BgWallListManager(updated_project.envelope.bgWall)
                updated_bg_wall = bg_wall_manager.add_new_window(
                    updated_project.envelope.bgWall[bg_wall_index], new_window
                )
                updated_project.envelope.bgWall[bg_wall_index] = updated_bg_wall
                return updated_project

        raise ValueError("Specified wall not found in project.")
    else:
        # Alteration projects: orphaned windows
        window_to_add: Window = new_window.model_copy(
            update={"bldgUseKey": building_area_key}
        )
        if not getattr(updated_project, "envelope"):
            raise ValueError("Envelope not found in project.")
        window_manager = WindowListManager(
            updated_project.get_by_path("envelope.window", [])
        )
        updated_project.envelope.window = window_manager.add_new(window_to_add)

    return updated_project


def add_door_to_project(
    project: ComBuilding,
    building_area_key: str,
    new_door: Door,
    wall: AgWall | BgWall | None = None,
) -> ComBuilding:
    """Add a new door to a wall (AgWall or BgWall) in the envelope.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        new_door: The door object to add
        wall: The AgWall or BgWall object to which the door will be added - required for non-alteration projects

    Returns:
        Updated project object with the door added to the specified wall

    Raises:
        ValueError: If buildingAreaKey is not found or if wall's bldgUseKey doesn't match buildingAreaKey
    """

    updated_project = project.model_copy(deep=True)

    _require_building_area(project, building_area_key)
    new_door.bldgUseKey = building_area_key

    if updated_project.projectType != "ALTERATION":

        if not wall:
            raise ValueError(
                "Wall (AgWall or BgWall) must be specified for non-alteration projects."
            )

        if (wall_use_key := getattr(wall, "bldgUseKey")) != building_area_key:
            raise ValueError(
                f"Wall's bldgUseKey '{wall_use_key}' does not match buildingAreaKey '{building_area_key}'."
            )

        # Try AgWall list
        ag_wall = updated_project.get_by_path("envelope.agWall")
        if isinstance(ag_wall, list):
            ag_wall_index = next(
                (
                    i
                    for i, w in enumerate(ag_wall)
                    if getattr(w, "assemblyType") == getattr(wall, "assemblyType")
                ),
                -1,
            )
            if ag_wall_index != -1:
                ag_wall_manager = AgWallListManager(updated_project.envelope.agWall)
                updated_ag_wall = ag_wall_manager.add_new_door(
                    updated_project.envelope.agWall[ag_wall_index], new_door
                )
                updated_project.envelope.agWall[ag_wall_index] = updated_ag_wall
                return updated_project

        # Try BgWall list
        bg_wall = updated_project.get_by_path("envelope.bgWall")
        if isinstance(bg_wall, list):
            bg_wall_index = next(
                (
                    i
                    for i, w in enumerate(bg_wall)
                    if getattr(w, "assemblyType") == getattr(wall, "assemblyType")
                ),
                -1,
            )
            if bg_wall_index != -1:
                bg_wall_manager = BgWallListManager(updated_project.envelope.bgWall)
                updated_bg_wall = bg_wall_manager.add_new_door(
                    updated_project.envelope.bgWall[bg_wall_index], new_door
                )
                updated_project.envelope.bgWall[bg_wall_index] = updated_bg_wall
                return updated_project

        raise ValueError("Specified wall not found in project.")

    else:
        door_to_add = new_door.model_copy(update={"bldgUseKey": building_area_key})

        if not getattr(updated_project, "envelope"):
            raise ValueError("Envelope not found in project.")

        door_manager = DoorListManager(updated_project.get_by_path("envelope.door", []))
        updated_project.envelope.door = door_manager.add_new(door_to_add)

        return updated_project


# TODO: verify when thermal bridges are needed
def add_thermal_bridge_to_project(
    project: ComBuilding,
    building_area_key: str,
    ag_wall: AgWall,
    thermal_bridge_type: Union[
        ThermalBridgeTypeOptions, str
    ] = ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER,
    thermal_bridge_category: Union[
        ThermalBridgeCategoryOptions, str
    ] = ThermalBridgeCategoryOptions.THERMAL_BRIDGE_UNCATEGORIZED,
    thermal_bridge_compliance_type: Union[
        ThermalBridgeComplianceTypeOptions, str
    ] = ThermalBridgeComplianceTypeOptions.THERMAL_BRIDGE_NON_PRESCRIPTIVE,
    psi_factor: float = 0.0,
    chi_factor: float = 0.0,
    thermal_bridge_length: float = 0.0,
) -> ComBuilding:
    """Add a new thermal bridge to an AgWall in the envelope.

    Note: Thermal bridges can only be added to AgWalls and cannot be orphaned.

    Args:
        project: The project object to modify
        building_area_key: The building area key to validate against lighting.wholeBldgUse list
        ag_wall: The AgWall object to which the thermal bridge will be added (required)
        thermal_bridge_type: Type of thermal bridge (defaults to 'THERMAL_BRIDGE_OTHER')
        thermal_bridge_category: Category of thermal bridge (defaults to 'THERMAL_BRIDGE_UNCATEGORIZED')
        thermal_bridge_compliance_type: Compliance type (defaults to 'THERMAL_BRIDGE_NON_PRESCRIPTIVE')
        psi_factor: Psi factor (defaults to 0.0)
        chi_factor: Chi factor (defaults to 0.0)
        thermal_bridge_length: Length of thermal bridge (defaults to 0.0)

    Returns:
        Updated project object with the thermal bridge added to the specified AgWall

    Raises:
        ValueError: If buildingAreaKey is not found, agWall is not provided, or wall's bldgUseKey doesn't match buildingAreaKey
    """
    updated_project = project.model_copy(deep=True)

    _require_building_area(
        project, building_area_key
    )  # assuming this works with models

    if ag_wall is None:
        raise ValueError("AgWall must be specified for thermal bridges.")

    if getattr(ag_wall, "bldgUseKey", None) != building_area_key:
        raise ValueError(
            f"AgWall's bldgUseKey '{getattr(ag_wall, 'bldgUseKey')}' does not match buildingAreaKey '{building_area_key}'."
        )

    envelope = getattr(updated_project, "envelope", None)
    if envelope is None:
        raise ValueError("Envelope not found in project.")

    ag_wall_list = getattr(envelope, "agWall", None)
    if not isinstance(ag_wall_list, list):
        raise ValueError("agWall list not found or invalid.")

    # Find index of matching agWall by assemblyType (attribute access)
    ag_wall_index = next(
        (
            i
            for i, w in enumerate(ag_wall_list)
            if getattr(w, "assemblyType", None)
            == getattr(ag_wall, "assemblyType", None)
        ),
        -1,
    )

    if ag_wall_index == -1:
        raise ValueError("Specified agWall not found in project.")

    # Use your manager on Pydantic list
    manager = AgWallListManager(ag_wall_list)
    updated_wall = manager.add_new_thermal_bridge(
        ag_wall_list[ag_wall_index],
        thermal_bridge_type,
        thermal_bridge_category,
        thermal_bridge_compliance_type,
        psi_factor,
        chi_factor,
        thermal_bridge_length,
    )

    # Replace the agWall in the list
    ag_wall_list[ag_wall_index] = updated_wall

    # If envelope.agWall is a Pydantic field with validation, reassign updated list
    envelope.agWall = ag_wall_list

    # If updated_project.envelope is frozen or uses validators, reassign as needed
    updated_project.envelope = envelope

    return updated_project
