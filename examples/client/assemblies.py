"""Example of using COMcheck API client assembly u-value calculation."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.defaults import (
    get_default_project_template,
    get_default_building_area_template,
    get_default_ag_wall_template,
    get_default_bg_wall_template,
    get_default_roof_template,
    get_default_floor_template,
)
from comcheck_api.project_operations import (
    project_building_area_operations,
    project_envelope_operations,
)
from comcheck_api.types.core_types import EnergyCodeOptions

# Initialize client
load_dotenv()
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Build a project with one of each calculated-u-value assembly. Only agWall,
# bgWall, roof, and floor receive calculated u-values (effectiveUFactor is
# agWall-only).
project = get_default_project_template()
project.control.code = EnergyCodeOptions.CEZ_90_1_2022

project = project_building_area_operations.add_building_area_to_project(
    project, get_default_building_area_template()
)
building_area_key = str(project.lighting.wholeBldgUse[0].key)

project = project_envelope_operations.add_ag_wall_to_project(
    project, building_area_key, get_default_ag_wall_template()
)
project = project_envelope_operations.add_bg_wall_to_project(
    project, building_area_key, get_default_bg_wall_template()
)
project = project_envelope_operations.add_roof_to_project(
    project, building_area_key, get_default_roof_template()
)
project = project_envelope_operations.add_floor_to_project(
    project, building_area_key, get_default_floor_template()
)


def print_uvalues(label: str) -> None:
    print(f"\n{label}")
    for kind, items in [
        ("agWall", project.envelope.agWall),
        ("bgWall", project.envelope.bgWall),
        ("roof", project.envelope.roof),
        ("floor", project.envelope.floor),
    ]:
        for item in items:
            print(
                f"  {kind:7} {item.assemblyType!r:30} "
                f"effectiveUFactor={getattr(item, 'effectiveUFactor', None)} "
                f"propUValue={item.propUValue}"
            )


# Example: Calculate assembly u-values and update the project in place.
# (start_run_simulation calls this automatically; call it directly when you
# want refreshed u-values outside the simulation flow.)
print_uvalues("Before update_uvalues:")
project = client.update_uvalues(project)
print_uvalues("After update_uvalues:")
