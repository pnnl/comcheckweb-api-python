"""Project Envelope Operations."""

import copy
from typing import Any, cast

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
    Door,
    Floor,
    Roof,
    Skylight,
    ThermalBridgeCategoryOptions,
    ThermalBridgeComplianceTypeOptions,
    ThermalBridgeTypeOptions,
    Window,
)


# TODO: assemblyType needs to be set properly and uniquely.


def add_roof_to_project(
    project: dict[str, Any], building_area_key: str, new_roof: Roof
) -> dict[str, Any]:
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
    updated_project = copy.deepcopy(project)

    # Check if buildingAreaKey exists in lighting.wholeBldgUse list
    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding roof error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if (
        "envelope" in updated_project
        and "roof" in updated_project["envelope"]
        and isinstance(updated_project["envelope"]["roof"], list)
    ):
        roof_to_add: Roof = cast(Roof, {**new_roof, "bldgUseKey": building_area_key})
        manager = RoofListManager(updated_project["envelope"]["roof"])
        updated_project["envelope"]["roof"] = manager.add_new(roof_to_add)
    else:
        raise ValueError("Envelope or roof array not found in project.")

    return updated_project


def add_ag_wall_to_project(
    project: dict[str, Any], building_area_key: str, new_ag_wall: AgWall
) -> dict[str, Any]:
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
    updated_project = copy.deepcopy(project)

    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding agWall error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if (
        "envelope" in updated_project
        and "agWall" in updated_project["envelope"]
        and isinstance(updated_project["envelope"]["agWall"], list)
    ):
        ag_wall_to_add: AgWall = cast(
            AgWall, {**new_ag_wall, "bldgUseKey": building_area_key}
        )
        manager = AgWallListManager(updated_project["envelope"]["agWall"])
        updated_project["envelope"]["agWall"] = manager.add_new(ag_wall_to_add)
    else:
        raise ValueError("Envelope or agWall array not found in project.")

    return updated_project


def add_bg_wall_to_project(
    project: dict[str, Any], building_area_key: str, new_bg_wall: BgWall
) -> dict[str, Any]:
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
    updated_project = copy.deepcopy(project)

    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding bgWall error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if (
        "envelope" in updated_project
        and "bgWall" in updated_project["envelope"]
        and isinstance(updated_project["envelope"]["bgWall"], list)
    ):
        bg_wall_to_add: BgWall = cast(
            BgWall, {**new_bg_wall, "bldgUseKey": building_area_key}
        )
        manager = BgWallListManager(updated_project["envelope"]["bgWall"])
        updated_project["envelope"]["bgWall"] = manager.add_new(bg_wall_to_add)
    else:
        raise ValueError("Envelope or bgWall array not found in project.")

    return updated_project


def add_floor_to_project(
    project: dict[str, Any], building_area_key: str, new_floor: Floor
) -> dict[str, Any]:
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
    updated_project = copy.deepcopy(project)

    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding floor error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if (
        "envelope" in updated_project
        and "floor" in updated_project["envelope"]
        and isinstance(updated_project["envelope"]["floor"], list)
    ):
        floor_to_add: Floor = cast(
            Floor, {**new_floor, "bldgUseKey": building_area_key}
        )
        manager = FloorListManager(updated_project["envelope"]["floor"])
        updated_project["envelope"]["floor"] = manager.add_new(floor_to_add)
    else:
        raise ValueError("Envelope or floor array not found in project.")

    return updated_project


# *********** Assemblies or Components attached to wall or roof ***********


