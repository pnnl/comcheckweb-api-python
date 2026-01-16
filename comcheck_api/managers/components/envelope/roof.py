"""Roof manager for COMcheck projects."""

from typing import cast

from comcheck_api.types.core_types import Roof, Skylight
from comcheck_api.managers.data_manager import DataManager
from comcheck_api.utilities.envelope_utilities import generate_assembly

from .skylight import SkylightListManager


class RoofListManager(DataManager[Roof]):
    """Manager for Roof assemblies with support for nested skylights.

    This manager handles Roof assemblies and their nested skylights,
    with automatic unique assemblyType generation.
    """
    model_type = Roof

    def add_new_skylight(self, roof: Roof, skylight: Skylight) -> Roof:
        """Add a new skylight to a Roof.

        Args:
            roof: The Roof to add the skylight to.
            skylight: The skylight configuration to add.

        Returns:
            The updated Roof.
        """
        return self.add_subcomponent(roof, skylight)