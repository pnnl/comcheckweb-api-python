"""Tests for BgWallListManager."""
from copy import deepcopy

from comcheck_api.managers.components.envelope.bg_wall import BgWallListManager
from comcheck_api.types.core_types import *

def test_initialization_with_provided_data(bg_wall: BgWall):
    """Test initialization with provided data."""
    manager = BgWallListManager([bg_wall])
    assert manager.get_all() == [bg_wall]


def test_add_door_to_bg_wall(bg_wall: BgWall, door: Door):
    """Test adding a door to bg wall."""
    manager = BgWallListManager([bg_wall]) 

    manager.add_new_door(bg_wall, door)
    updated_wall = manager.get_by_identifier(bg_wall.assemblyType)
        

    assert updated_wall is not None
    assert len(updated_wall.door) == 1


def test_add_window_to_bg_wall(bg_wall: BgWall, window: Window):
    """Test adding a window to bg wall."""
    manager = BgWallListManager([bg_wall])
    manager.add_new_window(bg_wall, window)
    updated_wall = manager.get_by_identifier(bg_wall.assemblyType)
    assert updated_wall is not None
    assert len(updated_wall.window) == 1


def test_add_duplicate_bg_wall_has_unique_assembly_type(bg_wall: BgWall):
    """Test that adding a duplicate bg wall raises an error."""
    manager = BgWallListManager([bg_wall])
    manager.add_new(deepcopy(bg_wall))
    
    bg_walls = manager.get_all()

    assembly_types = [wall.assemblyType for wall in bg_walls]
    assert len(assembly_types) == 2
    assert len(assembly_types) == len(set(assembly_types))
