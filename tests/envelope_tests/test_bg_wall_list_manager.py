"""Tests for BgWallListManager."""

import pytest

from src.components.envelope.bg_wall import BgWallListManager
from src.constants.envelope_constants import (
    DEFAULT_BG_WALL,
    DEFAULT_DOOR,
    DEFAULT_WINDOW,
)


def test_initialization_with_provided_data():
    """Test initialization with provided data."""
    manager = BgWallListManager([DEFAULT_BG_WALL])
    assert manager.get_all() == [DEFAULT_BG_WALL]


def test_add_door_to_bg_wall():
    """Test adding a door to bg wall."""
    manager = BgWallListManager([DEFAULT_BG_WALL])
    manager.add_new_door(DEFAULT_BG_WALL, DEFAULT_DOOR)
    updated_wall = manager.get_by_identifier(DEFAULT_BG_WALL["assemblyType"])
    assert updated_wall is not None
    assert len(updated_wall["door"]) == 1


def test_add_window_to_bg_wall():
    """Test adding a window to bg wall."""
    manager = BgWallListManager([DEFAULT_BG_WALL])
    manager.add_new_window(DEFAULT_BG_WALL, DEFAULT_WINDOW)
    updated_wall = manager.get_by_identifier(DEFAULT_BG_WALL["assemblyType"])
    assert updated_wall is not None
    assert len(updated_wall["window"]) == 1


def test_add_duplicate_bg_wall_raises_error():
    """Test that adding a duplicate bg wall raises an error."""
    manager = BgWallListManager([DEFAULT_BG_WALL])
    with pytest.raises(
        ValueError,
        match=f"Item with assemblyType '{DEFAULT_BG_WALL['assemblyType']}' already exists",
    ):
        manager.add_new(DEFAULT_BG_WALL)
