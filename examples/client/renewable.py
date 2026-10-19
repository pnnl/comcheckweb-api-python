"""Example of using COMcheck API client renewable calculations."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api import project_renewable_operations as rn_ops
from comcheck_api.defaults import (
    get_default_project_template,
    get_default_building_area_template,
    get_default_roof_template,
    get_default_floor_template,
    get_default_renewable_system_template,
)
from comcheck_api.project_operations import (
    project_building_area_operations,
    project_envelope_operations,
)
from comcheck_api.types.core_types import (
    EnergyCodeOptions,
    RenewableSystemCapacityUnitOptions,
    RenewableSystemTypeOptions,
)

# Initialize client
load_dotenv(override=True)
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Build a project with a roof, a floor, and an on-site solar system.
project = get_default_project_template()
project.control.code = EnergyCodeOptions.CEZ_IECC2021

project = project_building_area_operations.add_building_area_to_project(
    project, get_default_building_area_template()
)
building_area_key = str(project.lighting.wholeBldgUse[0].key)

project = project_envelope_operations.add_roof_to_project(
    project, building_area_key, get_default_roof_template()
)
project = project_envelope_operations.add_floor_to_project(
    project, building_area_key, get_default_floor_template()
)
project = rn_ops.update_renewable_in_project(project, {"numberOfFloors": 3})

renewable_system = get_default_renewable_system_template()
renewable_system.description = "Rooftop Solar"
renewable_system.renewableSystemType = (
    RenewableSystemTypeOptions.RENEWABLE_SYSTEM_TYPE_SOLAR
)
renewable_system.renewableSystemCapacity = 50000.0
renewable_system.renewableSystemCapacityUnit = (
    RenewableSystemCapacityUnitOptions.RENEWABLE_SYSTEM_UNIT_WATT
)
project = rn_ops.add_renewable_system_to_project(project, renewable_system)

# Example 1: Calculate renewable areas and update the project in place.
project = client.area_for_renewable(project)
print(f"largestThreeFloorArea: {project.renewable.largestThreeFloorArea}")
print(f"roofAreaForRenewable: {project.renewable.roofAreaForRenewable}")

# Example 2: Calculate renewable capacity and update the project in place.
project = client.renewable_capacity(project)
print(f"requiredCapacity: {project.renewable.requiredCapacity}")
print(f"proposedCapacity: {project.renewable.proposedCapacity}")
print(
    f"requiredOffsiteRenewableEnergy: {project.renewable.requiredOffsiteRenewableEnergy}"
)
print(
    f"proposedOffsiteRenewableEnergy: {project.renewable.proposedOffsiteRenewableEnergy}"
)
