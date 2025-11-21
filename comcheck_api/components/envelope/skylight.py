"""Skylight list manager for COMcheck projects."""

from typing import Any

from comcheck_api.types.core_types import Skylight
from comcheck_api.utilities.data_manager import DataManager


class SkylightListManager(DataManager[Skylight]):
    """Manager for Skylight assemblies."""

    def __init__(self, initial_skylights: list[Skylight]):
        """Initialize the Skylight list manager.

        Args:
            initial_skylights: Initial list of Skylight items.
        """
        super().__init__(
            initial_data=initial_skylights,
            identifier="assemblyType",
            schema_reference="Skylight",
        )
