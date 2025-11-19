"""AgWall (exterior wall) manager for COMcheck projects."""

from typing import cast
from src.constants.envelope_constants import DEFAULT_THERMAL_BRIDGE
from src.types.core_types import (
    AgWall,
    Door,
    ThermalBridge,
    ThermalBridgeCategoryOptions,
    ThermalBridgeComplianceTypeOptions,
    ThermalBridgeTypeOptions,
    Window,
)
from src.utilities.data_manager import DataManager
from src.utilities.envelope_utilities import generate_assembly

from .door import DoorListManager
from .window import WindowListManager


class ThermalBridgeListManager(DataManager[ThermalBridge]):
    """Manager for ThermalBridge assemblies."""

    def __init__(self, initial_thermal_bridges: list[ThermalBridge]):
        """Initialize the ThermalBridge list manager.
        Args:
            initial_thermal_bridges: Initial list of ThermalBridge items.
        """
        super().__init__(
            initial_data=initial_thermal_bridges,
            identifier="id",
            schema_reference="ThermalBridge",
        )


class AgWallListManager(DataManager[AgWall]):
    """Manager for AgWall assemblies with support for nested components.

    This manager handles AgWall assemblies and their nested components
    (thermal bridges, doors, windows).
    """

    def __init__(self, initial_ag_walls: list[AgWall]):
        """Initialize the AgWall list manager.

        Args:
            initial_ag_walls: Initial list of AgWall items.
        """
        super().__init__(
            initial_data=initial_ag_walls,
            identifier="assemblyType",
            schema_reference="AgWall",
        )

    def add_new_thermal_bridge(
        self,
        ag_wall: AgWall,
        thermal_bridge_type: ThermalBridgeTypeOptions = "THERMAL_BRIDGE_OTHER",
        thermal_bridge_category: ThermalBridgeCategoryOptions = "THERMAL_BRIDGE_UNCATEGORIZED",
        thermal_bridge_compliance_type: ThermalBridgeComplianceTypeOptions = "THERMAL_BRIDGE_NON_PRESCRIPTIVE",
        psi_factor: float = 0.0,
        chi_factor: float = 0.0,
        thermal_bridge_length: float = 0.0,
    ) -> AgWall:
        """Add a new thermal bridge to an AgWall.

        Args:
            ag_wall: The AgWall to add the thermal bridge to.
            thermal_bridge_type: Type of thermal bridge.
            thermal_bridge_category: Category of thermal bridge.
            thermal_bridge_compliance_type: Compliance type.
            psi_factor: Linear thermal transmittance (Psi factor).
            chi_factor: Point thermal transmittance (Chi factor).
            thermal_bridge_length: Length of the thermal bridge.

        Returns:
            The updated AgWall.
        """
        # Get thermal bridge manager
        thermal_bridge_manager: ThermalBridgeListManager = ThermalBridgeListManager(
            ag_wall["thermalBridge"] if "thermalBridge" in ag_wall else []
        )

        # Initialize new thermal bridge
        initialize_thermal_bridge: ThermalBridge = {
            **DEFAULT_THERMAL_BRIDGE,
            "thermalBridgeType": thermal_bridge_type,
            "thermalBridgeCategory": thermal_bridge_category,
            "thermalBridgeComplianceType": thermal_bridge_compliance_type,
            "psiFactor": psi_factor,
            "chiFactor": chi_factor,
            "thermalBridgeLength": thermal_bridge_length,
        }

        # Add to wall and update
        ag_wall["thermalBridge"] = thermal_bridge_manager.add_new(
            initialize_thermal_bridge
        )
        return self.modify_one(ag_wall["assemblyType"], ag_wall)

    def add_new_door(self, ag_wall: AgWall, door: Door) -> AgWall:
        """Add a new door to an AgWall.

        Args:
            ag_wall: The AgWall to add the door to.
            door: The door configuration to add.

        Returns:
            The updated AgWall.
        """

        # Create door manager
        door_manager = DoorListManager(ag_wall["door"] if "door" in ag_wall else [])

        # Generate default door assembly
        door_count = len(ag_wall["door"]) + 1
        initialize_door = generate_assembly(
            ag_wall["bldgUseKey"],
            f"Door in Exterior wall {door_count}",
            "Door",
        )

        # Merge with provided door data and add
        merged_door: Door = cast(Door, {**door, **initialize_door})
        ag_wall["door"] = door_manager.add_new(merged_door)
        return self.modify_one(ag_wall["assemblyType"], ag_wall)

    def add_new_window(self, ag_wall: AgWall, window: Window) -> AgWall:
        """Add a new window to an AgWall.

        Args:
            ag_wall: The AgWall to add the window to.
            window: The window configuration to add.

        Returns:
            The updated AgWall.
        """
        # Create window manager
        window_manager = WindowListManager(
            ag_wall["window"] if "window" in ag_wall else []
        )

        # Generate default window assembly
        window_count = len(ag_wall["window"]) + 1
        initialize_window = generate_assembly(
            ag_wall["bldgUseKey"],
            f"Window in Exterior wall {window_count}",
            "Window",
        )

        # Merge with provided window data and add
        merged_window: Window = cast(Window, {**window, **initialize_window})
        ag_wall["window"] = window_manager.add_new(merged_window)
        return self.modify_one(ag_wall["assemblyType"], ag_wall)
