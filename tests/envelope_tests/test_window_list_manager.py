"""Tests for WindowListManager."""

from src.components.envelope.window import WindowListManager
from src.constants.envelope_constants import DEFAULT_WINDOW


class TestWindowListManager:
    """Test suite for WindowListManager."""

    def test_initialization_with_provided_data(self):
        """Should initialize with provided data."""
        manager = WindowListManager([DEFAULT_WINDOW])
        assert manager.get_all() == [DEFAULT_WINDOW]

    # TODO: Determine window uniqueness, assemblyType instead of id?
    # def test_add_new_window(self):
    #     """Should add a new window."""
    #     manager = WindowListManager([])
    #     new_window = {**DEFAULT_WINDOW, "id": 2}
    #     manager.add_new(new_window)
    #     assert manager.get_by_id(2) == new_window
