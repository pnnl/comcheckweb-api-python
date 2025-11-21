"""Tests for DoorListManager."""

from comcheck_api.components.envelope.door import DoorListManager
from comcheck_api.constants.envelope_constants import DEFAULT_DOOR


def test_initialization_with_provided_data():
    """Test initialization with provided data."""
    manager = DoorListManager([DEFAULT_DOOR])
    assert manager.get_all() == [DEFAULT_DOOR]
