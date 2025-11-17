"""AgWall (exterior wall) manager for COMcheck projects."""

from typing import Any

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
            identifier="assemblyType",
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
        thermal_bridge_type=ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER,
        thermal_bridge_category=ThermalBridgeCategoryOptions.THERMAL_BRIDGE_UNCATEGORIZED,
        thermal_bridge_compliance_type=ThermalBridgeComplianceTypeOptions.THERMAL_BRIDGE_NON_PRESCRIPTIVE,
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
        tb_manager = self.get_thermal_bridges(ag_wall)

        # Initialize new thermal bridge
        initialize_thermal_bridge = {
            **DEFAULT_THERMAL_BRIDGE,
            "thermalBridgeType": thermal_bridge_type,
            "thermalBridgeCategory": thermal_bridge_category,
            "thermalBridgeComplianceType": thermal_bridge_compliance_type,
            "psiFactor": psi_factor,
            "chiFactor": chi_factor,
            "thermalBridgeLength": thermal_bridge_length,
        }

        # Add to wall and update
        ag_wall["thermalBridge"] = tb_manager.add_new(initialize_thermal_bridge)
        return self.modify_one(ag_wall["assemblyType"], ag_wall)

    def get_thermal_bridges(self, ag_wall: AgWall) -> ThermalBridgeListManager:
        """Get the thermal bridge manager for an AgWall.

        Args:
            ag_wall: The AgWall to get thermal bridges from.

        Returns:
            A ThermalBridgeListManager for the AgWall's thermal bridges.
        """
        # Ensure thermalBridge array exists
        if not ag_wall.get("thermalBridge") or not isinstance(
            ag_wall.get("thermalBridge"), list
        ):
            ag_wall["thermalBridge"] = []

        return ThermalBridgeListManager(ag_wall["thermalBridge"])

    def add_new_door(self, ag_wall: AgWall, door: Door) -> AgWall:
        """Add a new door to an AgWall.

        Args:
            ag_wall: The AgWall to add the door to.
            door: The door configuration to add.

        Returns:
            The updated AgWall.
        """
        # Ensure door array exists
        if not ag_wall.get("door") or not isinstance(ag_wall.get("door"), list):
            ag_wall["door"] = []

        # Create door manager
        door_mgr = DoorListManager(ag_wall["door"])

        # Generate default door assembly
        door_count = len(ag_wall["door"]) + 1
        initialize_door = generate_assembly(
            ag_wall["bldgUseKey"],
            f"Door in Exterior wall {door_count}",
            "Door",
        )

        # Merge with provided door data and add
        merged_door = {**door, **initialize_door}
        ag_wall["door"] = door_mgr.add_new(merged_door)
        return self.modify_one(ag_wall["assemblyType"], ag_wall)

    def add_new_window(self, ag_wall: AgWall, window: Window) -> AgWall:
        """Add a new window to an AgWall.

        Args:
            ag_wall: The AgWall to add the window to.
            window: The window configuration to add.

        Returns:
            The updated AgWall.
        """
        # Ensure window array exists
        if not ag_wall.get("window") or not isinstance(ag_wall.get("window"), list):
            ag_wall["window"] = []

        # Create window manager
        window_mgr = WindowListManager(ag_wall["window"])

        # Generate default window assembly
        window_count = len(ag_wall["window"]) + 1
        initialize_window = generate_assembly(
            ag_wall["bldgUseKey"],
            f"Window in Exterior wall {window_count}",
            "Window",
        )

        # Merge with provided window data and add
        merged_window = {**window, **initialize_window}
        ag_wall["window"] = window_mgr.add_new(merged_window)
        return self.modify_one(ag_wall["assemblyType"], ag_wall)
