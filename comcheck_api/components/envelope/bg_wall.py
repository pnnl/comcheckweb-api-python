"""BgWall (basement wall) manager for COMcheck projects."""

from typing import cast

from comcheck_api.types.core_types import BgWall, Door, Window
from comcheck_api.utilities.data_manager import DataManager
from comcheck_api.utilities.envelope_utilities import generate_assembly

from .door import DoorListManager
from .window import WindowListManager


class BgWallListManager(DataManager[BgWall]):
    """Manager for BgWall assemblies with support for nested components.

    This manager handles BgWall assemblies and their nested components
    (doors, windows).
    """

    def __init__(self, initial_bg_walls: list[BgWall]):
        """Initialize the BgWall list manager.

        Args:
            initial_bg_walls: Initial list of BgWall items.
        """
        super().__init__(
            initial_data=initial_bg_walls,
            identifier="assemblyType",
            schema_reference="BgWall",
        )

    def add_new_door(self, bg_wall: BgWall, door: Door) -> BgWall:
        """Add a new door to a BgWall.

        Args:
            bg_wall: The BgWall to add the door to.
            door: The door configuration to add.

        Returns:
            The updated BgWall.
        """
        # Create door manager
        door_manager = DoorListManager(bg_wall["door"] if "door" in bg_wall else [])

        # Generate default door assembly
        door_count = len(bg_wall["door"]) + 1
        initialize_door = generate_assembly(
            bg_wall["bldgUseKey"],
            f"Door {door_count}",
            "Door",
        )

        # Merge with provided door data and add
        merged_door: Door = cast(Door, {**door, **initialize_door})
        bg_wall["door"] = door_manager.add_new(merged_door)
        return self.modify_one(bg_wall["assemblyType"], bg_wall)

    def add_new_window(self, bg_wall: BgWall, window: Window) -> BgWall:
        """Add a new window to a BgWall.

        Args:
            bg_wall: The BgWall to add the window to.
            window: The window configuration to add.

        Returns:
            The updated BgWall.
        """
        # Create window manager
        window_manager = WindowListManager(
            bg_wall["window"] if "window" in bg_wall else []
        )

        # Generate default window assembly
        window_count = len(bg_wall["window"]) + 1
        initialize_window = generate_assembly(
            bg_wall["bldgUseKey"],
            f"Window {window_count}",
            "Window",
        )

        # Merge with provided window data and add
        merged_window: Window = cast(Window, {**window, **initialize_window})
        bg_wall["window"] = window_manager.add_new(merged_window)
        return self.modify_one(bg_wall["assemblyType"], bg_wall)
