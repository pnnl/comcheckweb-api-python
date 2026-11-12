"""Example of using COMcheck API client interior lighting allowed-wattage calculation.

Both allowed-wattage calls send the whole project, so the interior spaces
must be added to the project first. The energy code defaults to
``project.control.code``.
"""

import os
from dotenv import load_dotenv
from comcheck_api import (
    project_building_area_operations as ba_ops,
    project_interior_lighting_operations as il_ops,
)
from comcheck_api.client import COMcheckClient
from comcheck_api.defaults import (
    get_default_building_area_template,
    get_default_interior_space_template,
    get_default_project_template,
)
from comcheck_api.types.core_types import ActivityTypeOptions, EnergyCodeOptions

# Initialize client
load_dotenv(override=True)
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Build a project with one building area and two interior spaces.
project = get_default_project_template()
project.control.code = EnergyCodeOptions.CEZ_90_1_2022

area = get_default_building_area_template()
area.areaDescription = "Office Area"
project = ba_ops.add_building_area_to_project(project, area)

interior_space = get_default_interior_space_template()
interior_space.areaDescription = "Open Office"
interior_space.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
interior_space.floorArea = 2000.0
project = il_ops.add_interior_space_to_project(project, area.key, interior_space)

second_interior_space = get_default_interior_space_template()
second_interior_space.areaDescription = "Conference Room"
second_interior_space.activityType = ActivityTypeOptions.ACTIVITY_COMMON_CONFERENCE_HALL
second_interior_space.floorArea = 500.0
project = il_ops.add_interior_space_to_project(project, area.key, second_interior_space)

# Example 1: Calculate allowed wattage for one InteriorSpace, selected by areaDescription.
result = client.calculate_interior_space_allowed_wattage(project, "Open Office")
print(f"Allowed wattage: {result}")  # e.g. {"spaceAllowedWattage": 560}

# Example 2: Calculate allowed wattage for every InteriorSpace in the project.
results = client.calculate_interior_spaces_allowed_wattage(project)
print(
    f"Allowed wattages: {results}"
)  # e.g. {"Open Office": 560, "Conference Room": 610}
