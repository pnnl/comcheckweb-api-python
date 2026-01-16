"""Example of using the BuildingAreaListManager."""

from comcheck_api.managers.components.building_area import BuildingAreaListManager
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.types.core_types import WholeBuildingTypeOptions

# Create a manager instance
manager = BuildingAreaListManager([])

# Add a default building area
building_area = manager.add_new(DEFAULT_BUILDING_AREA)
print("Added default building area:", building_area)

# Update building area properties
building_area[0].wholeBldgType = WholeBuildingTypeOptions.WHOLE_BUILDING_COURT_HOUSE
building_area[0].areaDescription = "Example Building Area"
building_area[0].floorArea = 2500

print("\nUpdated building area:", manager.get_all())
