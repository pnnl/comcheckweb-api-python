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
from comcheck_api.types.core_types import Roof, ThermalBridgeTypeOptions

# Initialize client
load_dotenv()
api_key = os.getenv("COM_API_KEY")
if not api_key:
    raise ValueError("COM_API_KEY environment variable is not set")

client = COMcheckClient()
client.set_api_key(api_key)

# Get a project to work with
project = client.get_project("your-project-id")
if not project:
    raise ValueError("Project not found")

if not project.lighting or not project.lighting.wholeBldgUse:
    raise ValueError("Project has no wholeBldgUse")
building_area_key = str(project.lighting.wholeBldgUse[0].key)

# Example 1: Add a roof
new_roof = get_default_roof_template()
updated_project = project_envelope_operations.add_roof_to_project(
    project, building_area_key, new_roof
)
project_id = str(updated_project.id)
client.update_project(project_id, updated_project)

# Example 2: Add an above-grade wall
new_ag_wall = get_default_ag_wall_template()
updated_project = project_envelope_operations.add_ag_wall_to_project(
    project, building_area_key, new_ag_wall
)
client.update_project(project_id, updated_project)

# Example 3: Add a window to a wall
new_window = get_default_window_template()
if not project.envelope or not project.envelope.agWall:
    raise ValueError("Project has no agWall")
ag_wall = project.envelope.agWall[0]
updated_project = project_envelope_operations.add_window_to_project(
    project, building_area_key, new_window, ag_wall
)
client.update_project(project_id, updated_project)

# Example 4: Add a thermal bridge
updated_project = project_envelope_operations.add_thermal_bridge_to_project(
    project,
    building_area_key,
    ag_wall,
    thermal_bridge_type=ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER,
)
client.update_project(project_id, updated_project)
