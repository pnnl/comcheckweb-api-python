"""Project Envelope Operations."""

from typing import Any, Union

from comcheck_api.components.envelope.ag_wall import AgWallListManager
from comcheck_api.types.core_types import (
    AgWall,
    BgWall,
    ComBuilding,
    Door,
    Floor,
    ProjectTypeOptions,
    Roof,
    Skylight,
    ThermalBridgeCategoryOptions,
    ThermalBridgeComplianceTypeOptions,
    ThermalBridgeTypeOptions,
    Window,
)
from comcheck_api.utilities.project_utilities import _require_building_area

# *********** Roof, agWall, bgWall and floor add/update operations ***********

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
    updated_project.envelope.append_subcomponent(new_roof)

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

    updated_project.envelope.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=roof_assembly_type, subcomponent_name="roof")

    return updated_project

def remove_roof_from_project(
    project: ComBuilding, roof_assembly_type: str
) -> ComBuilding:
    """Remove a roof from the envelope in any project object.

    Args:
        project: The project object to modify
        roof_assembly_type: The assemblyType of the roof to update in project.envelope.roof list

    Returns:
        Project object with the roof removed

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """
    updated_project = project.model_copy(deep=True)

    updated_project.envelope.remove_from_subcomponent_list(subcomponent_id=roof_assembly_type, subcomponent_name="roof")

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
    updated_project.envelope.append_subcomponent(new_ag_wall)

    return updated_project


def update_ag_wall_in_project(
    project: ComBuilding, ag_wall_assembly_type: str, updates: dict[str, Any] | AgWall
) -> ComBuilding:
    """Update an agWall in the project's envelope.

    Args:
        project: The project object to modify
        ag_wall_assembly_type: The assemblyType of the agWall to update in project.envelope.agWall list
        updates: Partial updates (dict) or full AgWall object to apply

    Returns:
        Updated project object with the agWall updated
    """
    updated_project = project.model_copy(deep=True)

    updated_project.envelope.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=ag_wall_assembly_type, subcomponent_name="agWall")

    return updated_project

def remove_ag_wall_from_project(
    project: ComBuilding, ag_wall_assembly_type: str
) -> ComBuilding:
    """Remove an agWall from the envelope in any project object.

    Args:
        project: The project object to modify
        ag_wall_assembly_type: The assemblyType of the agWall to update in project.envelope.agWall list

    Returns:
        Project object with the agWall removed

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """
    updated_project = project.model_copy(deep=True)

    updated_project.envelope.remove_from_subcomponent_list(subcomponent_id=ag_wall_assembly_type, subcomponent_name="agWall")

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
    updated_project.envelope.append_subcomponent(new_bg_wall)

    return updated_project


def update_bg_wall_in_project(
    project: ComBuilding, bg_wall_assembly_type: str, updates: dict[str, Any] | BgWall
) -> ComBuilding:
    """Update an bgWall in the project's envelope.

    Args:
        project: The project object to modify
        bg_wall_assembly_type: The assemblyType of the bgWall to update in project.envelope.bgWall list
        updates: Partial updates (dict) or full BgWall object to apply

    Returns:
        Updated project object with the bgWall updated
    """
    updated_project = project.model_copy(deep=True)

    updated_project.envelope.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=bg_wall_assembly_type, subcomponent_name="bgWall")

    return updated_project


def remove_bg_wall_from_project(
    project: ComBuilding, bg_wall_assembly_type: str
) -> ComBuilding:
    """Remove an bgWall from the envelope in any project object.

    Args:
        project: The project object to modify
        bg_wall_assembly_type: The assemblyType of the bgWall to update in project.envelope.bgWall list

    Returns:
        Project object with the bgWall removed

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """
    updated_project = project.model_copy(deep=True)

    updated_project.envelope.remove_from_subcomponent_list(subcomponent_id=bg_wall_assembly_type, subcomponent_name="bgWall")

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
    updated_project.envelope.append_subcomponent(new_floor)

    return updated_project


def update_floor_in_project(
    project: ComBuilding, floor_assembly_type: str, updates: dict[str, Any] | Floor
) -> ComBuilding:
    """Update an floor in the project's envelope.

    Args:
        project: The project object to modify
        floor_assembly_type: The assemblyType of the floor to update in project.envelope.floor list
        updates: Partial updates (dict) or full Floor object to apply

    Returns:
        Updated project object with the floor updated
    """
    updated_project = project.model_copy(deep=True)

    updated_project.envelope.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=floor_assembly_type, subcomponent_name="floor")

    return updated_project

