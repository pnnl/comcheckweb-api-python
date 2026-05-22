"""Build a small office project from defaults and run a simulation.

Demonstrates:
- Using a default project template.
- Customizing project metadata.
- Adding an envelope component.
- Polling the simulation to completion.
"""

import os
import time

from comcheck_api import COMcheckClient, project_envelope_operations as env_ops
from comcheck_api.defaults import (
    get_default_project_template,
    get_default_ag_wall_template,
)


def main() -> None:
    client = COMcheckClient(api_key=os.environ["COM_API_KEY"])

    project = get_default_project_template()
    project.Project.title = "Small Seattle office"

    south_wall = get_default_ag_wall_template()
    south_wall.name = "South wall"
    south_wall.area = 1200.0
    project = env_ops.add_ag_wall_to_project(project, south_wall)

    session_id = client.start_run_simulation(project)
    print(f"Started simulation {session_id}")

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
    print(f"Performance rating: {result['performanceRating']}")


if __name__ == "__main__":
    main()
