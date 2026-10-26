"""Water heater manager for COMcheck projects."""

from comcheck_api.types.core_types import ServiceWaterHeatingSystem
from comcheck_api.managers.data_manager import DataManager


class WaterHeaterListManager(DataManager[ServiceWaterHeatingSystem]):
    """Manager for water heaters with automatic unique description generation.

    This manager handles water heaters identified by their description.
    """

    model_type = ServiceWaterHeatingSystem
