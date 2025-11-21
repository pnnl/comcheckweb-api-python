"""Script to test AgWall manager."""

import os
import sys

# Add compcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from comcheck_api.components.envelope.ag_wall import AgWallListManager
from comcheck_api.types.core_types import AgWall

manager = AgWallListManager([])

ag_wall_list = manager.add_new(
    AgWall(
        description="Test Wall",
        thermalBridge=[],
        thermalBridgeExceptionType="THERMAL_BRIDGE_EXCEPTION_NONE",
        bldgUseKey="1234",
        wallType="WOOD_FRAME_16_AG_WALL",
        agWallConstructionDetailsType="AG_WALL_METAL_BLDG_SINGLE_LAYER_MINERAL_FIBER",
        agWallExteriorFinishDetailsType=None,
        insulationPosition=None,
        otherWallType="NONE",
        adjacentSpaceType="ADJACENT_SPACE_UNCONDITIONED",
        effectiveUFactor=0.0,
        allowanceType=None,
        cmuType=None,
        concreteDensity=0,
        concreteThickness=0,
        exemptionType=None,
        furringType=None,
        heatCapacity=0,
        orientation="NORTH",
        window=[],
        door=[],
        cavityRValue=0,
        continuousRValue=0,
        propUValue=0,
        grossArea=0,
    )
)

print("Initial agWall list:", ag_wall_list)

manager.add_new_thermal_bridge(ag_wall_list[0])

print("Updated agWall:", ag_wall_list)
print("Updated thermal bridge:", ag_wall_list[0]["thermalBridge"])
