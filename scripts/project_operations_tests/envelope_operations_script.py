"""Integration tests for envelope operations.

These tests use the COMcheck API client to perform envelope operations on actual projects.
Each test modifies a project and saves the result to testProjectJson/ directory.
"""

import os
import sys
from typing import List

from dotenv import load_dotenv

# Add comcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from comcheck_api.client import COMcheckClient
from comcheck_api.project_operations import project_envelope_operations
from comcheck_api.utilities.common import export_to_json
from comcheck_api.utilities.get_project_default import (
    get_default_ag_wall_template,
    get_default_bg_wall_template,
    get_default_floor_template,
    get_default_roof_template,
    get_default_skylight_template,
    get_default_window_template,
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


# ========== Envelope Assembly Operations (Roof, Floor, Walls) ==========


def test_add_roof(test_project_id: str):
    """Test adding a roof to project."""
    try:
        default_roof = get_default_roof_template()
        response_project = client.get_project(test_project_id)

        if not response_project:
            print("No test project data found.")
            return

        whole_bldg_use = response_project.get_by_path("lighting.wholeBldgUse", [])
        building_area_key = (
            getattr(whole_bldg_use[0], "key") if whole_bldg_use else None
        )

        if not building_area_key:
            print("No building area key found in whole building use, cannot add roof.")
            return

        updated_project = project_envelope_operations.add_roof_to_project(
            response_project, building_area_key, default_roof
        )
        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_roof: {err}")
        return


def test_update_roof(test_project_id: str):
    """Test updating a roof in the project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        roofs: List[Roof] = test_project.get_by_path("envelope.roof") or []

        if not roofs:
            print("No roofs found in test project, cannot update roof.")
            return
        roof_assembly_type = roofs[0].assemblyType
        updates = {
            "description": "Updated roof description",
        }

        updated_project = project_envelope_operations.update_roof_in_project(
            test_project, roof_assembly_type, updates
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_roof: {err}")
        return


def test_add_floor(test_project_id: str):
    """Test adding a floor to project."""
    try:
        default_floor = get_default_floor_template()
        response_project = client.get_project(test_project_id)

        if not response_project:
            print("No test project data found.")
            return

        whole_bldg_use = response_project.get_by_path("lighting.wholeBldgUse", [])
        building_area_key = (
            getattr(whole_bldg_use[0], "key") if whole_bldg_use else None
        )

        if not building_area_key:
            print("No building area key found in whole building use, cannot add floor.")
            return

        updated_project = project_envelope_operations.add_floor_to_project(
            response_project, building_area_key, default_floor
        )
        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_floor: {err}")
        return


def test_update_floor(test_project_id: str):
    """Test updating a floor in the project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        floors: List[Floor] = test_project.get_by_path("envelope.floor") or []

        if not floors:
            print("No floors found in test project, cannot update floor.")
            return

        floor_assembly_type = floors[0].assemblyType
        updates = {
            "description": "Updated floor description",
        }

        updated_project = project_envelope_operations.update_floor_in_project(
            test_project, floor_assembly_type, updates
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_floor: {err}")
        return


def test_add_ag_wall(test_project_id: str):
    """Test adding an agWall to project."""
    try:
        default_ag_wall = get_default_ag_wall_template()
        response_project = client.get_project(test_project_id)

        if not response_project:
            print("No test project data found.")
            return

        whole_bldg_use = response_project.get_by_path("lighting.wholeBldgUse", [])
        building_area_key = (
            getattr(whole_bldg_use[0], "key") if whole_bldg_use else None
        )

        if not building_area_key:
            print(
                "No building area key found in whole building use, cannot add agWall."
            )
            return

        updated_project = project_envelope_operations.add_ag_wall_to_project(
            response_project, building_area_key, default_ag_wall
        )
        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_ag_wall: {err}")
        return


def test_update_ag_wall(test_project_id: str):
    """Test updating an agWall in the project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        ag_walls: List[AgWall] = test_project.get_by_path("envelope.agWall") or []

        if not ag_walls:
            print("No agWalls found in test project, cannot update agWall.")
            return

        ag_wall_assembly_type = ag_walls[0].assemblyType
        updates = {
            "description": "Updated agWall description",
        }

        updated_project = project_envelope_operations.update_ag_wall_in_project(
            test_project, ag_wall_assembly_type, updates
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_ag_wall: {err}")
        return


def test_add_bg_wall(test_project_id: str):
    """Test adding a bgWall to project."""
    try:
        default_bg_wall = get_default_bg_wall_template()
        response_project = client.get_project(test_project_id)

        if not response_project:
            print("No test project data found.")
            return

        whole_bldg_use = response_project.get_by_path("lighting.wholeBldgUse", [])
        building_area_key = (
            getattr(whole_bldg_use[0], "key") if whole_bldg_use else None
        )

        if not building_area_key:
            print(
                "No building area key found in whole building use, cannot add bgWall."
            )
            return

        updated_project = project_envelope_operations.add_bg_wall_to_project(
            response_project, building_area_key, default_bg_wall
        )
        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_bg_wall: {err}")
        return


def test_update_bg_wall(test_project_id: str):
    """Test updating a bgWall in the project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        bg_walls: List[BgWall] = test_project.get_by_path("envelope.bgWall") or []

        if not bg_walls:
            print("No bgWalls found in test project, cannot update bgWall.")
            return

        bg_wall_assembly_type = bg_walls[0].assemblyType
        updates = {
            "description": "Updated bgWall description",
        }

        updated_project = project_envelope_operations.update_bg_wall_in_project(
            test_project, bg_wall_assembly_type, updates
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_bg_wall: {err}")
        return


# ========== Nested Component Operations (Skylight, Window, Door, Thermal Bridge) ==========


def test_add_nested_skylight(test_project_id: str):
    """Test adding a skylight to project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        roof_list = test_project.get_by_path("envelope.roof", [])

        if roof_list:
            default_skylight = get_default_skylight_template()
            whole_bldg_use: List[WholeBldgUse] = test_project.get_by_path(
                "lighting.wholeBldgUse", []
            )

            updated_project = project_envelope_operations.add_skylight_to_project(
                test_project,
                whole_bldg_use[0].key,
                default_skylight,
                roof_list[0],
            )
            if project_id := getattr(updated_project, "id"):
                update_resp = client.update_project(project_id, updated_project)
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
        print(f"Error in test_add_skylight: {err}")
        return


def test_add_orphaned_skylight(test_project_id: str):
    """Test adding an orphaned skylight to project (alteration project)."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        # Update project to ALTERATION to have orphaned skylights
        test_project.projectType = ProjectTypeOptions.ALTERATION
        test_project = ComBuilding(
            **client.update_project(test_project_id, test_project)
        )
        print("  Project type updated to ALTERATION")

        default_skylight = get_default_skylight_template()
        whole_bldg_use: List[WholeBldgUse] = test_project.get_by_path(
            "lighting.wholeBldgUse", []
        )

        updated_project = project_envelope_operations.add_skylight_to_project(
            test_project,
            whole_bldg_use[0].key,
            default_skylight,
        )
        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_orphaned_skylight: {err}")
        return


def test_update_orphaned_skylight(test_project_id: str):
    """Test updating an orphaned skylight.

    First updates the project to ALTERATION type, then updates the orphaned skylight.
    """
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        # Update project to ALTERATION to have orphaned skylights
        test_project.projectType = ProjectTypeOptions.ALTERATION
        test_project = client.update_project(test_project_id, test_project)
        print("  Project type updated to ALTERATION")

        # TODO: need to wait project update complete before moving forward (update function to async?)
        export_to_json(test_project, "testProjectJson/orphanedSkylightProject.json")

        # pull the project again to ensure we have the latest data
        updated_project = client.get_project(test_project_id)
        # Check for orphaned skylights
        orphaned_skylights = updated_project.envelope.skylight

        if not orphaned_skylights:
            print("No orphaned skylights found, cannot update orphaned skylight.")
            return

        skylight_assembly_type = orphaned_skylights[0].assemblyType
        print(f"  Found orphaned skylight: {skylight_assembly_type}")

        # Update the skylight
        updates = {
            "description": "Updated orphaned skylight description",
        }

        updated_project = project_envelope_operations.update_skylight_in_project(
            updated_project, skylight_assembly_type, updates
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_orphaned_skylight: {err}")
        return


def test_update_nested_skylight(test_project_id: str):
    """Test updating a nested skylight (in roof.skylight)."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        # Check for nested skylights in roofs
        roof_list = test_project.get_by_path("envelope.roof", [])
        nested_skylights = []
        if roof_list:
            for roof in roof_list:
                roof_skylights = getattr(roof, "skylight", [])
                if roof_skylights:
                    nested_skylights.extend(roof_skylights)

        if not nested_skylights:
            print("No nested skylights found in roofs, cannot update nested skylight.")
            return

        skylight_assembly_type = nested_skylights[0].assemblyType
        print(f"  Found nested skylight in roof: {skylight_assembly_type}")

        # Update the skylight
        updates = {
            "description": "Updated nested skylight description",
        }

        updated_project = project_envelope_operations.update_skylight_in_project(
            test_project, skylight_assembly_type, updates
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_nested_skylight: {err}")
        return


# window and door are similar, so only testing window here. Orphaned window tests are not included since test would be similar to orphaned skylight tests.
def test_add_nested_window(test_project_id: str):
    """Test adding a window to project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        whole_bldg_use = test_project.get_by_path("lighting.wholeBldgUse", [])
        building_area_key = (
            getattr(whole_bldg_use[0], "key") if whole_bldg_use else None
        )

        if not building_area_key:
            print(
                "No building area key found in whole building use, cannot add window."
            )
            return

        # Check if an agWall exists
        ag_wall_list = test_project.get_by_path("envelope.agWall", [])

        if ag_wall_list:
            # Use existing agWall
            ag_wall = ag_wall_list[0]
            print("Using existing agWall")
        else:
            # Add a new agWall to the project
            print("No agWall found, adding a new one")
            default_ag_wall = get_default_ag_wall_template()
            # Set the bldgUseKey on the agWall
            default_ag_wall.bldgUseKey = building_area_key
            test_project = project_envelope_operations.add_ag_wall_to_project(
                test_project, building_area_key, default_ag_wall
            )

            # Get the newly added agWall (it should be the last one in the array)
            ag_wall = test_project.envelope.agWall[-1]

        # Now add a window to the agWall
        default_window = get_default_window_template()
        updated_project = project_envelope_operations.add_window_to_project(
            test_project, building_area_key, default_window, ag_wall
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_window: {err}")
        return


def test_update_nested_window(test_project_id: str):
    """Test updating a window in the project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return
        agWallList = test_project.get_by_path("envelope.agWall", [])
        if not agWallList:
            print("No agWalls found in test project, cannot update nested window.")
            return
        windows: List[Window] = agWallList[0].get_by_path("window") or []

        if not windows:
            print(
                "No nested windows found in test project, cannot update nested window."
            )
            return

        window_assembly_type = windows[0].assemblyType
        print(f"  Found nested window: {window_assembly_type}")
        updates = {
            "description": "Updated nested window description",
        }

        updated_project = project_envelope_operations.update_window_in_project(
            test_project, window_assembly_type, updates
        )

        if project_id := getattr(updated_project, "id"):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_update_window: {err}")
        return


def test_add_thermal_bridge(test_project_id: str):
    """Test adding a thermal bridge to project."""
    try:
        test_project = client.get_project(test_project_id)

        if not test_project:
            print("No test project data found.")
            return

        # Get building area key
        whole_bldg_use: List[WholeBldgUse] = (
            test_project.get_by_path("lighting.wholeBldgUse") or []
        )
        building_area_key = whole_bldg_use[0].key if whole_bldg_use else None

        if not building_area_key:
            print("No building area key found, cannot add thermal bridge.")
            return

        # Check if an agWall exists (thermal bridges can only be added to agWalls)
        ag_wall_list: List[AgWall] = test_project.get_by_path("envelope.agWall") or []

        if ag_wall_list:
            # Use existing agWall
            ag_wall = ag_wall_list[0]
            print("Using existing agWall for thermal bridge")
        else:
            # Add a new agWall to the project
            print("No agWall found, adding a new one for thermal bridge")
            default_ag_wall = get_default_ag_wall_template()
            # Set the bldgUseKey on the agWall
            default_ag_wall.bldgUseKey = building_area_key

            test_project = project_envelope_operations.add_ag_wall_to_project(
                test_project, building_area_key, default_ag_wall
            )

            # After adding, get the new agWall (should be last in list)
            envelope = getattr(test_project, "envelope", None)
            ag_wall_list = getattr(envelope, "agWall", []) if envelope else []
            ag_wall = ag_wall_list[-1] if ag_wall_list else None

        # Now add a thermal bridge to the agWall
        updated_project = project_envelope_operations.add_thermal_bridge_to_project(
            test_project,
            building_area_key,
            ag_wall,
            # Demo values for options (enums)
            thermal_bridge_type=ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER,
        )

        if project_id := getattr(updated_project, "id", None):
            update_resp = client.update_project(project_id, updated_project)
            return update_resp
        else:
            print("No id found on updated project, skipping updateProject API call.")
            return
    except Exception as err:
        print(f"Error in test_add_thermal_bridge: {err}")
        return


# ========== Main Test Runner ==========


def main(test_number: int = None):
    """Main test execution function - runs envelope integration tests.

    Args:
        test_number: Optional test number to run. If provided, only that test will run.
                     If None, all tests will run.
    """
    print("=" * 80)
    print("Envelope Operations Integration Tests")
    print("=" * 80)

    # Track failed tests
    failed_tests = []

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

    # Define all tests
    tests = {
        1: (
            "Adding roof",
            lambda: test_add_roof(project_id),
            "testProjectJson/roofAddedProject.json",
            "Roof added",
        ),
        2: (
            "Updating roof",
            lambda: test_update_roof(project_id),
            "testProjectJson/roofUpdatedProject.json",
            "Roof updated",
        ),
        3: (
            "Adding floor",
            lambda: test_add_floor(project_id),
            "testProjectJson/floorAddedProject.json",
            "Floor added",
        ),
        4: (
            "Updating floor",
            lambda: test_update_floor(project_id),
            "testProjectJson/floorUpdatedProject.json",
            "Floor updated",
        ),
        5: (
            "Adding agWall",
            lambda: test_add_ag_wall(project_id),
            "testProjectJson/agWallAddedProject.json",
            "AgWall added",
        ),
        6: (
            "Updating agWall",
            lambda: test_update_ag_wall(project_id),
            "testProjectJson/agWallUpdatedProject.json",
            "AgWall updated",
        ),
        7: (
            "Adding bgWall",
            lambda: test_add_bg_wall(project_id),
            "testProjectJson/bgWallAddedProject.json",
            "BgWall added",
        ),
        8: (
            "Updating bgWall",
            lambda: test_update_bg_wall(project_id),
            "testProjectJson/bgWallUpdatedProject.json",
            "BgWall updated",
        ),
        9: (
            "Adding nested skylight",
            lambda: test_add_nested_skylight(project_id),
            "testProjectJson/nestedSkylightAddedProject.json",
            "Nested skylight added",
        ),
        10: (
            "Updating nested skylight",
            lambda: test_update_nested_skylight(project_id),
            "testProjectJson/nestedSkylightUpdatedProject.json",
            "Nested skylight updated",
        ),
        11: (
            "Adding orphaned skylight",
            lambda: test_add_orphaned_skylight(project_id),
            "testProjectJson/orphanedSkylightAddedProject.json",
            "Orphaned skylight added",
        ),
        12: (
            "Updating orphaned skylight",
            lambda: test_update_orphaned_skylight(project_id),
            "testProjectJson/orphanedSkylightUpdatedProject.json",
            "Orphaned skylight updated",
        ),
        13: (
            "Adding nested window",
            lambda: test_add_nested_window(project_id),
            "testProjectJson/windowAddedProject.json",
            "Nested window added",
        ),
        14: (
            "Updating nested window",
            lambda: test_update_nested_window(project_id),
            "testProjectJson/windowUpdatedProject.json",
            "Nested window updated",
        ),
        15: (
            "Adding thermal bridge",
            lambda: test_add_thermal_bridge(project_id),
            "testProjectJson/thermalBridgeAddedProject.json",
            "Thermal bridge added",
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

    # Print section headers
    if test_number is None:
        print("-" * 80)
        print("ENVELOPE ASSEMBLY OPERATIONS (Roof, Floor, Walls)")
        print("-" * 80)

    # Run tests
    for num, (test_name, test_func, output_file, success_msg) in tests_to_run.items():
        # Print section header for nested components
        if test_number is None and num == 9:
            print("\n" + "-" * 80)
            print(
                "NESTED COMPONENT OPERATIONS (Skylight, Window, Door, Thermal Bridge)"
            )
            print("-" * 80)

        print(f"\n{num}. {test_name}...")
        result = test_func()
        if result:
            export_to_json(result, output_file)
            print(f"   ✓ {success_msg}")
        else:
            failed_tests.append(test_name)

    print("\n" + "=" * 80)
    print("Envelope Tests Complete")

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
