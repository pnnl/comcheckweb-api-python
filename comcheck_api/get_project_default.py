"""Module for project default templates/values."""

import copy

from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.constants.envelope_constants import (
    DEFAULT_AG_WALL,
    DEFAULT_BG_WALL,
    DEFAULT_DOOR,
    DEFAULT_FLOOR,
    DEFAULT_ROOF,
    DEFAULT_SKYLIGHT,
    DEFAULT_THERMAL_BRIDGE,
    DEFAULT_WINDOW,
)

from comcheck_api.constants.common_constants import PROJECT_TEMPLATE

# from comcheck_api.constants.lighting_constants import DEFAULT_FIXTURE_SCHEDULE


def get_default_project_template():
    """Get project defaults."""
    return copy.deepcopy(PROJECT_TEMPLATE)


def get_default_building_area_template():
    """Get building area defaults."""
    return copy.deepcopy(DEFAULT_BUILDING_AREA)


def get_default_roof_template():
    """Get default roof template."""
    return copy.deepcopy(DEFAULT_ROOF)


def get_default_ag_wall_template():
    """Get default above-grade wall template."""
    return copy.deepcopy(DEFAULT_AG_WALL)


def get_default_floor_template():
    """Get default floor template."""
    return copy.deepcopy(DEFAULT_FLOOR)


def get_default_bg_wall_template():
    """Get default below-grade wall template."""
    return copy.deepcopy(DEFAULT_BG_WALL)


def get_default_skylight_template():
    """Get default skylight template."""
    return copy.deepcopy(DEFAULT_SKYLIGHT)


def get_default_window_template():
    """Get default window template."""
    return copy.deepcopy(DEFAULT_WINDOW)


def get_default_door_template():
    """Get default door template."""
    return copy.deepcopy(DEFAULT_DOOR)


def get_default_thermal_bridge_template():
    """Get default thermal bridge template."""
    return copy.deepcopy(DEFAULT_THERMAL_BRIDGE)


def get_default_fixture_schedule_template():
    """Get default fixture schedule template with unique key."""
    # TODO: Implement when DEFAULT_FIXTURE_SCHEDULE constant is available
    # return {**DEFAULT_FIXTURE_SCHEDULE, "scheduleFixtureKey": str(uuid4())}
    raise NotImplementedError("DEFAULT_FIXTURE_SCHEDULE constant not yet implemented")
