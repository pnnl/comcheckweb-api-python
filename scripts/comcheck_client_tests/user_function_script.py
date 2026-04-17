"""Tests for COMcheckClient user functions: list_projects, get_project, update_project."""

import os
import sys

from dotenv import load_dotenv

# Add comcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from comcheck_api.client import COMcheckClient
from comcheck_api.defaults import get_default_project_template
from comcheck_api.utilities.common import export_to_json

load_dotenv()

# AWS API Gateway API keys are used for tracking and controlling API usage by clients.
api_key = os.getenv("COM_API_KEY")
if not api_key:
    print("COM_API_KEY is not set in environment variables.")
    sys.exit(1)

client = COMcheckClient()
client.set_api_key(api_key)


def test_list_projects():
    """Test getting project list."""
    try:
        projects = client.list_projects()
        return projects
    except Exception as err:
        print(f"Error in test_list_projects: {err}")
        return None


def test_get_first_project_json():
    """Test getting first project details as JSON."""
    try:
        projects = client.list_projects()
        if projects and (project_id := projects[0].get("_id")):
            print(f"Testing with project ID: {project_id}")
            project = client.get_project(project_id, mode="json")
            return project
        return None
    except Exception as err:
        print(f"Error in test_get_first_project_json: {err}")
        return None


def test_get_first_project_python():
    """Test getting first project details as Python objects."""
    try:
        projects = client.list_projects()
        if projects and (project_id := projects[0].get("_id")):
            print(f"Testing with project ID: {project_id}")
            project = client.get_project(project_id)
            return project
        return None
    except Exception as err:
        print(f"Error in test_get_first_project_python: {err}")
        return None


def test_update_project_with_default_dummy_project(test_project_id: str):
    """Test updating project with default template."""
    try:
        default_project = get_default_project_template()
        update_resp = client.update_project(test_project_id, default_project)
        return update_resp
    except Exception as err:
        raise err


def main(test_number: int | None = None):
    """Main test execution function."""
    print("=" * 80)
    print("Testing COMcheck API Client - Basic Operations")
    print("=" * 80)

    def run_test_1():
        print("\n1. Testing list_projects()...")
        projects = test_list_projects()
        if projects is not None:
            print(f"✓ Successfully retrieved project list: {projects}")
            return True
        else:
            print("✗ Failed to retrieve project list")
            return False

    def run_test_2():
        print("\n2. Testing get_project() with JSON mode...")
        project_json = test_get_first_project_json()
        if project_json:
            print("✓ Successfully retrieved project as JSON")
            export_to_json(project_json, "testProjectJson/api_test_project_json.json")
            return True
        else:
            print("✗ Failed to retrieve project as JSON")
            return False

    def run_test_3():
        print("\n3. Testing get_project() with Python mode...")
        project_python = test_get_first_project_python()
        if project_python:
            print("✓ Successfully retrieved project as Python object")
            print(f"   Project name: {getattr(project_python, 'projectName', 'N/A')}")
            print(f"   Project type: {getattr(project_python, 'projectType', 'N/A')}")
            return True
        else:
            print("✗ Failed to retrieve project as Python object")
            return False

    def run_test_4():
        print("\n4. Testing update_project() with default template...")
        try:
            projects = client.list_projects()
            if projects and (project_id := projects[2].get("_id")):
                default_project = test_update_project_with_default_dummy_project(
                    project_id
                )
                if default_project:
                    print("✓ Successfully updated project with default template")
                    export_to_json(
                        default_project, "testProjectJson/api_test_default_project.json"
                    )
                    return True
                else:
                    print("✗ Failed to update project")
                    return False
            else:
                print("✗ No projects found to update")
                return False
        except Exception as err:
            print(f"✗ Error updating project: {err}")
            return False

    tests = {
        1: ("List projects", run_test_1),
        2: ("Get first project (JSON mode)", run_test_2),
        3: ("Get first project (Python mode)", run_test_3),
        4: ("Update project with default template", run_test_4),
    }

    if test_number is not None:
        if test_number not in tests:
            print(f"✗ Invalid test number: {test_number}")
            print(f"Valid test numbers are 1-{len(tests)}")
            return
        tests_to_run = {test_number: tests[test_number]}
        print(f"\nRunning single test: #{test_number}")
    else:
        tests_to_run = tests

    failed_tests = []

    for num, (test_name, test_func) in tests_to_run.items():
        if not test_func():
            failed_tests.append(test_name)

    print("\n" + "=" * 80)
    print("API Client User Function Tests Complete")

    if failed_tests:
        print(f"\n✗ {len(failed_tests)} test(s) failed:")
        for test_name in failed_tests:
            print(f"  - {test_name}")
    else:
        print("\n✓ All tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    import sys

    # Check if test number is provided as command line argument
    test_num = None
    if len(sys.argv) > 1:
        try:
            test_num = int(sys.argv[1])
        except ValueError:
            print(f"Error: '{sys.argv[1]}' is not a valid test number")
            sys.exit(1)

    # if test_num is provided, run only that test; otherwise run all tests
    main(test_num)
