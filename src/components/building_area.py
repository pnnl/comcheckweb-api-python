"""Building area list manager for COMcheck projects."""

from typing import Any

from src.types.core_types import WholeBldgUse
from src.utilities.data_manager import DataManager


class BuildingAreaListManager(DataManager[WholeBldgUse]):
    """Manager for WholeBldgUse (building area) items."""

    def __init__(self, initial_whole_bldg_use: list[dict[str, Any]]):
        """Initialize the building area list manager.

        Args:
            initial_whole_bldg_use: Initial list of building area items.
        """
        super().__init__(
            initial_data=initial_whole_bldg_use,
            identifier="key",
            schema_reference="WholeBldgUse",
        )
