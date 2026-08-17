"""Example of using COMcheck API client interior lighting allowed-wattage calculation."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.defaults import get_default_interior_lighting_space_template
from comcheck_api.types.core_types import ActivityTypeOptions, EnergyCodeOptions

# Initialize client
load_dotenv(override=True)
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

energy_code = str(EnergyCodeOptions.CEZ_90_1_2022)

# Example 1: Calculate allowed wattage for a single ActivityUse.
activity_use = get_default_interior_lighting_space_template()
activity_use.areaDescription = "Open Office"
activity_use.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
activity_use.floorArea = 2000.0

result = client.calculate_activity_use_allowed_wattage(activity_use, energy_code)
print(f"Allowed wattage: {result}")  # e.g. {"spaceAllowedWattage": 560}

# Example 2: Calculate allowed wattage for a list of ActivityUse objects.
second_activity_use = get_default_interior_lighting_space_template()
second_activity_use.areaDescription = "Conference Room"
second_activity_use.activityType = ActivityTypeOptions.ACTIVITY_COMMON_CONFERENCE_HALL
second_activity_use.floorArea = 500.0

results = client.calculate_activity_uses_allowed_wattage(
    [activity_use, second_activity_use], energy_code
)
print(
    f"Allowed wattages: {results}"
)  # e.g. {"Open Office": 560, "Conference Room": 610}
