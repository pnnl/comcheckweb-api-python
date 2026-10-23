# Mechanical

The mechanical operations module manages HVAC systems, fan systems, HVAC plants, and water heaters in COMcheck projects.

```python
from comcheck_api import project_mechanical_operations as mech_ops
```

## Overview

Mechanical data lives in two places on `ComBuilding`:

- **`hvac`** — a singleton (can be `MISSING`) containing:
  - `hvacSystem[]` — list of HVAC systems
  - `fanSystem[]` — list of fan systems (can be `None`)
  - `hvacPlant[]` — list of HVAC plants
- **`swhSystem[]`** — water heaters (top-level, not under `hvac`)

All four lists are identified by `description`, which is auto-generated if missing (e.g., "HVAC System 1", "Fan System 1", "Plant 1", "Water Heater 1"). The `hvac` singleton is created automatically when you add the first HVAC, fan, or plant component.

See `examples/project_operations/mechanical_operations.py` for a full walkthrough.

## HVAC Systems

HVAC systems are identified by their `description`.

### add_hvac_system_to_project

```python
project = mech_ops.add_hvac_system_to_project(
    project,
    new_hvac_system
)
```

Add a new HVAC system. Creates the `hvac` singleton if it's `MISSING`.

**Parameters:**

- `project` (`ComBuilding`) — The project to modify
- `new_hvac_system` (`HVACSystem`) — The HVAC system to add

**Raises:**

- `ValueError` — If the HVAC system's `fanSystemKey` references a non-existent fan system

**Example:**

```python
from comcheck_api.defaults import get_default_hvac_system_template

hvac_system = get_default_hvac_system_template()
hvac_system.description = "Rooftop Unit 1"
hvac_system.quantity = 2
project = mech_ops.add_hvac_system_to_project(project, hvac_system)
```

### update_hvac_system_in_project

```python
project = mech_ops.update_hvac_system_in_project(
    project,
    hvac_system_description,
    updates
)
```

Update an existing HVAC system. Engine-calculated fields (`requirementAnswer`) are rejected.

**Parameters:**

- `project` (`ComBuilding`) — The project to modify
- `hvac_system_description` (`str`) — The description of the HVAC system to update
- `updates` (`dict | HVACSystem`) — Partial updates (dict) or full HVACSystem

**Raises:**

- `ValueError` — If the HVAC system is not found, updates contain engine-calculated fields, or `fanSystemKey` references a non-existent fan system

### remove_hvac_system_from_project

```python
project = mech_ops.remove_hvac_system_from_project(
    project,
    hvac_system_description
)
```

Remove an HVAC system from the project.

### assign_fan_system_to_hvac_system

```python
project = mech_ops.assign_fan_system_to_hvac_system(
    project,
    hvac_system_description,
    fan_system_description  # or None to unassign
)
```

Assign a fan system to an HVAC system by copying its UUID into `fanSystemKey`. Pass `fan_system_description=None` to unassign the fan system.

**Example:**

```python
project = mech_ops.assign_fan_system_to_hvac_system(
    project, "Rooftop Unit 1", "Supply Fan 1"
)
```

### get_hvac_system_keys_from_project

```python
keys = mech_ops.get_hvac_system_keys_from_project(project)
# Returns: [{"description": "...", "systemType": "...", "quantity": ..., 
#            "fanSystemKey": "...", "fanSystemDescription": "..."}, ...]
```

## Fan Systems

Fan systems are identified by their `description` and linked to HVAC systems via a UUID (`fanSystemKey`).

### add_fan_system_to_project

```python
project = mech_ops.add_fan_system_to_project(
    project,
    new_fan_system
)
```

Add a new fan system. The library sets a new UUID on `fanSystemKey` if it's empty or already used.

**Example:**

```python
from comcheck_api.defaults import get_default_fan_system_template

fan_system = get_default_fan_system_template()
fan_system.description = "Supply Fan 1"
project = mech_ops.add_fan_system_to_project(project, fan_system)
```

### update_fan_system_in_project

```python
project = mech_ops.update_fan_system_in_project(
    project,
    fan_system_description,
    updates
)
```

Update an existing fan system. Engine-calculated fields (`complies`, `complianceMessage`, `requirementAnswer`) and identity fields (`fanSystemKey`) are rejected.

**Raises:**

