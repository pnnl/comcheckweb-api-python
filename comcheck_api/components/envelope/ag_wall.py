"""AgWall (exterior wall) manager for COMcheck projects."""

from typing import Dict, cast, Union
from comcheck_api.api.api_services import COMCheckApiService
from comcheck_api.constants.envelope_constants import DEFAULT_THERMAL_BRIDGE
from comcheck_api.types.api_types import (
    AgWallAssembliesUValuesArgs,
    AssembliesUValuesArgs,
)
from comcheck_api.types.core_types import (
    AgWall,
    Door,
    ThermalBridge,
    ThermalBridgeCategoryOptions,
    ThermalBridgeComplianceTypeOptions,
    ThermalBridgeTypeOptions,
    Window,
)
from comcheck_api.utilities.data_manager import DataManager


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
    model_type = AgWall

    def add_new_thermal_bridge(
        self,
        ag_wall: AgWall,
        thermal_bridge_type: Union[ThermalBridgeTypeOptions, str] = ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER,
        thermal_bridge_category: Union[ThermalBridgeCategoryOptions, str] = ThermalBridgeCategoryOptions.THERMAL_BRIDGE_UNCATEGORIZED,
        thermal_bridge_compliance_type: Union[ThermalBridgeComplianceTypeOptions, str] = ThermalBridgeComplianceTypeOptions.THERMAL_BRIDGE_NON_PRESCRIPTIVE,
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
        # Initialize new thermal bridge
        initialize_thermal_bridge: ThermalBridge = ThermalBridge(
            thermalBridgeType=thermal_bridge_type,
            thermalBridgeCategory=thermal_bridge_category,
            thermalBridgeComplianceType=thermal_bridge_compliance_type,
            psiFactor=psi_factor,
            chiFactor=chi_factor,
            thermalBridgeLength=thermal_bridge_length
        )

        return self.add_subcomponent(ag_wall, initialize_thermal_bridge)

    def add_new_door(self, ag_wall: AgWall, door: Door) -> AgWall:
        """Add a new door to an AgWall.

        Args:
            ag_wall: The AgWall to add the door to.
            door: The door configuration to add.

        Returns:
            The updated AgWall.
        """
        return self.add_subcomponent(ag_wall, door)

    def add_new_window(self, ag_wall: AgWall, window: Window) -> AgWall:
        """Add a new window to an AgWall.

        Args:
            ag_wall: The AgWall to add the window to.
            window: The window configuration to add.

        Returns:
            The updated AgWall.
        """
        return self.add_subcomponent(ag_wall, window)
    
    def get_u_values(self, code_version) -> Dict:
        """Add a new window to an AgWall.

        Args:
            ag_wall: The AgWall to add the window to.
            window: The window configuration to add.

        Returns:
            The updated AgWall.
        """
        client = COMCheckApiService()
        client.get_assemblies_u_values(code_version)

        payload = AssembliesUValuesArgs(
            agWall=[AgWallAssembliesUValuesArgs(**data) for data in self._data]
        ).model_dump(mode="json")

        return client.get_assemblies_u_values(code_version, payload=payload)
