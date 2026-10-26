"""Example: mechanical operations.

Mechanical data lives in two places on ComBuilding:

- ``hvac`` — HVAC systems (hvacSystem[]), fan systems (fanSystem[]) with their
  fans and pressure drop credits, and plants (hvacPlant[]). It is created
  automatically when the first item is added.
- ``swhSystem[]`` — water heaters (``ServiceWaterHeatingSystem``), at the top
  level rather than under ``hvac``.

Key concepts
------------
- Every item is identified by its ``description``, which must be unique in its
  list. An empty or duplicate description gets a UI-style name such as
  "HVAC System 1", "Fan System 1", "Plant 1", or "Water Heater 1".
- Fan systems are linked to HVAC systems through ``fanSystemKey``, a UUID the
  library sets. Link them by description with
  ``assign_fan_system_to_hvac_system``; you never handle the UUID.
- Engine-calculated fields (``complies``, ``complianceMessage``,
  ``pressureDropCredit``, ``requirementAnswer``) can't be set through the update
  operations. ``client.update_fan_system_compliance`` and
  ``client.update_fan_pressure_drop_credits`` fill them in.
"""

import os
from dotenv import load_dotenv

from comcheck_api import (
    COMcheckClient,
    project_mechanical_operations as mech_ops,
)
from comcheck_api.defaults import (
    get_default_hvac_system_template,
    get_default_fan_system_template,
    get_default_fan_template,
    get_default_hvac_plant_template,
    get_default_water_heater_template,
)
from comcheck_api.types.core_types import (
    FanSystemComplianceMethodOptions,
    FanSystemPressureDropCredits,
    PlantTypeOptions,
    PressureDropTypeOptions,
    SWHFuelTypeOptions,
    SWHSystemTypeOptions,
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


# ── Step 1: Add an HVAC system ────────────────────────────────────────────────
hvac_system = get_default_hvac_system_template()
hvac_system.description = "Rooftop Unit 1"
hvac_system.quantity = 2
project = mech_ops.add_hvac_system_to_project(project, hvac_system)
print(f"HVAC systems: {mech_ops.get_hvac_system_keys_from_project(project)}")

# ── Step 2: Add a fan system with a fan ───────────────────────────────────────
# fanSystemKey is left empty; the library sets a UUID.
fan_system = get_default_fan_system_template()
fan_system.description = "Supply Fans"
fan_system.complyMethod = FanSystemComplianceMethodOptions.FAN_SYSTEM_MOTOR_BRAKE_HP
project = mech_ops.add_fan_system_to_project(project, fan_system)

fan = get_default_fan_template()
fan.description = "Supply Fan 1"
fan.nameplateHp = 10.0
project = mech_ops.add_fan_to_fan_system(project, "Supply Fans", fan)

# ── Step 3: Add a pressure drop credit to the fan system ──────────────────────
# Credits are identified by type, which is unique within a fan system. They
# apply to fan systems using the brake horsepower method.
MERV_9 = PressureDropTypeOptions.PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12
project = mech_ops.add_pressure_drop_credit_to_fan_system(
    project, "Supply Fans", FanSystemPressureDropCredits(type=MERV_9, cfm=4000.0)
)

# ── Step 4: Link the fan system to the HVAC system ────────────────────────────
project = mech_ops.assign_fan_system_to_hvac_system(
    project, "Rooftop Unit 1", "Supply Fans"
)
print(f"HVAC systems: {mech_ops.get_hvac_system_keys_from_project(project)}")
print(f"Fan systems: {mech_ops.get_fan_system_keys_from_project(project)}")

# ── Step 5: Add a plant and a water heater ────────────────────────────────────
plant = get_default_hvac_plant_template()
plant.description = "Boiler Plant"
plant.plantType = PlantTypeOptions.HEATING_PLANT
project = mech_ops.add_hvac_plant_to_project(project, plant)

water_heater = get_default_water_heater_template()
water_heater.description = "Water Heater 1"
water_heater.swhSystemType = SWHSystemTypeOptions.STORAGE_WATER_HEATER
water_heater.fuelType = SWHFuelTypeOptions.GAS
water_heater.quantity = 1
project = mech_ops.add_water_heater_to_project(project, water_heater)

print(f"Plants: {mech_ops.get_hvac_plant_keys_from_project(project)}")
print(f"Water heaters: {mech_ops.get_water_heater_keys_from_project(project)}")

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("Mechanical systems saved")

# ── Step 6: Fill in engine-calculated fan system values ───────────────────────
# These call the mechanical API with project.control.code and update the
# project's fan system in place.
project = client.update_fan_pressure_drop_credits(project, "Supply Fans")
project = client.update_fan_system_compliance(project, "Supply Fans")
fan_system = project.hvac.fanSystem[0]
print(f"Pressure drop credit: {fan_system.pressureDropCredits[0].pressureDropCredit}")
print(f"Fan system complies: {fan_system.complies} ({fan_system.complianceMessage})")

# ── Step 7: Update items by description ───────────────────────────────────────
project = mech_ops.update_hvac_system_in_project(
    project, "Rooftop Unit 1", {"quantity": 3}
)
project = mech_ops.update_fan_in_fan_system(
    project, "Supply Fans", "Supply Fan 1", {"nameplateHp": 7.5}
)
# Changing a credit input clears its pressureDropCredit; recalculate it.
project = mech_ops.update_pressure_drop_credit_in_fan_system(
    project, "Supply Fans", MERV_9, {"cfm": 5000.0}
)
project = client.update_fan_pressure_drop_credits(project, "Supply Fans")
# Renaming is an update of description; it must stay unique.
project = mech_ops.update_water_heater_in_project(
    project, "Water Heater 1", {"description": "Kitchen Water Heater"}
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("Mechanical systems updated")

# ── Step 8: Remove items ──────────────────────────────────────────────────────
# Removing a fan system also clears fanSystemKey on HVAC systems that used it.
project = mech_ops.remove_fan_system_from_project(project, "Supply Fans")
project = mech_ops.remove_hvac_plant_from_project(project, "Boiler Plant")
project = mech_ops.remove_water_heater_from_project(project, "Kitchen Water Heater")
project = mech_ops.remove_hvac_system_from_project(project, "Rooftop Unit 1")

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")

# ── Final check ────────────────────────────────────────────────────────────────
print(f"\nFinal HVAC systems: {mech_ops.get_hvac_system_keys_from_project(project)}")
print(f"Final fan systems: {mech_ops.get_fan_system_keys_from_project(project)}")
print(f"Final plants: {mech_ops.get_hvac_plant_keys_from_project(project)}")
print(f"Final water heaters: {mech_ops.get_water_heater_keys_from_project(project)}")
