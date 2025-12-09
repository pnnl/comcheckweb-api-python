"""Skylight list manager for COMcheck projects."""

from typing import Any

from comcheck_api.types.core_types import Skylight
from comcheck_api.utilities.data_manager import DataManager


class SkylightListManager(DataManager[Skylight]):
    """Manager for Skylight assemblies."""
    model_type = Skylight