def add_skylight_to_project(
    project: dict[str, Any],
    building_area_key: str,
    new_skylight: Skylight,
    roof: Roof | None = None,
) -> dict[str, Any]:
    """Add a new skylight to a specific roof in the envelope using RoofListManager's add_new_skylight.

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
    # TODO: alteration projects allow orphaned skylights/windows/doors. Handle that case as well.
    updated_project = copy.deepcopy(project)

    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding skylight error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if updated_project.get("project") != "ALTERATION":
        if not roof:
            raise ValueError("Roof must be specified for non-alteration projects.")

        if roof.get("bldgUseKey") and roof.get("bldgUseKey") != building_area_key:
            raise ValueError(
                f"Roof's bldgUseKey '{roof.get('bldgUseKey')}' does not match the provided buildingAreaKey '{building_area_key}'."
            )

        if (
            "envelope" in updated_project
            and "roof" in updated_project["envelope"]
            and isinstance(updated_project["envelope"]["roof"], list)
        ):
            # Find the matching roof by assemblyType
            target_index = next(
                (
                    i
                    for i, r in enumerate(updated_project["envelope"]["roof"])
                    if r.get("assemblyType") == roof.get("assemblyType")
                ),
                -1,
            )
            if target_index == -1:
                raise ValueError("Specified roof not found in project.")

            roof_manager = RoofListManager(updated_project["envelope"]["roof"])
            updated_roof = roof_manager.add_new_skylight(
                updated_project["envelope"]["roof"][target_index], new_skylight
            )
            updated_project["envelope"]["roof"][target_index] = updated_roof
        else:
            raise ValueError("Envelope or roof array not found in project.")
    else:
        # For alteration projects, add skylight without specifying roof
        skylight_to_add: Skylight = cast(
            Skylight, {**new_skylight, "bldgUseKey": building_area_key}
        )
        if "envelope" in updated_project:
            skylight_manager = SkylightListManager(
                updated_project["envelope"].get("skylight", [])
            )
            updated_project["envelope"]["skylight"] = skylight_manager.add_new(
                skylight_to_add
            )

    return updated_project


def add_window_to_project(
    project: dict[str, Any],
    building_area_key: str,
    new_window: Window,
    wall: AgWall | BgWall | None = None,
) -> dict[str, Any]:
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
    updated_project = copy.deepcopy(project)

    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding window error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if updated_project.get("project") != "ALTERATION":
        if not wall:
            raise ValueError(
                "Wall (AgWall or BgWall) must be specified for non-alteration projects."
            )

        if wall.get("bldgUseKey") and wall.get("bldgUseKey") != building_area_key:
            raise ValueError(
                f"Wall's bldgUseKey '{wall.get('bldgUseKey')}' does not match buildingAreaKey '{building_area_key}'."
            )

        if "envelope" not in updated_project:
            raise ValueError("Envelope not found in project.")

        # Try to find in agWall array first
        if "agWall" in updated_project["envelope"] and isinstance(
            updated_project["envelope"]["agWall"], list
        ):
            ag_wall_index = next(
                (
                    i
                    for i, w in enumerate(updated_project["envelope"]["agWall"])
                    if w.get("assemblyType") == wall.get("assemblyType")
                ),
                -1,
            )
            if ag_wall_index != -1:
                ag_wall_manager = AgWallListManager(
                    updated_project["envelope"]["agWall"]
                )
                updated_ag_wall = ag_wall_manager.add_new_window(
                    updated_project["envelope"]["agWall"][ag_wall_index], new_window
                )
                updated_project["envelope"]["agWall"][ag_wall_index] = updated_ag_wall
                return updated_project

        # Try to find in bgWall array
        if "bgWall" in updated_project["envelope"] and isinstance(
            updated_project["envelope"]["bgWall"], list
        ):
            bg_wall_index = next(
                (
                    i
                    for i, w in enumerate(updated_project["envelope"]["bgWall"])
                    if w.get("assemblyType") == wall.get("assemblyType")
                ),
                -1,
            )
            if bg_wall_index != -1:
                bg_wall_list = cast(list[BgWall], updated_project["envelope"]["bgWall"])
                bg_wall_manager = BgWallListManager(bg_wall_list)
                updated_bg_wall = bg_wall_manager.add_new_window(
                    bg_wall_list[bg_wall_index], new_window
                )
                updated_project["envelope"]["bgWall"][bg_wall_index] = updated_bg_wall
                return updated_project

        raise ValueError("Specified wall not found in project.")
    else:
        # Alteration projects: orphaned windows
        window_to_add: Window = cast(
            Window, {**new_window, "bldgUseKey": building_area_key}
        )
        if "envelope" not in updated_project:
            raise ValueError("Envelope not found in project.")
        window_manager = WindowListManager(
            updated_project["envelope"].get("window", [])
        )
        updated_project["envelope"]["window"] = window_manager.add_new(window_to_add)

    return updated_project


def add_door_to_project(
    project: dict[str, Any],
    building_area_key: str,
    new_door: Door,
    wall: AgWall | BgWall | None = None,
) -> dict[str, Any]:
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
    updated_project = copy.deepcopy(project)

    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding door error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if updated_project.get("project") != "ALTERATION":
        if not wall:
            raise ValueError(
                "Wall (AgWall or BgWall) must be specified for non-alteration projects."
            )

        if wall.get("bldgUseKey") and wall.get("bldgUseKey") != building_area_key:
            raise ValueError(
                f"Wall's bldgUseKey '{wall.get('bldgUseKey')}' does not match buildingAreaKey '{building_area_key}'."
            )

        if "envelope" not in updated_project:
            raise ValueError("Envelope not found in project.")

        # Try to find in agWall array first
        if "agWall" in updated_project["envelope"] and isinstance(
            updated_project["envelope"]["agWall"], list
        ):
            ag_wall_index = next(
                (
                    i
                    for i, w in enumerate(updated_project["envelope"]["agWall"])
                    if w.get("assemblyType") == wall.get("assemblyType")
                ),
                -1,
            )
            if ag_wall_index != -1:
                ag_wall_manager = AgWallListManager(
                    updated_project["envelope"]["agWall"]
                )
                updated_ag_wall = ag_wall_manager.add_new_door(
                    updated_project["envelope"]["agWall"][ag_wall_index], new_door
                )
                updated_project["envelope"]["agWall"][ag_wall_index] = updated_ag_wall
                return updated_project

        # Try to find in bgWall array
        if "bgWall" in updated_project["envelope"] and isinstance(
            updated_project["envelope"]["bgWall"], list
        ):
            bg_wall_index = next(
                (
                    i
                    for i, w in enumerate(updated_project["envelope"]["bgWall"])
                    if w.get("assemblyType") == wall.get("assemblyType")
                ),
                -1,
            )
            if bg_wall_index != -1:
                bg_wall_manager = BgWallListManager(
                    updated_project["envelope"]["bgWall"]
                )
                updated_bg_wall = bg_wall_manager.add_new_door(
                    updated_project["envelope"]["bgWall"][bg_wall_index], new_door
                )
                updated_project["envelope"]["bgWall"][bg_wall_index] = updated_bg_wall
                return updated_project

        raise ValueError("Specified wall not found in project.")
    else:
        # Alteration projects: orphaned doors
        door_to_add: Door = cast(Door, {**new_door, "bldgUseKey": building_area_key})
        if "envelope" not in updated_project:
            raise ValueError("Envelope not found in project.")
        door_manager = DoorListManager(updated_project["envelope"].get("door", []))
        updated_project["envelope"]["door"] = door_manager.add_new(door_to_add)

    return updated_project


# TODO: verify when thermal bridges are needed
def add_thermal_bridge_to_project(
    project: dict[str, Any],
    building_area_key: str,
    ag_wall: AgWall,
    thermal_bridge_type: ThermalBridgeTypeOptions = "THERMAL_BRIDGE_OTHER",
    thermal_bridge_category: ThermalBridgeCategoryOptions = "THERMAL_BRIDGE_UNCATEGORIZED",
    thermal_bridge_compliance_type: ThermalBridgeComplianceTypeOptions = "THERMAL_BRIDGE_NON_PRESCRIPTIVE",
    psi_factor: float = 0.0,
    chi_factor: float = 0.0,
    thermal_bridge_length: float = 0.0,
) -> dict[str, Any]:
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
    updated_project = copy.deepcopy(project)

    if (
        "lighting" not in updated_project
        or "wholeBldgUse" not in updated_project["lighting"]
        or not isinstance(updated_project["lighting"]["wholeBldgUse"], list)
    ):
        raise ValueError("No building area found in project.")

    building_area_exists = any(
        item.get("key") == building_area_key
        for item in updated_project["lighting"]["wholeBldgUse"]
    )

    if not building_area_exists:
        raise ValueError(
            f"Adding thermal bridge error: Building area with key '{building_area_key}' not found in lighting.wholeBldgUse list."
        )

    if not ag_wall:
        raise ValueError("AgWall must be specified for thermal bridges.")

    if ag_wall.get("bldgUseKey") and ag_wall.get("bldgUseKey") != building_area_key:
        raise ValueError(
            f"AgWall's bldgUseKey '{ag_wall.get('bldgUseKey')}' does not match buildingAreaKey '{building_area_key}'."
        )

    if (
        "envelope" not in updated_project
        or "agWall" not in updated_project["envelope"]
        or not isinstance(updated_project["envelope"]["agWall"], list)
    ):
        raise ValueError("Envelope or agWall array not found in project.")

    ag_wall_index = next(
        (
            i
            for i, w in enumerate(updated_project["envelope"]["agWall"])
            if w.get("assemblyType") == ag_wall.get("assemblyType")
        ),
        -1,
    )

    if ag_wall_index == -1:
        raise ValueError("Specified agWall not found in project.")

    manager = AgWallListManager(updated_project["envelope"]["agWall"])
    updated_wall = manager.add_new_thermal_bridge(
        updated_project["envelope"]["agWall"][ag_wall_index],
        thermal_bridge_type,
        thermal_bridge_category,
        thermal_bridge_compliance_type,
        psi_factor,
        chi_factor,
        thermal_bridge_length,
    )
    updated_project["envelope"]["agWall"][ag_wall_index] = updated_wall

    return updated_project
