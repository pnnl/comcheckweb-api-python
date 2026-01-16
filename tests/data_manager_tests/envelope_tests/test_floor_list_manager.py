"""Tests for FloorListManager."""

from comcheck_api.managers.components.envelope.floor import FloorListManager


def test_initialization_with_provided_data(floor):
    """Test initialization with provided data."""
    manager = FloorListManager([floor])
    assert manager.get_all() == [floor]
