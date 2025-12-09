"""Floor list manager for COMcheck projects."""

from typing import Any

from comcheck_api.types.core_types import Floor
from comcheck_api.utilities.data_manager import DataManager


class FloorListManager(DataManager[Floor]):
    """Manager for Floor assemblies."""
    model_type = Floor