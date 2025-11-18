"""Tests for FloorListManager."""

from src.components.envelope.floor import FloorListManager
from src.constants.envelope_constants import DEFAULT_FLOOR


def test_initialization_with_provided_data():
    """Test initialization with provided data."""
    manager = FloorListManager([DEFAULT_FLOOR])
    assert manager.get_all() == [DEFAULT_FLOOR]
