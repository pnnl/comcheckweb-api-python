"""Fan system manager for COMcheck projects."""

from comcheck_api.types.core_types import Fan, FanSystem
from comcheck_api.managers.data_manager import DataManager


class FanSystemListManager(DataManager[FanSystem]):
    """Manager for fan systems with support for nested fans.

    This manager handles fan systems and their nested fans,
    with automatic unique description generation.
    """

    model_type = FanSystem

    def add_new_fan(self, fan_system: FanSystem, fan: Fan) -> FanSystem:
        """Add a new fan to a fan system.

        Args:
            fan_system: The fan system to add the fan to.
            fan: The fan configuration to add.

        Returns:
            The updated fan system.
        """
        return self.add_subcomponent(fan_system, fan)

    def update_fan(self, fan_system: FanSystem, fan_description: str, updates: dict | Fan) -> FanSystem:
        """Update an existing fan in a fan system.

        Args:
            fan_system: The fan system containing the fan.
            fan_description: The description of the fan to update.
            updates: Partial updates (dict) or full Fan object to apply.

        Returns:
            The updated fan system.
        """
        from comcheck_api.managers.data_manager import DataManager

        current_fans = getattr(fan_system, "fan", []) or []
        fan_manager: DataManager[Fan] = DataManager(
            initial_data=current_fans, model_type=Fan
        )

        fan_manager.modify_one(id_value=fan_description, updates=updates)
        updated_fan_system = fan_system.model_copy(deep=True)
        updated_fan_system.fan = fan_manager.get_all()

        # Update the fan system in the manager
        return self.modify_one(
            id_value=getattr(fan_system, self._identifier),
            updates=updated_fan_system
        )

    def remove_fan(self, fan_system: FanSystem, fan_description: str) -> FanSystem:
        """Remove a fan from a fan system.

        Args:
            fan_system: The fan system containing the fan.
            fan_description: The description of the fan to remove.

        Returns:
            The updated fan system.
        """
        from comcheck_api.managers.data_manager import DataManager

        current_fans = getattr(fan_system, "fan", []) or []
        fan_manager: DataManager[Fan] = DataManager(
            initial_data=current_fans, model_type=Fan
        )

        was_deleted = fan_manager.delete_one(fan_description)
        if not was_deleted:
            raise ValueError(
                f"Fan with description '{fan_description}' not found in fan system."
            )

        updated_fan_system = fan_system.model_copy(deep=True)
        updated_fan_system.fan = fan_manager.get_all()

        # Update the fan system in the manager
        return self.modify_one(
            id_value=getattr(fan_system, self._identifier),
            updates=updated_fan_system
        )