- `ValueError` — If updates contain disallowed fields. Use `assign_fan_system_to_hvac_system` for linking.

### remove_fan_system_from_project

```python
project = mech_ops.remove_fan_system_from_project(
    project,
    fan_system_description
)
```

Remove a fan system from the project. Also clears `fanSystemKey` on any HVAC systems that reference it.

### get_fan_system_keys_from_project

```python
keys = mech_ops.get_fan_system_keys_from_project(project)
# Returns: [{"description": "...", "fanSystemKey": "...", "complyMethod": "..."}, ...]
```

## Fans

Fans are nested within fan systems (`FanSystem.fan[]`) and identified by their `description`.

### add_fan_to_fan_system

```python
project = mech_ops.add_fan_to_fan_system(
    project,
    fan_system_description,
    new_fan
)
```

Add a new fan to a fan system.

**Example:**

```python
from comcheck_api.defaults import get_default_fan_template

fan = get_default_fan_template()
fan.description = "Fan 1"
project = mech_ops.add_fan_to_fan_system(project, "Supply Fan 1", fan)
```

### update_fan_in_fan_system

```python
project = mech_ops.update_fan_in_fan_system(
    project,
    fan_system_description,
    fan_description,
    updates
)
```

Update an existing fan in a fan system.

### remove_fan_from_fan_system

```python
project = mech_ops.remove_fan_from_fan_system(
    project,
    fan_system_description,
    fan_description
)
```

Remove a fan from a fan system.

## Pressure Drop Credits

Pressure drop credits are nested within fan systems (`FanSystem.pressureDropCredits[]`)
and identified by their `type` (a `PressureDropTypeOptions` value), which is
unique within a fan system. They apply to fan systems that use the
`FAN_SYSTEM_MOTOR_BRAKE_HP` compliance method; adding one to another fan system
emits a `UserWarning`.

