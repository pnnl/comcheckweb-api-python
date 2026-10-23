"""HVAC system manager for COMcheck projects."""

from comcheck_api.types.core_types import HVACSystem
from comcheck_api.managers.data_manager import DataManager


class HVACSystemListManager(DataManager[HVACSystem]):
    """Manager for HVAC systems with automatic unique description generation.

    This manager handles HVAC systems identified by their description.
    """

    model_type = HVACSystem
