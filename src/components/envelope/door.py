"""Door list manager for COMcheck projects."""

from typing import Any

from src.types.core_types import Door
from src.utilities.data_manager import DataManager


class DoorListManager(DataManager[Door]):
    """Manager for Door assemblies."""

    def __init__(self, initial_doors: list[Door]):
        """Initialize the Door list manager.

        Args:
            initial_doors: Initial list of door items.
        """
        super().__init__(
            initial_data=initial_doors,
            identifier="assemblyType",
            schema_reference="Door",
        )
