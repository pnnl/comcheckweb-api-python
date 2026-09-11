"""Example of using COMcheck API client interior lighting allowed-wattage calculation."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.defaults import get_default_interior_space_template
from comcheck_api.types.core_types import ActivityTypeOptions, EnergyCodeOptions

# Initialize client
load_dotenv(override=True)
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

energy_code = str(EnergyCodeOptions.CEZ_90_1_2022)

# Example 1: Calculate allowed wattage for a single InteriorSpace.
interior_space = get_default_interior_space_template()
interior_space.areaDescription = "Open Office"
interior_space.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
interior_space.floorArea = 2000.0

result = client.calculate_interior_space_allowed_wattage(interior_space, energy_code)
print(f"Allowed wattage: {result}")  # e.g. {"spaceAllowedWattage": 560}

# Example 2: Calculate allowed wattage for a list of InteriorSpace objects.
second_interior_space = get_default_interior_space_template()
second_interior_space.areaDescription = "Conference Room"
second_interior_space.activityType = ActivityTypeOptions.ACTIVITY_COMMON_CONFERENCE_HALL
second_interior_space.floorArea = 500.0

results = client.calculate_interior_spaces_allowed_wattage(
    [interior_space, second_interior_space], energy_code
)
print(
    f"Allowed wattages: {results}"
)  # e.g. {"Open Office": 560, "Conference Room": 610}
