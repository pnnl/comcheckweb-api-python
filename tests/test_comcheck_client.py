"""Tests for COMcheckClient."""

import os

import pytest
from dotenv import load_dotenv

from src.comcheck_client import COMcheckClient

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def client():
    """Fixture to create and configure COMcheckClient."""
    api_key = os.getenv("COM_API_KEY")
    if not api_key:
        pytest.fail("COM_API_KEY is not set in environment variables.")

    client = COMcheckClient()
    client.set_api_key(api_key)
    return client


def test_fetch_project_list(client: COMcheckClient):
    """Test fetching the project list."""
    response = client.list_projects()
    project_list = response.get("data", [])
    assert isinstance(project_list, list)


def test_fetch_single_project(client: COMcheckClient):
    """Test fetching a single project if any exist."""
    response = client.list_projects()
    project_list = response.get("data", [])

    if project_list and project_list[0].get("_id"):
        project = client.get_project(project_list[0]["_id"])
        assert "data" in project
    else:
        # If no projects exist, just pass the test
        assert True
