# """Tests for COMcheck API client simulation functions."""

# import copy
# import pytest
# from comcheck_api.client import COMcheckClient
# from comcheck_api.constants.common_constants import PROJECT_TEMPLATE
# from comcheck_api.types.core_types import EnergyCodeOptions
# from fixtures.components import SAMPLE_BUILDING_AREA, SAMPLE_PROJECT_ENVELOPE


# @pytest.fixture
# def client(monkeypatch):
#     """Create a COMcheck client with mocked API key."""
#     client = COMcheckClient()
#     monkeypatch.setenv("COM_API_KEY", "test-api-key")
#     client.set_api_key("test-api-key")
#     return client


# def test_run_simulation_without_id(client):
#     """Test running a simulation without providing a project ID."""
#     # Prepare test project
#     test_project = copy.deepcopy(PROJECT_TEMPLATE)
#     test_project.control.code = EnergyCodeOptions.CEZ_90_1_2022
#     test_project.lighting.wholeBldgUse = copy.deepcopy(SAMPLE_BUILDING_AREA)
#     test_project.envelope = copy.deepcopy(SAMPLE_PROJECT_ENVELOPE)

#     # Run simulation
#     session_id = client.start_run_simulation(test_project)
#     assert session_id is not None, "Should return a simulation session ID"


# def test_run_simulation_with_id(client):
#     """Test running a simulation with a project ID."""
#     # Prepare test project
#     test_project = copy.deepcopy(PROJECT_TEMPLATE)
#     test_project.project.projectTitle = "Simulation test"
#     test_project.control.code = EnergyCodeOptions.CEZ_90_1_2022
#     test_project.lighting.wholeBldgUse = copy.deepcopy(SAMPLE_BUILDING_AREA)
#     test_project.envelope = copy.deepcopy(SAMPLE_PROJECT_ENVELOPE)

#     # Mock project ID
#     project_id = "test-project-id"

#     # Run simulation
#     session_id = client.start_run_simulation(test_project, project_id)
#     assert session_id is not None, "Should return a simulation session ID"


# def test_get_simulation_status(client):
#     """Test getting simulation status."""
#     session_id = "test-session-id"
#     status_info = client.get_simulation_status(session_id)
#     assert status_info is not None, "Should return simulation status info"


# def test_get_simulation_result(client):
#     """Test getting simulation result."""
#     session_id = "test-session-id"
#     result_info = client.get_simulation_result(session_id)
#     assert result_info is not None, "Should return simulation result info"