def remove_floor_from_project(
    project: ComBuilding, floor_assembly_type: str
) -> ComBuilding:
    """Remove an bgWall from the envelope in any project object.

    Args:
        project: The project object to modify
        floor_assembly_type: The assemblyType of the floor to remove in project.envelope.floor list

    Returns:
        Project object with the floor removed

    Raises:
        ValueError: If buildingAreaKey is not found in lighting.wholeBldgUse list
    """
    updated_project = project.model_copy(deep=True)

    updated_project.envelope.remove_from_subcomponent_list(subcomponent_id=floor_assembly_type, subcomponent_name="floor")

    return updated_project


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
    updated_project.require_attribute("envelope")

    skylight_to_add = new_skylight.model_copy(update={"bldgUseKey": building_area_key})

    if updated_project.projectType != ProjectTypeOptions.ALTERATION:
        # Add to existing roof for non-alteration projects
        if roof is None:
            raise ValueError("Roof must be specified for non-alteration projects.")

        if (roof_use_key := getattr(roof, "bldgUseKey")) != building_area_key:
            raise ValueError(
                f"Roof's bldgUseKey '{roof_use_key}' does not match buildingAreaKey '{building_area_key}'."
            )

        roof.append_subcomponent(skylight_to_add, "skylight")
        updated_project.envelope.update_subcomponent_list(
            subcomponent_updates=roof,
            subcomponent_id=getattr(roof, "assemblyType"),
            subcomponent_name=roof.json_key(),
        )

        return updated_project
    else:
        # Alteration projects: add orphaned skylight directly
        updated_project.envelope.append_subcomponent(skylight_to_add, "skylight")
        return updated_project

def remove_skylight_from_project(
    project: ComBuilding,
    skylight_assembly_type: str,
) -> ComBuilding:
    """Add a new skylight to a specific roof in the envelope.

    Args:
        project: ComBuilding,
        skylight_assembly_type: str

    Returns:
        Updated project object with the skylight added to the specified roof

    Raises:
        ValueError: If buildingAreaKey is not found or if roof's bldgUseKey doesn't match buildingAreaKey
    """
    updated_project = project.model_copy(deep=True)

    # Find where the skylight is located
    location_type, roof_index, _ = _find_component_location(
        project, "skylight", skylight_assembly_type
    )

    # Update skylight based on its location
    if location_type == "orphaned":
        parent_obj = updated_project.envelope
    elif location_type == "roof":
        parent_obj = updated_project.envelope.roof[roof_index]
    parent_obj.remove_from_subcomponent_list(subcomponent_id=skylight_assembly_type, subcomponent_name="skylight")

    return updated_project

def update_skylight_in_project(
    project: ComBuilding,
    skylight_assembly_type: str,
    updates: dict[str, Any] | Skylight,
) -> ComBuilding:
    """Update a skylight in the project's envelope.

    Skylights can exist in two locations:
    1. Orphaned skylights in envelope.skylight (ALTERATION projects)
    2. Skylights nested in roof list

    Args:
        project: The project object to modify
        skylight_assembly_type: The assemblyType of the skylight to update
        updates: Partial updates (dict) or full Skylight object to apply

    Returns:
        Updated project object with the skylight updated

    Raises:
        ValueError: If the skylight is not found in any location
    """
    updated_project = project.model_copy(deep=True)

    # Find where the skylight is located
    location_type, roof_index, _ = _find_component_location(
        project, "skylight", skylight_assembly_type
    )

    # Update skylight based on its location
    if location_type == "orphaned":
        parent_obj = updated_project.envelope
    elif location_type == "roof":
        parent_obj = updated_project.envelope.roof[roof_index]
    parent_obj.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=skylight_assembly_type, subcomponent_name="skylight")

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
    updated_project.require_attribute("envelope")

    window_to_add = new_window.model_copy(update={"bldgUseKey": building_area_key})

    if updated_project.projectType != ProjectTypeOptions.ALTERATION:
        if wall is None:
            raise ValueError(
                "Wall (AgWall or BgWall) must be specified for non-alteration projects."
            )

        if (wall_use_key := getattr(wall, "bldgUseKey")) != building_area_key:
            raise ValueError(
                f"Wall's bldgUseKey '{wall_use_key}' does not match buildingAreaKey '{building_area_key}'."
            )

        wall.append_subcomponent(window_to_add, "window")
        updated_project.envelope.update_subcomponent_list(
            subcomponent_updates=wall,
            subcomponent_id=getattr(wall, "assemblyType"),
            subcomponent_name=wall.json_key(),
        )
        return updated_project
    else:
        # Alteration projects: orphaned windows
        updated_project.envelope.append_subcomponent(window_to_add, "window")
        return updated_project
    
