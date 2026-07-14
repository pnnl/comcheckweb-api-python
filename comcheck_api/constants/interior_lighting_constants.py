"""Interior lighting constants for COMcheck projects."""

from comcheck_api.types.core_types import (
    ActivityUse,
    ActivityTypeOptions,
    Fixture,
    InteriorLightingSpace,
    LightingTypeOptions,
)

# key is a placeholder — callers must set it to the parent WholeBldgUse.key
DEFAULT_INTERIOR_LIGHTING_SPACE_AREA: ActivityUse = ActivityUse(
    key="__unset__",
    areaDescription="Space 1",
    activityType=ActivityTypeOptions.ACTIVITY_COMMON_OFFICE,
    floorArea=1000.0,
    ceilingHeight=9.0,
    interiorLightingSpace=InteriorLightingSpace(
        altExemptType=None,
        description="",
        numFixturesAlteredOrAdded=0,
        postAltTotalWattage=0.0,
        preAltNumberFixtures=0,
        preAltTotalWattage=0.0,
        allowanceType=None,
        exemptionType=None,
        allowanceFloorArea=0.0,
        rcrFloorToWorkplaneHeight=0.0,
        rcrPerimeter=0.0,
        rcrWorkplaneToLuminaireHeight=0.0,
        fixture=[],
    ),
)

DEFAULT_FIXTURE: Fixture = Fixture(
    description="LED fixture",
    lightingType=LightingTypeOptions.LED,
    fixtureWattage=32.0,
    quantity=1,
    lightingControl=[],
)
