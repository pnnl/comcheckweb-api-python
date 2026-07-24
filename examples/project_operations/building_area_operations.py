"""Examples of using building area operations with the COMcheck API."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.defaults import get_default_building_area_template
from comcheck_api.types.core_types import WholeBuildingTypeOptions
from comcheck_api.utilities.common import export_to_json

# Initialize client
load_dotenv()
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Get a project to work with
project = client.get_project("your-project-id")
if not project:
    raise ValueError("Project not found")

# Example 1: Add a building area
new_building_area = get_default_building_area_template()
new_building_area.areaDescription = "New Building Area 2"
updated_project = project_building_area_operations.add_building_area_to_project(
    project, new_building_area
)
# # export the updated project to JSON for inspection
export_to_json(updated_project, "updated_project_with_new_building_area.json")
project = client.update_project(str(updated_project.id), updated_project)

# Example 2: Update a building area
if not project:
    raise ValueError("Project not found after update")
else:
    if not project.lighting or not project.lighting.wholeBldgUse:
        raise ValueError("Project has no building areas (wholeBldgUse)")
    building_area_key = str(project.lighting.wholeBldgUse[0].key)
    updates = {
        "wholeBldgType": WholeBuildingTypeOptions.WHOLE_BUILDING_COURT_HOUSE,
        "areaDescription": "Updated description 2",
        "floorArea": 2500,
    }
    updated_project = project_building_area_operations.update_building_area_in_project(
        project, building_area_key, updates
    )
    client.update_project(str(updated_project.id), updated_project)
