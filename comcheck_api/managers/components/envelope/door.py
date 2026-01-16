"""Door list manager for COMcheck projects."""

from typing import Any

from comcheck_api.types.core_types import Door
from comcheck_api.managers.data_manager import DataManager


class DoorListManager(DataManager[Door]):
    """Manager for Door assemblies."""
    model_type = Door