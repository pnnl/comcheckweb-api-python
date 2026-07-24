"""Module for project default templates/values."""

import copy
from uuid import uuid4

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
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.ComBuilding` template.

    The template is pre-populated with sensible defaults for location
    (Boulder, CO), envelope, lighting, HVAC, and other required sections.

    Returns:
        A new ``ComBuilding`` instance ready to be customized.
    """
    return copy.deepcopy(PROJECT_TEMPLATE)


def get_default_building_area_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.WholeBldgUse` template.

    Defaults to an *Automotive Facility* with 1 000 sq ft floor area
    and interior lighting space initialized.  Each call gets a fresh unique
    ``key`` so multiple areas can be added to a project without colliding.

    Returns:
        A new ``WholeBldgUse`` instance.
    """
    area = copy.deepcopy(DEFAULT_BUILDING_AREA)
    area.key = str(uuid4())
    return area


def get_default_roof_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.Roof` template.

    Defaults to an above-deck roof with 6 000 sq ft gross area and
    R-37 continuous insulation.

    Returns:
        A new ``Roof`` instance.
    """
    return copy.deepcopy(DEFAULT_ROOF)


def get_default_ag_wall_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.AgWall` template.

    Defaults to a metal-frame 24-inch above-grade wall with 4 800 sq ft
    gross area, R-20 cavity / R-10 continuous insulation.

    Returns:
        A new ``AgWall`` instance.
    """
    return copy.deepcopy(DEFAULT_AG_WALL)


def get_default_floor_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.Floor` template.

    Defaults to a heated slab-on-grade floor with 320 sq ft gross area
    and R-15 continuous insulation.

    Returns:
        A new ``Floor`` instance.
    """
    return copy.deepcopy(DEFAULT_FLOOR)


def get_default_bg_wall_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.BgWall` template.

    Defaults to a concrete below-grade wall with 3 000 sq ft gross area,
    R-20 cavity / R-10 continuous insulation, and wood furring.

    Returns:
        A new ``BgWall`` instance.
    """
    return copy.deepcopy(DEFAULT_BG_WALL)


def get_default_skylight_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.Skylight` template.

    Defaults to a no-curb, double-pane low-E skylight with 100 sq ft
    gross area.

    Returns:
        A new ``Skylight`` instance.
    """
    return copy.deepcopy(DEFAULT_SKYLIGHT)


def get_default_window_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.Window` template.

    Defaults to a triple-pane, non-operable, metal-frame window with
    300 sq ft gross area and NFRC performance data.

    Returns:
        A new ``Window`` instance.
    """
    return copy.deepcopy(DEFAULT_WINDOW)


def get_default_door_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.Door` template.

    Defaults to a swinging, insulated metal entrance door with 23 sq ft
    gross area.

    Returns:
        A new ``Door`` instance.
    """
    return copy.deepcopy(DEFAULT_DOOR)


def get_default_thermal_bridge_template():
    """Return a deep copy of the default :class:`~comcheck_api.types.core_types.ThermalBridge` template.

    Defaults to a prescriptive linear floor-to-wall intersection thermal
    bridge with a psi factor of 0.177 and 100 ft length.

    Returns:
        A new ``ThermalBridge`` instance.
    """
    return copy.deepcopy(DEFAULT_THERMAL_BRIDGE)


def get_default_fixture_schedule_template():
    """Return a default fixture schedule template with a unique key.

    .. warning::
        Not yet implemented — raises :exc:`NotImplementedError`.
    """
    # TODO: Implement when DEFAULT_FIXTURE_SCHEDULE constant is available
    # return {**DEFAULT_FIXTURE_SCHEDULE, "scheduleFixtureKey": str(uuid4())}
    raise NotImplementedError("DEFAULT_FIXTURE_SCHEDULE constant not yet implemented")
