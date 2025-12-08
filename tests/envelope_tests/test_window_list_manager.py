"""Tests for WindowListManager."""

from comcheck_api.components.envelope.window import WindowListManager

class TestWindowListManager:
    """Test suite for WindowListManager."""

    def test_initialization_with_provided_data(self, window):
        """Should initialize with provided data."""
        manager = WindowListManager([window])
        assert manager.get_all() == [window]

    # TODO: Determine window uniqueness, assemblyType instead of id?
    # def test_add_new_window(self):
    #     """Should add a new window."""
    #     manager = WindowListManager([])
    #     new_window = {**DEFAULT_WINDOW, "id": 2}
    #     manager.add_new(new_window)
    #     assert manager.get_by_id(2) == new_window