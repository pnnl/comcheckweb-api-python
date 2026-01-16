"""Examples of using building area operations with the COMcheck API."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.utilities.get_project_default import get_default_building_area_template
from comcheck_api.types.core_types import WholeBuildingTypeOptions

# Initialize client
load_dotenv()
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY"))

# Get a project to work with
project = client.get_project("your-project-id")

# Example 1: Add a building area
new_building_area = get_default_building_area_template()
updated_project = project_building_area_operations.add_building_area_to_project(
    project, new_building_area
)
client.update_project(updated_project.id, updated_project)

# Example 2: Update a building area
building_area_key = project.lighting.wholeBldgUse[0].key
updates = {
    "wholeBldgType": WholeBuildingTypeOptions.WHOLE_BUILDING_COURT_HOUSE,
    "areaDescription": "Updated description",
    "floorArea": 2500,
}
updated_project = project_building_area_operations.update_building_area_in_project(
    project, building_area_key, updates
)
client.update_project(updated_project.id, updated_project)
