"""Script to test COMcheck API client and project operations."""

import os
import sys

from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from comcheck_api.comcheck_client import COMcheckClient
from comcheck_api.projectOperations import (
    project_building_area_operations,
    project_envelope_operations,
)
from comcheck_api.utilities.common import export_to_json
from comcheck_api.get_project_default import (
    get_default_ag_wall_template,
    get_default_building_area_template,
    get_default_project_template,
    get_default_roof_template,
    get_default_skylight_template,
    get_default_window_template,
)

load_dotenv()

api_key = os.getenv("COM_API_KEY")
if not api_key:
    print("COM_API_KEY is not set in environment variables.")
    sys.exit(1)

client = COMcheckClient()
client.set_api_key(api_key)


# Test API services Functions
def test_get_project_and_project_list():
    """Test getting project list and first project details."""
    try:
        response = client.list_projects()
        project_list = response.get("data", [])

        if project_list and (project_list[0].get("_id") or project_list[0].get("id")):
            project_id = project_list[0].get("_id") or project_list[0].get("id")
            project = client.get_project(project_id)
            return project.get("data")
        return None
    except Exception as err:
        print(f"Error in test_get_project_and_project_list: {err}")
        return None


def test_update_project_with_default_dummy_project(test_project_id: str):
    """Test updating project with default template."""
    try:
        default_project = get_default_project_template()
        update_resp = client.update_project(test_project_id, default_project)
        return update_resp
    except Exception as err:
        print(f"Error in test_update_project_with_default_dummy_project: {err}")


