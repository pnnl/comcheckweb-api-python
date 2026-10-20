"""Example of adding energy credits and calculating them with the COMcheck API client."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api import project_credit_operations as cr_ops
from comcheck_api.defaults import (
    get_default_project_template,
    get_default_building_area_template,
)
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.types.core_types import (
    EfficiencyPackage,
    EnergyCodeOptions,
    IECC2024EnergyCreditTypeOptions as Credit,
)

# Initialize client
load_dotenv(override=True)
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Build an IECC 2024 project with one building area.
project = get_default_project_template()
project.control.code = EnergyCodeOptions.CEZ_IECC2024

project = project_building_area_operations.add_building_area_to_project(
    project, get_default_building_area_template()
)
building_area_key = str(project.lighting.wholeBldgUse[0].key)

# Example 1: Add energy credits to the building area.
project = cr_ops.add_energy_credit_to_project(
    project,
    building_area_key,
    EfficiencyPackage(type=Credit.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ENHANCED_FENESTRATION),
)
project = cr_ops.add_energy_credit_to_project(
    project,
    building_area_key,
    EfficiencyPackage(
        type=Credit.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_REDUCE_AIR_INFILTRATION,
        airInfiltration=0.25,
        airInfiltrationMeasurementType="AIR_INFILTRATION_MEASUREMENT_75PA",
    ),
)

# Example 2: Update the inputs of a credit.
project = cr_ops.update_energy_credit_in_project(
    project,
    building_area_key,
    Credit.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_REDUCE_AIR_INFILTRATION,
    {"airInfiltration": 0.2},
)
print(cr_ops.get_energy_credit_keys_from_project(project))

# Example 3: Calculate the proposed and required credits (the project is not modified).
result = client.calculate_energy_credits(project)
print(f"Credits - Required: {result.required} Proposed: {result.proposed}")
print(
    "Renewable and Load Management Credits - "
    f"Required: {result.requiredRenewableAndLoadMgmt} "
    f"Proposed: {result.proposedRenewableAndLoadMgmt}"
)
for credit in result.energyCredits:
    print(f"  {credit.creditType}: {credit.value}")
for alert in result.userAlerts:
    print(f"  [{alert.level}] {alert.message}")
print(f"Meets required credits: {result.passes}")
