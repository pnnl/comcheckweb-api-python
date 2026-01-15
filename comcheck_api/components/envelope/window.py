"""Window list manager for COMcheck projects."""

from typing import Any

from comcheck_api.types.core_types import Window
from comcheck_api.managers.data_manager import DataManager


class WindowListManager(DataManager[Window]):
    """Manager for Window assemblies."""
    model_type = Window