def remove_window_from_project(
    project: ComBuilding,
    window_assembly_type: str,
) -> ComBuilding:
    """Remove a window from the project.

    Args:
        project: ComBuilding,
        window_assembly_type: str

    Returns:
        Updated project object with the window removed
    """
    updated_project = project.model_copy(deep=True)

    # Find where the window is located
    location_type, wall_index, _ = _find_component_location(
        project, "window", window_assembly_type
    )

    # Update window based on its location
    if location_type == "orphaned":
        parent_obj = updated_project.envelope
    elif location_type in ["agWall", "bgWall"]:
        parent_obj = updated_project.envelope.get_by_path(f"{location_type}[{wall_index}]")
    parent_obj.remove_from_subcomponent_list(subcomponent_id=window_assembly_type, subcomponent_name="window")

    return updated_project


def update_window_in_project(
    project: ComBuilding, window_assembly_type: str, updates: dict[str, Any] | Window
) -> ComBuilding:
    """Update a window in the project's envelope.

    Windows can exist in three locations:
    1. Orphaned windows in envelope.window (ALTERATION projects)
    2. Windows nested in agWall list
    3. Windows nested in bgWall list

    Args:
        project: The project object to modify
        window_assembly_type: The assemblyType of the window to update
        updates: Partial updates (dict) or full Window object to apply

    Returns:
        Updated project object with the window updated

    Raises:
        ValueError: If the window is not found in any location
    """
    updated_project = project.model_copy(deep=True)

    # Find where the window is located
    location_type, wall_index, _ = _find_component_location(
        project, "window", window_assembly_type
    )

    # Update window based on its location
    if location_type == "orphaned":
        parent_obj = updated_project.envelope
    elif location_type in ["agWall", "bgWall"]:
        parent_obj = updated_project.envelope.get_by_path(f"{location_type}[{wall_index}]")
    parent_obj.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=window_assembly_type, subcomponent_name="window")

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
    updated_project.require_attribute("envelope")

    door_to_add = new_door.model_copy(update={"bldgUseKey": building_area_key})

    if updated_project.projectType != ProjectTypeOptions.ALTERATION:
        # Add to existing wall for non-alteration projects
        if not wall:
            raise ValueError(
                "Wall (AgWall or BgWall) must be specified for non-alteration projects."
            )

        if (wall_use_key := getattr(wall, "bldgUseKey")) != building_area_key:
            raise ValueError(
                f"Wall's bldgUseKey '{wall_use_key}' does not match buildingAreaKey '{building_area_key}'."
            )
        wall.append_subcomponent(door_to_add, "door")
        updated_project.envelope.update_subcomponent_list(subcomponent_updates=wall, subcomponent_id=getattr(wall, "assemblyType"), subcomponent_name=wall.json_key())
        return updated_project
    else:
        updated_project.envelope.append_subcomponent(door_to_add)

        return updated_project


def remove_door_from_project(
    project: ComBuilding,
    door_assembly_type: str,
) -> ComBuilding:
    """Remove a door from the project.

    Args:
        project: ComBuilding,
        door_assembly_type: str

    Returns:
        Updated project object with the door removed
    """
    updated_project = project.model_copy(deep=True)

    # Find where the door is located
    location_type, wall_index, _ = _find_component_location(
        project, "door", door_assembly_type
    )

    # Remove door based on its location
    if location_type == "orphaned":
        parent_obj = updated_project.envelope
    elif location_type in ["agWall", "bgWall"]:
        parent_obj = updated_project.envelope.get_by_path(f"{location_type}[{wall_index}]")
    parent_obj.remove_from_subcomponent_list(subcomponent_id=door_assembly_type, subcomponent_name="door")

    return updated_project

