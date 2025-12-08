"""Script to test Roof manager."""

import os
import sys
from uuid import uuid4

# Add compcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from comcheck_api.components.envelope.roof import RoofListManager
from comcheck_api.types.core_types import Roof, Skylight

# Example usage
manager = RoofListManager([])
sample_roof = Roof(
    bldgUseKey=str(uuid4()),
    adjacentSpaceType=None,
    altExemptType=None,
    assemblyType="Roof:Roof",
    cavityRValue=0,
    continuousRValue=37,
    description="",
    grossArea=6000,
    orientation="UNSPECIFIED_ORIENTATION",
    otherRoofType=None,
    propUValue=0.026,
    purlinSpacing=0,
    roofType="ABOVE_DECK_ROOF",
    allowanceType=None,
    exemptionType=None,
    highAlbedoRoofReqType="HA_ROOF_EXEMPTION_VEGETATED",
    roofInsulType=None,
    solarReflectance=0,
    solarReflectanceIndex=0,
    thermalEmittance=0,
    constructionType=None,
    skylight=[],
)

manager.add_new(sample_roof)
print("before adding skylight:", manager.get_all())

sample_skylight = Skylight(
    bldgUseKey=sample_roof.bldgUseKey,
    adjacentSpaceType=None,
    altExemptType=None,
    assemblyType="Skylight:Skylight",
    curbType="NO_CURB_SKYLIGHT",
    description="",
    frameType="METAL",
    glazingType="DOUBLE_PANE_LOWE",
    grossArea=100,
    orientation="UNSPECIFIED_ORIENTATION",
    preAltPropShgc=0,
    productType=None,
    propProjectionFactor=0,
    propShgc=0.6,
    propUValue=0.55,
    solarType="TINTED",
    propVt=0,
    allowanceType=None,
    exemptionType=None,
    constructionType=None,
    glazingMaterialType="GLASS_GLAZING_MAT",
    perfDataType="PERF_TYPE_DEFAULT",
    productId=None,
    isSiteShading=None,
)

manager.add_new_skylight(sample_roof, sample_skylight)

print("after adding skylight:", manager.get_all())
