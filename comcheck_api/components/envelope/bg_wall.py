"""BgWall (basement wall) manager for COMcheck projects."""


from comcheck_api.types.core_types import BgWall, Door, Window
from comcheck_api.utilities.data_manager import DataManager


class BgWallListManager(DataManager[BgWall]):
    """Manager for BgWall assemblies with support for nested components.

    This manager handles BgWall assemblies and their nested components
    (doors, windows).
    """
    model_type = BgWall

    def add_new_door(self, bg_wall: BgWall, door: Door) -> BgWall:
        """Add a new door to a BgWall.

        Args:
            bg_wall: The BgWall to add the door to.
            door: The door configuration to add.

        Returns:
            The updated BgWall.
        """
        return self.add_subcomponent(bg_wall, door)

    def add_new_window(self, bg_wall: BgWall, window: Window) -> BgWall:
        """Add a new window to a BgWall.

        Args:
            bg_wall: The BgWall to add the window to.
            window: The window configuration to add.

        Returns:
            The updated BgWall.
        """
        # Create window manager
        return self.add_subcomponent(bg_wall, window)
