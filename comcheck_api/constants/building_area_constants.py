"""Building area constants for COMcheck projects."""

from uuid import uuid4

from comcheck_api.types.core_types import WholeBldgUse

# Default building area structure with interior lighting space
DEFAULT_BUILDING_AREA: WholeBldgUse = {
    "key": str(uuid4()),
    "wholeBldgType": "WHOLE_BUILDING_AUTOMOTIVE",  # TODO: wholeBldgType is a list of enum, need to define the enum type
    "areaDescription": "Automotive Facility",
    "constructionType": "NON_RESIDENTIAL",
    "floorArea": 1000,
    "internalLoad": 0,
    "powerDensity": 0.71,  # TODO: power density is automatically calculated based on wholeBldgType
    "isTenantSpace": False,  # TODO: space conditioning is a list of enum, need to define the enum type
    "activityUse": [],
    "interiorLightingSpace": {
        "altExemptType": "EXEMPT_NOT_SET",
        "description": "",
        "numFixturesAlteredOrAdded": 0,
        "postAltTotalWattage": 0,
        "preAltNumberFixtures": 0,
        "preAltTotalWattage": 0,
        "allowanceType": None,
        "exemptionType": None,
        "allowanceFloorArea": 0,
        "rcrFloorToWorkplaneHeight": 0,
        "rcrPerimeter": 0,
        "rcrWorkplaneToLuminaireHeight": 0,
        "fixture": [],
    },  # redundant data, but need it for backend call
}
