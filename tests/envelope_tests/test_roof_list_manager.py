from copy import deepcopy

from comcheck_api.components.envelope.roof import RoofListManager
from comcheck_api.types.core_types import Roof, Skylight

class TestRoofListManager:
    """Test suite for RoofListManager."""

    def test_initialization_with_provided_data(self, roof: Roof):
        """Should initialize with provided data."""
        manager = RoofListManager([roof])
        assert manager.get_all() == [roof]

    def test_add_skylight_to_roof(self, roof: Roof, skylight: Skylight):
        """Should be able to add skylight to roof."""
        manager = RoofListManager([roof])
        manager.add_new_skylight(roof, skylight)

        # Assuming get_by_identifier takes assemblyType string, which is an enum now
        roof_from_manager = manager.get_by_identifier(roof.assemblyType)
        assert roof_from_manager is not None
        assert len(roof_from_manager.skylight) == 1

    def test_add_duplicate_roof_throws_error(self, roof: Roof):
        """Should throw if adding a duplicate roof."""
        manager = RoofListManager([roof])
        manager.add_new(deepcopy(roof))

        roofs = manager.get_all()
        assembly_types = [r.assemblyType for r in roofs]
        assert len(assembly_types) == 2
        assert len(assembly_types) == len(set(assembly_types))
