"""Tests for RoofListManager."""

import pytest

from comcheck_api.components.envelope.roof import RoofListManager
from comcheck_api.constants.envelope_constants import DEFAULT_ROOF, DEFAULT_SKYLIGHT


class TestRoofListManager:
    """Test suite for RoofListManager."""

    def test_initialization_with_provided_data(self):
        """Should initialize with provided data."""
        manager = RoofListManager([DEFAULT_ROOF])
        assert manager.get_all() == [DEFAULT_ROOF]

    def test_add_skylight_to_roof(self):
        """Should be able to add skylight to roof."""
        manager = RoofListManager([DEFAULT_ROOF])
        manager.add_new_skylight(DEFAULT_ROOF, DEFAULT_SKYLIGHT)
        roof = manager.get_by_identifier(DEFAULT_ROOF["assemblyType"])
        assert roof is not None
        assert len(roof["skylight"]) == 1

    def test_add_duplicate_roof_throws_error(self):
        """Should throw if adding a duplicate roof."""
        manager = RoofListManager([DEFAULT_ROOF])
        with pytest.raises(
            ValueError, match="Item with assemblyType .* already exists"
        ):
            manager.add_new(DEFAULT_ROOF)
