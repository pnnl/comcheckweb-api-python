"""Build a complete project: building area + roof + walls + windows.

Demonstrates a fuller workflow that mirrors a real compliance check.
"""

import os
import time

from comcheck_api import (
    COMcheckClient,
    project_building_area_operations as ba_ops,
    project_envelope_operations as env_ops,
)
from comcheck_api.defaults import (
    get_default_project_template,
    get_default_building_area_template,
    get_default_roof_template,
    get_default_ag_wall_template,
    get_default_window_template,
    get_default_door_template,
)


def main() -> None:
    client = COMcheckClient(api_key=os.environ["COM_API_KEY"])

    # Project metadata
    project = get_default_project_template()
    project.Project.title = "5,000 sqft office"

    # Add an open-office building area
    area = get_default_building_area_template()
    area.areaDescription = "Open office"
    project = ba_ops.add_building_area_to_project(project, area)

    # Roof
    roof = get_default_roof_template()
    roof.area = 5000.0
    project = env_ops.add_roof_to_project(project, roof)

    # Four walls
    for direction, area_sqft in [
        ("North", 1500.0),
        ("South", 1500.0),
        ("East", 1000.0),
        ("West", 1000.0),
    ]:
        wall = get_default_ag_wall_template()
        wall.name = f"{direction} wall"
        wall.area = area_sqft
        project = env_ops.add_ag_wall_to_project(project, wall)

    # A south-facing window and an entry door
    window = get_default_window_template()
    window.name = "South window"
    window.area = 200.0
    project = env_ops.add_window_to_project(project, window)

    door = get_default_door_template()
    door.name = "Main entry"
    project = env_ops.add_door_to_project(project, door)

    # Simulate
    session_id = client.start_run_simulation(project)
    print(f"Simulation started: {session_id}")

    deadline = time.time() + 300
    while time.time() < deadline:
        status = client.get_simulation_status(session_id)
        if status["status"] == "complete":
            break
        if status["status"] == "error":
            raise RuntimeError(f"Simulation failed: {status.get('message')}")
        time.sleep(5)
    else:
        raise TimeoutError("Simulation did not complete in 5 minutes")

    result = client.get_simulation_result(session_id)
    margin = result["performanceRating"]
    verdict = "PASS" if margin >= 0 else "FAIL"
    print(f"Result: {verdict} ({margin}% margin)")


if __name__ == "__main__":
    main()
