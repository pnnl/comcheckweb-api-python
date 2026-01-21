"""Examples of using envelope operations with the COMcheck API."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.project_operations import project_envelope_operations
from comcheck_api.utilities.get_project_default import (
    get_default_roof_template,
    get_default_ag_wall_template,
    get_default_window_template,
)
from comcheck_api.types.core_types import ThermalBridgeTypeOptions

# Initialize client
load_dotenv()
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY"))

# Get a project to work with
project = client.get_project("your-project-id")
building_area_key = project.lighting.wholeBldgUse[0].key

# Example 1: Add a roof
new_roof = get_default_roof_template()
updated_project = project_envelope_operations.add_roof_to_project(
    project, building_area_key, new_roof
)
client.update_project(updated_project.id, updated_project)

# Example 2: Add an above-grade wall
new_ag_wall = get_default_ag_wall_template()
updated_project = project_envelope_operations.add_ag_wall_to_project(
    project, building_area_key, new_ag_wall
)
client.update_project(updated_project.id, updated_project)

# Example 3: Add a window to a wall
new_window = get_default_window_template()
ag_wall = project.envelope.agWall[0]
updated_project = project_envelope_operations.add_window_to_project(
    project, building_area_key, new_window, ag_wall
)
client.update_project(updated_project.id, updated_project)

# Example 4: Add a thermal bridge
updated_project = project_envelope_operations.add_thermal_bridge_to_project(
    project,
    building_area_key,
    ag_wall,
    thermal_bridge_type=ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER,
)
client.update_project(updated_project.id, updated_project)
