"""Live tests for COMcheckClient.

These hit the real COMcheck Web API and need a valid ``COM_API_KEY``. They
skip (rather than fail) when no key is set or the key is rejected, so the
offline suite stays green; provide a valid key to exercise them.
"""

import os

import pytest
from dotenv import load_dotenv

from comcheck_api.client import COMcheckClient
from comcheck_api.exceptions import COMCheckHTTPError

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def client():
    """Fixture to create and configure COMcheckClient."""
    api_key = os.getenv("COM_API_KEY")
    if not api_key:
        pytest.skip("COM_API_KEY is not set; skipping live client tests.")

    client = COMcheckClient()
    client.set_api_key(api_key)
    return client


def test_fetch_project_list(client: COMcheckClient):
    """Test fetching the project list."""
    try:
        project_list = client.list_projects()
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise
    assert isinstance(project_list, list)


def test_fetch_single_project(client: COMcheckClient):
    """Test fetching a single project if any exist."""
    try:
        project_list = client.list_projects()
    except COMCheckHTTPError as exc:
        if exc.status_code in (401, 403):
            pytest.skip(
                f"COM_API_KEY rejected ({exc.status_code}); skipping live test."
            )
        raise

    if project_list and project_list[0].get("_id"):
        project = client.get_project(project_list[0]["_id"])
        assert project is not None
    else:
        # If no projects exist, just pass the test
        assert True
