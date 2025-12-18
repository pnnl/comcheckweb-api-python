"""Script to test Door manager."""

import os
import sys
from uuid import uuid4

# Add comcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from comcheck_api.components.envelope.door import DoorListManager
from comcheck_api.types.core_types import Door

# Example usage
manager = DoorListManager([])
sample_door = Door(
    bldgUseKey=str(uuid4()),
    adjacentSpaceType=None,
    altExemptType=None,
    assemblyType="Door:Door",
    cavityRValue=0,
    continuousRValue=0,
    description="",
    doorEntranceType=None,
    doorOpenType=None,
    doorType="NO_INSUL_SINGLE_METAL_DOOR",
    frameType=None,
    glazingType=None,
    grossArea=15,
    orientation="UNSPECIFIED_ORIENTATION",
    preAltPropShgc=0,
    preAltPropUval=0,
    productType=None,
    propProjectionFactor=0,
    propShgc=0,
    propUValue=0.35,
    solarType=None,
    propVt=None,
    allowanceType=None,
    exemptionType=None,
    constructionType=None,
    glazingMaterialType=None,
    perfDataType=None,
    productId=None,
    isSiteShading=None,
)

manager.add_new(sample_door)

print(manager.get_all())