`pressureDropCredit` is calculated by the engine. Updating a credit's inputs
clears it; recalculate with `COMcheckClient.update_fan_pressure_drop_credits`
(see [API calls](#api-calls)).

```python
from comcheck_api.types.core_types import (
    FanSystemPressureDropCredits,
    PressureDropTypeOptions,
)

MERV_9 = PressureDropTypeOptions.PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12

project = mech_ops.add_pressure_drop_credit_to_fan_system(
    project, "Supply Fan 1", FanSystemPressureDropCredits(type=MERV_9, cfm=1000)
)
project = mech_ops.update_pressure_drop_credit_in_fan_system(
    project, "Supply Fan 1", MERV_9, {"cfm": 1200}
)
project = mech_ops.remove_pressure_drop_credit_from_fan_system(
    project, "Supply Fan 1", MERV_9
)
```

`type` can't be updated — remove the credit and add a new one.

## HVAC Plants

HVAC plants are identified by their `description`.

### add_hvac_plant_to_project

```python
project = mech_ops.add_hvac_plant_to_project(
    project,
    new_hvac_plant
)
```

Add a new HVAC plant. Creates the `hvac` singleton if it's `MISSING`.

**Example:**

```python
from comcheck_api.defaults import get_default_hvac_plant_template

plant = get_default_hvac_plant_template()
plant.description = "Chiller 1"
project = mech_ops.add_hvac_plant_to_project(project, plant)
```

### update_hvac_plant_in_project

```python
project = mech_ops.update_hvac_plant_in_project(
    project,
    hvac_plant_description,
    updates
)
```

Update an existing HVAC plant. Engine-calculated fields (`requirementAnswer`) are rejected.

### remove_hvac_plant_from_project

```python
project = mech_ops.remove_hvac_plant_from_project(
    project,
    hvac_plant_description
)
```

Remove an HVAC plant from the project.

### get_hvac_plant_keys_from_project

```python
keys = mech_ops.get_hvac_plant_keys_from_project(project)
# Returns: [{"description": "...", "plantType": "...", "systemType": "...", "quantity": ...}, ...]
```

## Water Heaters

Water heaters live in the top-level `swhSystem[]` list (not under `hvac`) and are identified by their `description`. The model class keeps its schema name, `ServiceWaterHeatingSystem`.

### add_water_heater_to_project

```python
project = mech_ops.add_water_heater_to_project(
    project,
    new_water_heater
)
```

Add a new water heater. Initializes `swhSystem` to `[]` if it's `MISSING`.

**Example:**

```python
from comcheck_api.defaults import get_default_water_heater_template

water_heater = get_default_water_heater_template()
water_heater.description = "Water Heater 1"
project = mech_ops.add_water_heater_to_project(project, water_heater)
```

### update_water_heater_in_project

```python
project = mech_ops.update_water_heater_in_project(
    project,
    water_heater_description,
    updates
)
```

Update an existing water heater. Engine-calculated fields (`requirementAnswer`) are rejected.

### remove_water_heater_from_project

```python
project = mech_ops.remove_water_heater_from_project(
    project,
    water_heater_description
)
```

Remove a water heater from the project.

### get_water_heater_keys_from_project

```python
keys = mech_ops.get_water_heater_keys_from_project(project)
# Returns: [{"description": "...", "swhSystemType": "...", "fuelType": "...", "quantity": ...}, ...]
```

## Fan System Keys

`FanSystem.fanSystemKey` is a UUID that links a fan system to an HVAC system:

- The library sets a new UUID when you add a fan system if it's empty or already used
- You cannot update `fanSystemKey` directly — use `assign_fan_system_to_hvac_system`
- When a fan system is removed, `fanSystemKey` is cleared on any HVAC systems that reference it
- Callers use descriptions and never handle the UUID directly

## API calls

`COMcheckClient` calls the mechanical endpoints (`POST /COM/{energyCode}/mechanical/...`)
for efficiency requirements and fan system compliance. These methods take the
components and an energy code; they don't need a saved project.

| Method | Endpoint | Returns |
|---|---|---|
| `calculate_water_heater_efficiency(water_heaters, energy_code, water_heater_name=None)` | `water-heaters/efficiency` | `dict[str, WaterHeaterEfficiency]` keyed by description |
| `calculate_hvac_system_efficiency(hvac_systems, energy_code, hvac_name=None)` | `hvac-systems/efficiency` | `dict[str, HVACSystemEfficiency]` keyed by description |
| `validate_hvac_system_economizer(hvac_system, energy_code)` | `hvac-systems/economizers-validation` | `EconomizerValidation` |
| `calculate_plant_efficiency(plants, energy_code, plant_name=None)` | `plants/efficiency` | `dict[str, PlantEfficiency]` keyed by description |
| `calculate_fan_pressure_drop_credit(credit, energy_code)` | `fan-systems/fan-pressure-credit` | `float` (`pressureDropCredit`) |
| `check_fan_system_compliance(fan_system, energy_code)` | `fan-systems/compliance` | `FanSystemComplianceResult` |
| `calculate_fan_maximum_allowable_hp(fan, energy_code)` | `fan-systems/maximum-allowable-hp` | `float` (`maxNameplateHp`) |

- The water heater, HVAC system, and plant methods take one component or a list.
  Descriptions in a list must be unique, and the optional `*_name` filter must
  match one of them; otherwise a `ValueError` is raised before the request is sent.
- `calculate_fan_pressure_drop_credit` sends the credit's `type` as the
  `fanPressureCreditType` query parameter. The type must be set and not
  `PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED`.
- `validate_hvac_system_economizer` requires a non-empty `description`.

```python
from comcheck_api import COMcheckClient
from comcheck_api.types.core_types import HVACSystem

client = COMcheckClient()
efficiency = client.calculate_hvac_system_efficiency(
    HVACSystem(description="Rooftop Unit 1"), "CEZ_IECC2021"
)
print(efficiency["Rooftop Unit 1"].minCoolingEfficiency)
```

### Writing results back to the project

`complies`, `complianceMessage`, and `pressureDropCredit` are calculated by the
engine, so the update operations reject them. Use these client methods to fill
them in. They use `project.control.code`, update the project in place, and
return it:

- `update_fan_system_compliance(project, fan_system_description)` — writes
  `complies`, `complianceMessage`, `complyMethod`, and `hasPressureDropCredits`.
- `update_fan_pressure_drop_credits(project, fan_system_description)` — writes
  `pressureDropCredit` on each entry of the fan system's `pressureDropCredits[]`.

```python
project = client.update_fan_system_compliance(project, "Supply Fan 1")
```

See `examples/client/mechanical.py` for a full example.

## Related

- [Types Guide](../../types-guide.md) — Import `HVACSystem`, `FanSystem`, `Fan`, `HVACPlant`, `ServiceWaterHeatingSystem`
