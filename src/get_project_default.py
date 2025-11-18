"""Module for project default templates/values."""

from uuid import uuid4

from src.constants.building_area_constants import DEFAULT_BUILDING_AREA
from src.constants.envelope_constants import (
    DEFAULT_AG_WALL,
    DEFAULT_BG_WALL,
    DEFAULT_DOOR,
    DEFAULT_FLOOR,
    DEFAULT_ROOF,
    DEFAULT_SKYLIGHT,
    DEFAULT_THERMAL_BRIDGE,
    DEFAULT_WINDOW,
)

# TODO: Import these when the modules are created
# from src.constants import DUMMY_PROJECT
# from src.constants.lighting_constants import DEFAULT_FIXTURE_SCHEDULE


def get_default_project_template():
    """Get project defaults."""
    # TODO: Implement when DUMMY_PROJECT constant is available
    # return DUMMY_PROJECT
    raise NotImplementedError("DUMMY_PROJECT constant not yet implemented")


def get_default_building_area_template():
    """Get building area defaults."""
    return DEFAULT_BUILDING_AREA


def get_default_roof_template():
    """Get default roof template."""
    return DEFAULT_ROOF


def get_default_ag_wall_template():
    """Get default above-grade wall template."""
    return DEFAULT_AG_WALL


def get_default_floor_template():
    """Get default floor template."""
    return DEFAULT_FLOOR


def get_default_bg_wall_template():
    """Get default below-grade wall template."""
    return DEFAULT_BG_WALL


def get_default_skylight_template():
    """Get default skylight template."""
    return DEFAULT_SKYLIGHT


def get_default_window_template():
    """Get default window template."""
    return DEFAULT_WINDOW


def get_default_door_template():
    """Get default door template."""
    return DEFAULT_DOOR


def get_default_thermal_bridge_template():
    """Get default thermal bridge template."""
    return DEFAULT_THERMAL_BRIDGE


def get_default_fixture_schedule_template():
    """Get default fixture schedule template with unique key."""
    # TODO: Implement when DEFAULT_FIXTURE_SCHEDULE constant is available
    # return {**DEFAULT_FIXTURE_SCHEDULE, "scheduleFixtureKey": str(uuid4())}
    raise NotImplementedError("DEFAULT_FIXTURE_SCHEDULE constant not yet implemented")
