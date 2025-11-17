"""Roof manager for COMcheck projects."""

from typing import Any

from src.types.core_types import Roof, Skylight
from src.utilities.data_manager import DataManager
from src.utilities.envelope_utilities import generate_assembly

from .skylight import SkylightListManager


class RoofListManager(DataManager[Roof]):
    """Manager for Roof assemblies with support for nested skylights.

    This manager handles Roof assemblies and their nested skylights,
    with automatic unique assemblyType generation.
    """

    def __init__(self, initial_roofs: list[Roof]):
        """Initialize the Roof list manager.

        Args:
            initial_roofs: Initial list of Roof items.
        """
        super().__init__(
            initial_data=None,  # Don't add items yet, we'll add them with custom logic
            identifier="assemblyType",
            schema_reference="Roof",
        )
        self._initial_count = len(initial_roofs) if initial_roofs else 0

        # Add initial items with custom add_new logic
        if initial_roofs:
            for roof in initial_roofs:
                self.add_new(roof)

    def add_new(self, roof: Roof) -> list[Roof]:
        """Add a new Roof item with automatic unique assemblyType generation.

        If the roof doesn't have an assemblyType or it's not unique,
        generates a unique assemblyType in the format "Roof:Roof{counter}".

        Args:
            roof: The roof to add.

        Returns:
            The updated list of roofs.
        """
        assembly_type = roof.get("assemblyType", "")

        # Check if assemblyType is missing or doesn't start with "Roof:"
        if not assembly_type or not assembly_type.startswith("Roof:"):
            roof["assemblyType"] = self._generate_unique_assembly_type()
        else:
            # Check if the assemblyType is unique
            if any(r.get("assemblyType") == assembly_type for r in self._data):
                roof["assemblyType"] = self._generate_unique_assembly_type()

        return super().add_new(roof)

    def _generate_unique_assembly_type(self) -> str:
        """Generate a unique assemblyType for a roof.

        Returns:
            A unique assemblyType string in the format "Roof:Roof{counter}".
        """
        counter = self._initial_count + 1
        new_assembly_type = f"Roof:Roof{counter}"

        # Ensure uniqueness
        while any(r.get("assemblyType") == new_assembly_type for r in self._data):
            counter += 1
            new_assembly_type = f"Roof:Roof{counter}"

        return new_assembly_type

    def add_new_skylight(self, roof: Roof, skylight: Skylight) -> Roof:
        """Add a new skylight to a Roof.

        Args:
            roof: The Roof to add the skylight to.
            skylight: The skylight configuration to add.

        Returns:
            The updated Roof.
        """
        # Ensure skylight array exists
        if not roof.get("skylight") or not isinstance(roof.get("skylight"), list):
            roof["skylight"] = []

        # Create skylight manager
        skylight_mgr = SkylightListManager(roof["skylight"])

        # Generate default skylight assembly
        skylight_count = len(roof["skylight"]) + 1
        initialize_skylight = generate_assembly(
            roof["bldgUseKey"],
            f"Skylight {skylight_count}",
            "Skylight",
        )

        # Merge with provided skylight data and add
        merged_skylight = {**skylight, **initialize_skylight}
        roof["skylight"] = skylight_mgr.add_new(merged_skylight)
        return self.modify_one(roof["assemblyType"], roof)
