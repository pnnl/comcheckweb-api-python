"""Roof manager for COMcheck projects."""

from typing import cast

from comcheck_api.types.core_types import Roof, Skylight
from comcheck_api.utilities.data_manager import DataManager
from comcheck_api.utilities.envelope_utilities import generate_assembly

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
        assembly_type = str(roof["assemblyType"] if "assemblyType" in roof else "")

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
        while any(r["assemblyType"] == new_assembly_type for r in self._data):
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
        # Create skylight manager
        skylight_manager = SkylightListManager(
            roof["skylight"] if "skylight" in roof else []
        )

        # Generate default skylight assembly
        skylight_count = len(roof["skylight"]) + 1
        initialize_skylight = generate_assembly(
            roof["bldgUseKey"],
            f"Skylight {skylight_count}",
            "Skylight",
        )

        # Merge with provided skylight data and add
        merged_skylight: Skylight = cast(Skylight, {**skylight, **initialize_skylight})  # type: ignore[typeddict-item]
        roof["skylight"] = skylight_manager.add_new(merged_skylight)
        return self.modify_one(roof["assemblyType"], roof)
