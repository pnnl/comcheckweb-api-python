"""Building area list manager for COMcheck projects."""

from typing import Any

from comcheck_api.types.core_types import WholeBldgUse
from comcheck_api.utilities.data_manager import DataManager


class BuildingAreaListManager(DataManager[WholeBldgUse]):
    """Manager for WholeBldgUse (building area) items."""
    model_type = WholeBldgUse
