"""Exterior lighting constants for COMcheck projects."""

from comcheck_api.types.core_types import (
    ExteriorLightingSpace,
    ExteriorUse,
    ExteriorUseTypeOptions,
)

DEFAULT_EXTERIOR_LIGHTING_AREA: ExteriorUse = ExteriorUse(
    areaDescription="Ext Area 1",
    exteriorType=ExteriorUseTypeOptions.EXTERIOR_PARKING_AREA,
    isTradable=True,
    powerDensity=0.0,
    quantityUnits="sq ft",
    useQuantity=1000.0,
    exteriorLightingSpace=ExteriorLightingSpace(
        description="",
        numFixturesAlteredOrAdded=0,
        postAltTotalWattage=0.0,
        preAltNumberFixtures=0,
        preAltTotalWattage=0.0,
        altExemptType=None,
        fixture=[],
    ),
)
