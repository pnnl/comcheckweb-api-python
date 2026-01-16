"""Tests for DoorListManager."""

from comcheck_api.managers.components.envelope.door import DoorListManager


def test_initialization_with_provided_data(door):
    """Test initialization with provided data."""
    manager = DoorListManager([door])
    assert manager.get_all() == [door]
