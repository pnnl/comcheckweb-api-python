"""Tests for COMcheckClient simulation functions: run_simulation, get_simulation_status, get_simulation_result."""

import copy
import os
import sys

from tools.scripts.script_test_data import TEST_BUILDING_AREA, TEST_PROJECT_ENVELOPE

# Add comcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.constants.common_constants import PROJECT_TEMPLATE
from comcheck_api.types.core_types import EnergyCodeOptions

load_dotenv()

# AWS API Gateway API keys are used for tracking and controlling API usage by clients.
api_key = os.getenv("COM_API_KEY")
if not api_key:
    print("COM_API_KEY is not set in environment variables.")
    sys.exit(1)

client = COMcheckClient()
client.set_api_key(api_key)


def test_run_simulation_without_id():
    """Test running a simulation without providing a project ID, which won't update any project under the user's account."""
    test_project = copy.deepcopy(PROJECT_TEMPLATE)
    test_project.control.code = EnergyCodeOptions.CEZ_90_1_2022
    test_project.lighting.wholeBldgUse = copy.deepcopy(TEST_BUILDING_AREA)
    test_project.envelope = copy.deepcopy(TEST_PROJECT_ENVELOPE)
    project_data = test_project
    simulation_session_id = client.start_run_simulation(project_data)
    print("Run simulation", simulation_session_id)
    return simulation_session_id


def test_run_simulation_with_id():
    """Test running a simulation with a project ID, which will update the project"""
    test_project = copy.deepcopy(PROJECT_TEMPLATE)
    test_project.project.projectTitle = "Simulation test"
    test_project.control.code = EnergyCodeOptions.CEZ_90_1_2022
    test_project.lighting.wholeBldgUse = copy.deepcopy(TEST_BUILDING_AREA)
    test_project.envelope = copy.deepcopy(TEST_PROJECT_ENVELOPE)

    # Check existing projects to find "Simulation test" project
    project_list = client.list_projects()

    # Find project with name "Simulation test"
    project_id = None
    for project in project_list:
        if project.get("name") == "Simulation test":
            project_id = project.get("_id")
            print(f"Found 'Simulation test' project with ID: {project_id}")
            break

    if not project_id:
        print("Project 'Simulation test' not found in project list")
        return None

    project_data = test_project
    print("project title:", project_data.project.projectTitle)

    simulation_session_id = client.start_run_simulation(project_data, project_id)
    print("Run simulation", simulation_session_id)
    return simulation_session_id


def test_get_simulation_status(session_id: str):
    """Test getting simulation status."""
    status_info = client.get_simulation_status(session_id)
    print("Simulation status:", status_info)
    return status_info


def test_get_simulation_result(session_id: str):
    """Test getting simulation result."""
    result_info = client.get_simulation_result(session_id)
    print("Simulation result:", result_info)
    return result_info


if __name__ == "__main__":
    # session_id = test_run_simulation_without_id()
    # session_id = test_run_simulation_with_id()
    session_id = "4c4a0076-347d-49ae-80f8-b301dc0bec85"  # Replace with actual session ID from test_run_simulation
    test_get_simulation_status(session_id)
    test_get_simulation_result(session_id)
