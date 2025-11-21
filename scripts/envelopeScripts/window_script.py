"""Script to test Window manager."""

import os
import sys
from uuid import uuid4

# Add compcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from comcheck_api.components.envelope.window import WindowListManager
from comcheck_api.types.core_types import Window

# Example usage
manager = WindowListManager([])
sample_window = Window(
    id=1,
    bldgUseKey=str(uuid4()),
    description="Double-pane Low-E Window",
    assemblyType="WINDOW",
    adjacentSpaceType="ADJACENT_SPACE_EXTERIOR",
    adjacentSpaceBuildingType="WHOLE_BUILDING_OFFICE",
    propUValue=0.35,
    grossArea=48,
    altExemptType=None,
    propShgc=0.25,
    propProjectionFactor=0.5,
    frameType="METAL_W_THERMAL_BREAK",
    glazingType="DOUBLE_PANE_LOWE",
    propVt=0.65,
    preAltPropShgc=0.25,
    solarType="CLEAR",
    orientation="NORTH",
    glazingMaterialType="GLASS_GLAZING_MAT",
    productType="FACTORY_ASSEMBLED_WINDOW",
    allowanceType="ENV_ALLOWANCE_NONE",
    exemptionType="ENV_EXEMPTION_NONE",
    constructionType="NON_RESIDENTIAL",
    isSiteShading=False,
    perfDataType="PERF_TYPE_NFRC",
    productId="WIN-001",
    preAltPropUval=0.35,
    windowOpenType="NON_OPERABLE_WINDOW",
)

manager.add_new(sample_window)

print(manager.get_all())
