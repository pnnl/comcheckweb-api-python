"""Building area list manager for COMcheck projects."""

from typing import Any

from comcheck_api.types.core_types import WholeBldgUse
from comcheck_api.utilities.data_manager import DataManager


class BuildingAreaListManager(DataManager[WholeBldgUse]):
    """Manager for WholeBldgUse (building area) items."""

    def __init__(self, initial_whole_bldg_use: list[WholeBldgUse]):
        """Initialize the building area list manager.

        Args:
            initial_whole_bldg_use: Initial list of building area items.
        """
        super().__init__(
            initial_data=initial_whole_bldg_use,
            identifier="key",
            schema_reference="WholeBldgUse",
        )
