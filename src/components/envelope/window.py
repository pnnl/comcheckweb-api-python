"""Window list manager for COMcheck projects."""

from typing import Any

from src.types.core_types import Window
from src.utilities.data_manager import DataManager


class WindowListManager(DataManager[Window]):
    """Manager for Window assemblies."""

    def __init__(self, initial_windows: list[Window]):
        """Initialize the Window list manager.

        Args:
            initial_windows: Initial list of window items.
        """
        super().__init__(
            initial_data=initial_windows,
            identifier="assemblyType",
            schema_reference="Window",
        )
