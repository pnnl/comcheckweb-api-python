"""Script to test simulations."""

import copy
import os
import sys

# Add compcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from comcheck_api.comcheck_client import COMcheckClient
from comcheck_api.constants.common_constants import (
    DUMMY_PROJECT,
    DUMMY_BUILDING_AREA,
    DUMMY_PROJECT_ENVELOPE,
)
from comcheck_api.types.core_types import EnergyCodeOptions

load_dotenv()

# AWS API Gateway API keys are used for tracking and controlling API usage by clients.
api_key = os.getenv("COM_API_KEY")
if not api_key:
    print("COM_API_KEY is not set in environment variables.")
    sys.exit(1)

client = COMcheckClient()
client.set_api_key(api_key)


def test_run_simulation():
    """Test running a simulation."""
    test_project = copy.deepcopy(DUMMY_PROJECT)
    test_project.control.code = EnergyCodeOptions.CEZ_90_1_2022
    test_project.lighting.wholeBldgUse = copy.deepcopy(DUMMY_BUILDING_AREA)
    test_project.envelope = copy.deepcopy(DUMMY_PROJECT_ENVELOPE)
    project_data = test_project
    simulation_session_id = client.start_run_simulation(project_data)
    print("Run simulation", simulation_session_id)
    return simulation_session_id


def test_get_simulation_status(sessionId: str):
    """Test getting simulation status."""
    status_info = client.get_simulation_status(sessionId)
    print("Simulation status:", status_info)
    return status_info


def test_get_simulation_result(sessionId: str):
    """Test getting simulation result."""
    result_info = client.get_simulation_result(sessionId)
    print("Simulation result:", result_info)
    return result_info


def main():
    """Main function to run the simulation test."""
    test_run_simulation()


if __name__ == "__main__":
    session_id = test_run_simulation()
    # session_id = "3c6f3255-6472-4846-950a-6b10d5dfd369"  # Replace with actual session ID from test_run_simulation
    test_get_simulation_status(session_id)
    test_get_simulation_result(session_id)
