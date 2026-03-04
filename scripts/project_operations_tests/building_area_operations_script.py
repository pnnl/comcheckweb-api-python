"""Integration tests for building area operations.

These tests use the COMcheck API client to perform building area operations on actual projects.
Each test modifies a project and saves the result to testProjectJson/ directory.
"""

import os
import sys
from typing import List

from dotenv import load_dotenv

# Add comcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from comcheck_api.client import COMcheckClient
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.utilities.common import export_to_json
from comcheck_api.utilities.get_project_default import (
    get_default_building_area_template,
)
from comcheck_api.types.core_types import *

load_dotenv()

# AWS API Gateway API keys are used for tracking and controlling API usage by clients.
api_key = os.getenv("COM_API_KEY")
if not api_key:
    print("COM_API_KEY is not set in environment variables.")
    sys.exit(1)

client = COMcheckClient()
client.set_api_key(api_key)


# ========== Building Area Operations ==========


def test_add_building_area(test_project_id: str):
    """Test adding a building area to project."""
    try:
        test_project = client.get_project(test_project_id)
        if not test_project:
            print("No test project data found.")
            return
        default_building_area = get_default_building_area_template()
        updated_project = project_building_area_operations.add_building_area_to_project(
            test_project, default_building_area
        )
        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_building_area: {err}")
        return


def test_update_building_area(test_project_id: str):
    """Test updating a building area in the project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        whole_bldg_use: List[WholeBldgUse] = (
            test_project.get_by_path("lighting.wholeBldgUse") or []
        )
        if not whole_bldg_use:
            print(
                "No building areas found in test project, cannot update building area."
            )
            return
        building_area_key = whole_bldg_use[0].key
        updates = {
            "wholeBldgType": WholeBuildingTypeOptions.WHOLE_BUILDING_COURT_HOUSE,
            "areaDescription": "Updated building area description",
            "floorArea": 2500,
        }

        updated_project = (
            project_building_area_operations.update_building_area_in_project(
                test_project, building_area_key, updates
            )
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_building_area: {err}")
        return


# ========== Main Test Runner ==========


def main(test_number: int | None = None):
    """Main test execution function - runs building area integration tests."""
    print("=" * 80)
    print("Building Area Operations Integration Tests")
    print("=" * 80)

    # Get test project
    projects = client.list_projects()
    if not projects or not (project_id := projects[0].get("_id")):
        print("✗ No projects found")
        return

    # Export initial project state
    test_project_json = client.get_project(project_id, mode="json")
    export_to_json(test_project_json, "testProjectJson/initialProject.json")
    print(f"\n✓ Using project ID: {project_id}")
    print(f"  Exported initial state to: testProjectJson/initialProject.json\n")

    failed_tests = []

    tests = {
        1: (
            "Adding building area",
            lambda: test_add_building_area(project_id),
            "testProjectJson/buildingAreaAddedProject.json",
            "Building area added",
        ),
        2: (
            "Updating building area",
            lambda: test_update_building_area(project_id),
            "testProjectJson/buildingAreaUpdatedProject.json",
            "Building area updated",
        ),
    }

    # Determine which tests to run
    if test_number is not None:
        if test_number not in tests:
            print(f"✗ Invalid test number: {test_number}")
            print(f"Valid test numbers are 1-{len(tests)}")
            return
        tests_to_run = {test_number: tests[test_number]}
        print(f"\nRunning single test: #{test_number}")
    else:
        tests_to_run = tests

    # Building Area Tests
    if test_number is None:
        print("-" * 80)
        print("BUILDING AREA OPERATIONS")
        print("-" * 80)

    for num, (test_name, test_func, output_file, success_msg) in tests_to_run.items():
        print(f"\n{num}. {test_name}...")
        result = test_func()
        if result:
            export_to_json(result, output_file)
            print(f"   ✓ {success_msg}")
        else:
            failed_tests.append(test_name)

    print("\n" + "=" * 80)
    print("Building Area Tests Complete")

    # Print summary of failed tests
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
