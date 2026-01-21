"""Example of using COMcheck API client simulation functions."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.constants.common_constants import PROJECT_TEMPLATE
from comcheck_api.types.core_types import EnergyCodeOptions

# Initialize client
load_dotenv()
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY"))

# Example 1: Run a simulation without saving to a project
project = PROJECT_TEMPLATE.model_copy(deep=True)
project.control.code = EnergyCodeOptions.CEZ_90_1_2022
session_id = client.start_run_simulation(project)
print(f"Started simulation: {session_id}")

# Example 2: Check simulation status
status = client.get_simulation_status(session_id)
print(f"Simulation status: {status}")

# Example 3: Get simulation results
results = client.get_simulation_result(session_id)
print(f"Simulation results: {results}")

# Example 4: Run simulation for an existing project
project_id = "your-project-id"  # Replace with actual project ID
session_id = client.start_run_simulation(project, project_id)
print(f"Started simulation for project {project_id}: {session_id}")
