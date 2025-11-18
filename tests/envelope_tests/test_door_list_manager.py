"""Tests for DoorListManager."""

from src.components.envelope.door import DoorListManager
from src.constants.envelope_constants import DEFAULT_DOOR


def test_initialization_with_provided_data():
    """Test initialization with provided data."""
    manager = DoorListManager([DEFAULT_DOOR])
    assert manager.get_all() == [DEFAULT_DOOR]
