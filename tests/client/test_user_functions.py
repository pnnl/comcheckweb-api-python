# """Tests for COMcheck API client user functions."""

# import pytest
# from comcheck_api.client import COMcheckClient
# from comcheck_api.defaults import get_default_project_template


# @pytest.fixture
# def client(monkeypatch):
#     """Create a COMcheck client with mocked API key."""
#     client = COMcheckClient()
#     monkeypatch.setenv("COM_API_KEY", "test-api-key")
#     client.set_api_key("test-api-key")
#     return client


# @pytest.fixture
# def mock_project_list():
#     """Mock project list response."""
#     return [
#         {
#             "_id": "test-project-id",
#             "name": "Test Project",
#             "type": "NEW_BUILDING"
#         }
#     ]


# def test_list_projects(client, mocker, mock_project_list):
#     """Test listing projects."""
#     mocker.patch.object(client, 'list_projects', return_value=mock_project_list)
#     projects = client.list_projects()
#     assert projects is not None, "Should return project list"
#     assert len(projects) > 0, "Should return at least one project"
#     assert "_id" in projects[0], "Project should have an ID"


# def test_get_project_json(client, mocker, mock_project_list):
#     """Test getting project in JSON format."""
#     project_id = mock_project_list[0]["_id"]
#     mock_project = {"id": project_id, "name": "Test Project"}
#     mocker.patch.object(client, 'get_project', return_value=mock_project)

#     project = client.get_project(project_id, mode="json")
#     assert project is not None, "Should return project data"
#     assert isinstance(project, dict), "Should return JSON data as dict"


# def test_get_project_python(client, mocker, mock_project_list):
#     """Test getting project as Python object."""
#     project_id = mock_project_list[0]["_id"]
#     mock_project = get_default_project_template()
#     mock_project.projectName = "Test Project"
#     mocker.patch.object(client, 'get_project', return_value=mock_project)

#     project = client.get_project(project_id)
#     assert project is not None, "Should return project data"
#     assert hasattr(project, 'projectName'), "Should return project object with attributes"


# def test_update_project(client, mocker, mock_project_list):
#     """Test updating project with default template."""
#     project_id = mock_project_list[0]["_id"]
#     default_project = get_default_project_template()
#     mock_response = {"id": project_id, "status": "updated"}
#     mocker.patch.object(client, 'update_project', return_value=mock_response)

#     response = client.update_project(project_id, default_project)
#     assert response is not None, "Should return update response"
#     assert response["status"] == "updated", "Should indicate successful update"