# Test building area operations
def test_update_project_with_add_building_area(test_project_id: str):
    """Test adding a building area to project."""
    try:
        response = client.get_project(test_project_id)
        test_project = response.get("data")
        if not test_project:
            print("No test project data found.")
            return
        default_building_area = get_default_building_area_template()
        updated_project = project_building_area_operations.add_building_area_to_project(
            test_project, default_building_area
        )
        if updated_project.get("id"):
            update_resp = client.update_project(updated_project["id"], updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_project_with_add_building_area: {err}")
        return


# Test envelope operations
# Adding roof, agWall, bgWall, and floor are similar, only roof and bgWall shown here
def test_update_project_with_add_roof(test_project_id: str):
    """Test adding a roof to project."""
    try:
        default_roof = get_default_roof_template()
        response = client.get_project(test_project_id)
        # Add a new roof to the project
        response_project = response.get("data")

        if not response_project:
            print("No test project data found.")
            return

        whole_bldg_use = response_project.get("lighting", {}).get("wholeBldgUse", [])
        building_area_key = whole_bldg_use[0].get("key") if whole_bldg_use else None

        if not building_area_key:
            print("No building area key found in whole building use, cannot add roof.")
            return

        updated_project = project_envelope_operations.add_roof_to_project(
            response_project, building_area_key, default_roof
        )
        if updated_project.get("id"):
            update_resp = client.update_project(updated_project["id"], updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_project_with_add_roof: {err}")
        return


def test_update_project_with_add_skylight(test_project_id: str):
    """Test adding a skylight to project."""
    try:
        response = client.get_project(test_project_id)
        test_project = response.get("data")

        if not test_project:
            print("No test project data found.")
            return

        envelope = test_project.get("envelope", {})
        roof_list = envelope.get("roof", [])

        if roof_list:
            default_skylight = get_default_skylight_template()
            whole_bldg_use = test_project.get("lighting", {}).get("wholeBldgUse", [])

            updated_project = project_envelope_operations.add_skylight_to_project(
                test_project,
                whole_bldg_use[0]["key"],
                default_skylight,
                roof_list[0],
            )
            if updated_project.get("id"):
                update_resp = client.update_project(
                    updated_project["id"], updated_project
                )
                return update_resp
            else:
                print(
                    "No id found on updated project, skipping updateProject API call."
                )
                return
        else:
            print("No roof found in test project, cannot add skylight.")
            return
    except Exception as err:
        print(f"Error in test_update_project_with_add_roof_and_skylight: {err}")
        return


# Adding window, door are similar, only window shown here
def test_update_project_with_add_window(test_project_id: str):
    """Test adding a window to project."""
    try:
        response = client.get_project(test_project_id)
        test_project = response.get("data")

        if not test_project:
            print("No test project data found.")
            return

        # Get building area key
        whole_bldg_use = test_project.get("lighting", {}).get("wholeBldgUse", [])
        building_area_key = whole_bldg_use[0].get("key") if whole_bldg_use else None

        if not building_area_key:
            print("No building area key found, cannot add agWall and window.")
            return

        # Check if an agWall exists
        envelope = test_project.get("envelope", {})
        ag_wall_list = envelope.get("agWall", [])

        if ag_wall_list:
            # Use existing agWall
            ag_wall = ag_wall_list[0]
            print("Using existing agWall")
        else:
            # Add a new agWall to the project
            print("No agWall found, adding a new one")
            default_ag_wall = get_default_ag_wall_template()
            # Set the bldgUseKey on the agWall
            default_ag_wall["bldgUseKey"] = building_area_key
            test_project = project_envelope_operations.add_ag_wall_to_project(
                test_project, building_area_key, default_ag_wall
            )

            # Get the newly added agWall (it should be the last one in the array)
            ag_wall = test_project["envelope"]["agWall"][-1]

        # Now add a window to the agWall
        default_window = get_default_window_template()
        updated_project = project_envelope_operations.add_window_to_project(
            test_project, building_area_key, default_window, ag_wall
        )

        if updated_project.get("id"):
            update_resp = client.update_project(updated_project["id"], updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_project_with_add_window: {err}")
        return


def test_update_project_with_add_thermal_bridge(test_project_id: str):
    """Test adding a thermal bridge to project."""
    try:
        response = client.get_project(test_project_id)
        test_project = response.get("data")

        if not test_project:
            print("No test project data found.")
            return

        # Get building area key
        whole_bldg_use = test_project.get("lighting", {}).get("wholeBldgUse", [])
        building_area_key = whole_bldg_use[0].get("key") if whole_bldg_use else None

        if not building_area_key:
            print("No building area key found, cannot add thermal bridge.")
            return

        # Check if an agWall exists (thermal bridges can only be added to agWalls)
        envelope = test_project.get("envelope", {})
        ag_wall_list = envelope.get("agWall", [])

        if ag_wall_list:
            # Use existing agWall
            ag_wall = ag_wall_list[0]
            print("Using existing agWall for thermal bridge")
        else:
            # Add a new agWall to the project
            print("No agWall found, adding a new one for thermal bridge")
            default_ag_wall = get_default_ag_wall_template()
            # Set the bldgUseKey on the agWall
            default_ag_wall["bldgUseKey"] = building_area_key
            test_project = project_envelope_operations.add_ag_wall_to_project(
                test_project, building_area_key, default_ag_wall
            )

            # Get the newly added agWall (it should be the last one in the array)
            ag_wall = test_project["envelope"]["agWall"][-1]

        # Now add a thermal bridge to the agWall
        updated_project = project_envelope_operations.add_thermal_bridge_to_project(
            test_project,
            building_area_key,
            ag_wall,
            # Optional parameters: thermal_bridge_type, thermal_bridge_category,
            # thermal_bridge_compliance_type, psi_factor, chi_factor, thermal_bridge_length
        )

        if updated_project.get("id"):
            update_resp = client.update_project(updated_project["id"], updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_project_with_add_thermal_bridge: {err}")
        return


def test_update_project_with_fixture_schedule(test_project_id: str):
    """Test adding fixture schedule to project."""
    try:
        response = client.get_project(test_project_id)
        test_project = response.get("data")

        if not test_project:
            print("No test project data found.")
            return

        if test_project.get("lighting"):
            # Note: This requires project_lighting_operations module to be converted
            print(
                "Fixture schedule test not yet implemented - requires lighting operations module"
            )
            # from src.projectOperations import project_lighting_operations
            # from src.utilities.project_defaults import get_default_fixture_schedule_template
            # default_fixture_schedule = get_default_fixture_schedule_template()
            # updated_project = project_lighting_operations.add_fixture_schedule_to_project(
            #     test_project, default_fixture_schedule
            # )
            # if updated_project.get("id"):
            #     update_resp = client.update_project(
            #         updated_project["id"], updated_project
            #     )
            #     # print("Project after adding fixture schedule:", update_resp)
            #     return update_resp
            # else:
            #     print("No id found on updated project, skipping updateProject API call.")
            #     return
        else:
            print("No lighting found in test project, cannot add fixture schedule.")
            return
    except Exception as err:
        print(f"Error in test_update_project_with_fixture_schedule: {err}")
        return


# Main Test Execution
def main():
    """Main test execution function."""
    # test project is the first project in the project list
    test_project = test_get_project_and_project_list()
    export_to_json(test_project, "testProjectJson/initialProject.json")

    if test_project:
        # default_project=test_update_project_with_default_dummy_project(test_project["id"])
        # export_to_json(default_project, "testProjectJson/defaultProject.json")
        # building_area_project = test_update_project_with_add_building_area(test_project["id"])
        # export_to_json(building_area_project, "testProjectJson/buildingAreaAddedProject.json")

        # roof_project = test_update_project_with_add_roof(test_project["id"])
        # export_to_json(roof_project, "testProjectJson/roofAddedProject.json")

        # skylight_project = test_update_project_with_add_skylight(test_project["id"])
        # export_to_json(skylight_project, "testProjectJson/skylightAddedProject.json")
        # window_project = test_update_project_with_add_window(test_project["id"])
        # export_to_json(window_project, "testProjectJson/windowAddedProject.json")

        thermal_bridge_project = test_update_project_with_add_thermal_bridge(
            test_project["id"]
        )
        export_to_json(
            thermal_bridge_project, "testProjectJson/thermalBridgeAddedProject.json"
        )
        # test_update_project_with_fixture_schedule(test_project["id"])


if __name__ == "__main__":
    main()
