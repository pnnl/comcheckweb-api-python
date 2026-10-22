"""HVAC plant manager for COMcheck projects."""

from comcheck_api.types.core_types import HVACPlant
from comcheck_api.managers.data_manager import DataManager


class HVACPlantListManager(DataManager[HVACPlant]):
    """Manager for HVAC plants with automatic unique description generation.

    This manager handles HVAC plants identified by their description.
    """

    model_type = HVACPlant
