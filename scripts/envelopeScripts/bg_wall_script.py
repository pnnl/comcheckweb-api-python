"""Script to test BgWall manager."""

import os
import sys

# Add compcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from comcheck_api.components.envelope.bg_wall import BgWallListManager
from comcheck_api.types.core_types import BgWall, Door, Window

manager = BgWallListManager([])

bg_wall_list = manager.add_new(
    BgWall(
        id="999999",
        description="Test Below-Grade Wall",
        assemblyType="SOLID_CONCRETE_LE_8IN_BG_WALL",
        bldgUseKey="5678",
        wallHeight=10,
        wallHeightBelowGrade=8,
        adjacentSpaceType="ADJACENT_SPACE_UNCONDITIONED",
        allowanceType=None,
        cmuType=None,
        concreteDensity=115,
        concreteThickness=8,
        constructionType=None,
        exemptionType=None,
        furringType=None,
        heatCapacity=0,
        orientation="NORTH",
        insulationPosition=None,
        window=[],
        door=[],
        cavityRValue=0,
        continuousRValue=0,
        propUValue=0,
        grossArea=0,
    )
)

print("Initial bgWall list:", bg_wall_list)

manager.add_new_door(
    bg_wall_list[0],
    Door(
        id="door-1",
        description="Test Door",
        assemblyType="DOOR_SOLID_CORE",
        bldgUseKey="5678",
        grossArea=10,
        propUValue=0.5,
        adjacentSpaceType=None,
        altExemptType=None,
        cavityRValue=0,
        continuousRValue=0,
        doorEntranceType=None,
        doorOpenType=None,
        doorType=None,
        frameType=None,
        glazingType=None,
        orientation="UNSPECIFIED_ORIENTATION",
        preAltPropShgc=0,
        preAltPropUval=0,
        productType=None,
        propProjectionFactor=0,
        propShgc=0,
        solarType=None,
        propVt=None,
        allowanceType=None,
        exemptionType=None,
        constructionType=None,
        glazingMaterialType=None,
        perfDataType=None,
        productId=None,
        isSiteShading=None,
    ),
)

print("After adding door:", bg_wall_list[0])
print("Door list:", bg_wall_list[0]["door"])

manager.add_new_window(
    bg_wall_list[0],
    Window(
        id="window-1",
        description="Test Window",
        assemblyType="WINDOW_DOUBLE_PANE",
        bldgUseKey="5678",
        grossArea=12,
        propUValue=0.35,
        adjacentSpaceType=None,
        adjacentSpaceBuildingType=None,
        altExemptType=None,
        propShgc=0,
        propProjectionFactor=0,
        frameType=None,
        glazingType=None,
        propVt=0,
        preAltPropShgc=0,
        solarType=None,
        orientation="UNSPECIFIED_ORIENTATION",
        glazingMaterialType=None,
        productType=None,
        allowanceType=None,
        exemptionType=None,
        constructionType=None,
        isSiteShading=False,
        perfDataType=None,
        productId=None,
        preAltPropUval=0,
        windowOpenType=None,
    ),
)

print("After adding window:", bg_wall_list[0])
print("Window list:", bg_wall_list[0]["window"])