def update_door_in_project(
    project: ComBuilding, door_assembly_type: str, updates: dict[str, Any] | Door
) -> ComBuilding:
    """Update a door in the project's envelope.

    Doors can exist in three locations:
    1. Orphaned doors in envelope.door (ALTERATION projects)
    2. Doors nested in agWall list
    3. Doors nested in bgWall list

    Args:
        project: The project object to modify
        door_assembly_type: The assemblyType of the door to update
        updates: Partial updates (dict) or full Door object to apply

    Returns:
        Updated project object with the door updated

    Raises:
        ValueError: If the door is not found in any location
    """
    updated_project = project.model_copy(deep=True)

    # Find where the door is located
    location_type, wall_index, _ = _find_component_location(
        project, "door", door_assembly_type
    )

    # Update door based on its location
    if location_type == "orphaned":
        parent_obj = updated_project.envelope
    elif location_type in ["agWall", "bgWall"]:
        parent_obj = updated_project.envelope.get_by_path(f"{location_type}[{wall_index}]")
    parent_obj.update_subcomponent_list(subcomponent_updates=updates, subcomponent_id=door_assembly_type, subcomponent_name="door")

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
    number_of_points: int = 0,
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
        number_of_points: Number of points for thermal bridge (defaults to 0)

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
        number_of_points,
    )

    # Replace the agWall in the list
    ag_wall_list[ag_wall_index] = updated_wall

    # If envelope.agWall is a Pydantic field with validation, reassign updated list
    envelope.agWall = ag_wall_list

    # If updated_project.envelope is frozen or uses validators, reassign as needed
    updated_project.envelope = envelope

    return updated_project


# *********** Helper Functions ***********

def _find_component_location(
    project: ComBuilding, component_type: str, assembly_type: str
) -> tuple[str, int | None, int | None]:
    """Find the location of a window, door, or skylight component.

    Components can exist in different locations:
    - Windows/Doors: orphaned (envelope.window/door) or nested in agWall/bgWall
    - Skylights: orphaned (envelope.skylight) or nested in roof

    Args:
        project: The project to search in
        component_type: Either "window", "door", or "skylight"
        assembly_type: The assemblyType to search for

    Returns:
        Tuple of (location_type, parent_index, component_index) where:
        - location_type is "orphaned", "agWall", "bgWall", or "roof"
        - parent_index is the index in agWall/bgWall/roof list (None for orphaned)
        - component_index is the index in the component list

    Raises:
        ValueError: If component is not found anywhere
    """
    # Check orphaned components first
    orphaned_list = getattr(project.envelope, component_type, [])
    if orphaned_list:
        component_index = next(
            (
                i
                for i, c in enumerate(orphaned_list)
                if getattr(c, "assemblyType", None) == assembly_type
            ),
            -1,
        )
        if component_index != -1:
            return ("orphaned", None, component_index)

    # For windows/doors: check agWall and bgWall components
    if component_type in ("window", "door"):
        # Check agWall components
        for ag_wall_index, ag_wall in enumerate(project.envelope.agWall):
            wall_components = getattr(ag_wall, component_type, [])
            if wall_components:
                component_index = next(
                    (
                        i
                        for i, c in enumerate(wall_components)
                        if getattr(c, "assemblyType", None) == assembly_type
                    ),
                    -1,
                )
                if component_index != -1:
                    return ("agWall", ag_wall_index, component_index)

        # Check bgWall components
        for bg_wall_index, bg_wall in enumerate(project.envelope.bgWall):
            wall_components = getattr(bg_wall, component_type, [])
            if wall_components:
                component_index = next(
                    (
                        i
                        for i, c in enumerate(wall_components)
                        if getattr(c, "assemblyType", None) == assembly_type
                    ),
                    -1,
                )
                if component_index != -1:
                    return ("bgWall", bg_wall_index, component_index)

    # For skylights: check roof components
    elif component_type == "skylight":
        for roof_index, roof in enumerate(project.envelope.roof or []):
            roof_skylights = getattr(roof, "skylight", [])
            if roof_skylights:
                skylight_index = next(
                    (
                        i
                        for i, s in enumerate(roof_skylights)
                        if getattr(s, "assemblyType", None) == assembly_type
                    ),
                    -1,
                )
                if skylight_index != -1:
                    return ("roof", roof_index, skylight_index)

    raise ValueError(
        f"{component_type.capitalize()} with assemblyType '{assembly_type}' not found in project"
    )


# *********** End of Project Envelope Operations ***********
