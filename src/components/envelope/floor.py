"""Floor list manager for COMcheck projects."""

from typing import Any

from src.types.core_types import Floor
from src.utilities.data_manager import DataManager


class FloorListManager(DataManager[Floor]):
    """Manager for Floor assemblies."""

    def __init__(self, initial_floors: list[Floor]):
        """Initialize the Floor list manager.

        Args:
            initial_floors: Initial list of floor items.
        """
        super().__init__(
            initial_data=initial_floors,
            identifier="assemblyType",
            schema_reference="Floor",
        )
