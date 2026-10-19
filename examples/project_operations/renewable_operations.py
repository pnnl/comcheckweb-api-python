"""Example: renewable energy operations.

Renewable energy is managed at the project level through the
ComBuilding.renewable singleton. The Renewable object carries renewable
exceptions, sizing scalars, on-site renewable systems (renewableSystem[]),
and off-site procurement (offsiteRenewableProcurement[]).

Energy codes
------------
Renewable requirements only apply under some energy codes (and state codes
based on them). These operations don't check ``control.code`` — whether the
project needs renewable data is up to you.

Key concepts
------------
- Exception and systems coexist: setting a renewable exception does not
  preclude adding on-site renewable systems, and vice versa.
- Off-site procurement confirmation: confirm with the user before adding
  off-site renewable procurement (not always present on projects).
"""

import logging
import os
from dotenv import load_dotenv

from comcheck_api import (
    COMcheckClient,
    project_renewable_operations as rn_ops,
)
from comcheck_api.defaults import (
    get_default_renewable_system_template,
    get_default_offsite_renewable_procurement_template,
)
from comcheck_api.types.core_types import (
    RenewableExceptionOptions,
    RenewableSystemTypeOptions,
    RenewableSystemCapacityUnitOptions,
    OffsiteRenewableProcurementType,
)

load_dotenv(override=True)
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY") or "your-api-key-here")

# Fetch an existing project so changes can be saved back to the account.
# (update_project persists to the server; it requires a project that already
# exists there, so we start from a fetched project rather than a local
# template.)
project = client.get_project("your-project-id")
if not project:
    raise ValueError("Project not found")
project_id = str(project.id)


# ── Step 1: Set the renewable exception ───────────────────────────────────────
# A renewable exception can coexist with on-site renewable systems
project = rn_ops.set_renewable_exception_in_project(
    project, RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_NONE
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Renewable exception set: {project.renewable.renewableException}")

# ── Step 2: Add an on-site renewable system ───────────────────────────────────
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

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Renewable system added: {renewable_system.description!r}")

# ── Step 3: List all renewable systems ────────────────────────────────────────
keys = rn_ops.get_renewable_system_keys_from_project(project)
print(f"Renewable systems: {keys}")

# ── Step 4: Update the renewable system (change capacity) ─────────────────────
project = rn_ops.update_renewable_system_in_project(
    project,
    "Rooftop Solar",
    {"renewableSystemCapacity": 75000.0},
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Renewable system capacity updated to 75000.0 W")

# ── Step 5: Add an offsite renewable procurement ──────────────────────────────
# NOTE: Only add offsite procurement if the project actually uses it.
# Confirm with the user before calling this function.
offsite_procurement = get_default_offsite_renewable_procurement_template()
offsite_procurement.description = "Wind PPA"
offsite_procurement.offsiteRenewableProcurementType = (
    OffsiteRenewableProcurementType.OFFSITE_RENEWABLE_PROCUREMENT_PHYSICAL_AGREEMENT
)
offsite_procurement.offsiteRenewableEnergy = 100000.0  # kWh

project = rn_ops.add_offsite_renewable_procurement_to_project(
    project, offsite_procurement
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Offsite procurement added: {offsite_procurement.description!r}")

# ── Step 6: List all offsite renewable procurements ───────────────────────────
offsite_keys = rn_ops.get_offsite_renewable_procurement_keys_from_project(project)
print(f"Offsite renewable procurements: {offsite_keys}")

# ── Step 7: Update a scalar field on the renewable singleton ──────────────────
project = rn_ops.update_renewable_in_project(project, {"numberOfFloors": 5})

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Number of floors updated to 5")

# ── Step 8: Remove the offsite renewable procurement ──────────────────────────
project = rn_ops.remove_offsite_renewable_procurement_from_project(project, "Wind PPA")

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Offsite procurement 'Wind PPA' removed")

# ── Step 9: Remove the on-site renewable system ───────────────────────────────
project = rn_ops.remove_renewable_system_from_project(project, "Rooftop Solar")

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Renewable system 'Rooftop Solar' removed")

# ── Final check ────────────────────────────────────────────────────────────────
renewable_systems = rn_ops.get_renewable_system_keys_from_project(project)
offsite_procurements = rn_ops.get_offsite_renewable_procurement_keys_from_project(
    project
)
print(f"\nFinal renewable systems: {renewable_systems}")
print(f"Final offsite procurements: {offsite_procurements}")
print(f"Renewable exception: {project.renewable.renewableException}")
