"""Script to test Floor manager."""

import os
import sys
from uuid import uuid4

# Add comcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from comcheck_api.components.envelope.floor import FloorListManager
from comcheck_api.types.core_types import Floor

# Example usage
manager = FloorListManager([])
sample_floor = Floor(
    bldgUseKey=str(uuid4()),
    orientation="UNSPECIFIED_ORIENTATION",
    description="Floor:Floor",
    assemblyType="Floor:Floor",
    altExemptType=None,
    allowanceType=None,
    exemptionType=None,
    constructionType=None,
    adjacentSpaceType=None,
    hasEdgeInsul=None,
    insulationPosition="VERTICAL",
    floorType="HEATED_SLAB_ON_GRADE",
    floorExposedFrameType=None,
    grossArea=320,
    depthOfInsulation=4,
    cavityRValue=0,
    continuousRValue=15,
    propUValue=0.72,
)

manager.add_new(sample_floor)

print(manager.get_all())
