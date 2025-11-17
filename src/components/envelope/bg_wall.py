"""BgWall (basement wall) manager for COMcheck projects."""

from typing import Any

from src.types.core_types import BgWall, Door, Window
from src.utilities.data_manager import DataManager
from src.utilities.envelope_utilities import generate_assembly

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
        # Ensure door array exists
        if not bg_wall.get("door") or not isinstance(bg_wall.get("door"), list):
            bg_wall["door"] = list[Door]([])

        # Create door manager
        door_mgr = DoorListManager(bg_wall["door"])

        # Generate default door assembly
        door_count = len(bg_wall["door"]) + 1
        initialize_door = generate_assembly(
            bg_wall["bldgUseKey"],
            f"Door {door_count}",
            "Door",
        )

        # Merge with provided door data and add
        merged_door = {**door, **initialize_door}
        bg_wall["door"] = door_mgr.add_new(merged_door)
        return self.modify_one(bg_wall["assemblyType"], bg_wall)

    def add_new_window(self, bg_wall: BgWall, window: Window) -> BgWall:
        """Add a new window to a BgWall.

        Args:
            bg_wall: The BgWall to add the window to.
            window: The window configuration to add.

        Returns:
            The updated BgWall.
        """
        # Ensure window array exists
        if not bg_wall.get("window") or not isinstance(bg_wall.get("window"), list):
            bg_wall["window"] = []

        # Create window manager
        window_mgr = WindowListManager(bg_wall["window"])

        # Generate default window assembly
        window_count = len(bg_wall["window"]) + 1
        initialize_window = generate_assembly(
            bg_wall["bldgUseKey"],
            f"Window {window_count}",
            "Window",
        )

        # Merge with provided window data and add
        merged_window = {**window, **initialize_window}
        bg_wall["window"] = window_mgr.add_new(merged_window)
        return self.modify_one(bg_wall["assemblyType"], bg_wall)
