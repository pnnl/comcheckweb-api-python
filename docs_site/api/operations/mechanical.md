# Mechanical Operations

The mechanical operations module manages HVAC systems, fan systems (with their
fans and pressure drop credits), HVAC plants, and water heaters in COMcheck
projects.

```python
from comcheck_api import project_mechanical_operations as mech_ops
```

## Key concepts

- **Where the data lives.** Mechanical data is in two places on `ComBuilding`:
    - **`hvac`** — a singleton (can be `MISSING`) containing `hvacSystem[]`,
      `fanSystem[]` (can be `None`), and `hvacPlant[]`. It is created
      automatically when you add the first HVAC system, fan system, or plant.
    - **`swhSystem[]`** — water heaters (top-level, not under `hvac`).
- **Components are identified by `description`.** HVAC systems, fan systems,
  fans, plants, and water heaters are matched by `description` in update and
  remove operations. If missing, one is auto-generated (e.g., "HVAC System 1",
  "Fan System 1", "Plant 1", "Water Heater 1"). Pressure drop credits are the
  exception — they are identified by `type`.
- **Fans and pressure drop credits belong to a fan system.** Add the fan
  system first, then pass its description to the fan and pressure drop credit
  operations.
- **Fan system keys link fan systems to HVAC systems.**
  `FanSystem.fanSystemKey` is a UUID:
    - The library sets a new UUID when you add a fan system if it's empty or
      already used.
    - You cannot update `fanSystemKey` directly — use
      `assign_fan_system_to_hvac_system`, which copies it into
      `HVACSystem.fanSystemKey`.
    - When a fan system is removed, `fanSystemKey` is cleared on any HVAC
      systems that reference it.
    - Callers use descriptions and never handle the UUID directly.
- **The fan system's compliance method decides which fan inputs matter.**
  `FanSystem.complyMethod` is one of:
    - `FAN_SYSTEM_MOTOR_NAMEPLATE_HP` — enter `nameplateHp` and
      `designBrakeHp` on each fan. Compliance uses the nameplate HP, and each
      fan's maximum nameplate HP is sized from its design brake HP (see
      [Maximum allowable HP](#maximum-allowable-hp)).
    - `FAN_SYSTEM_MOTOR_BRAKE_HP` — enter `designBrakeHp` and `brakeHp`
      (the fan's maximum brake HP, shown as "max. BHP" in the report) on each
      fan. Compliance uses the design brake HP and checks that the motor
      nameplate HP is at least 75% of `brakeHp`. Only this method supports
      pressure drop credits.

    `maxNameplateHp` on fans is calculated by the engine, not entered.
- **Pressure drop credits only count when `hasPressureDropCredits` is set.**
  Set `FanSystem.hasPressureDropCredits` to `HasPressureDropCredits.int_1`
  on a `FAN_SYSTEM_MOTOR_BRAKE_HP` fan system; otherwise its credits are
  ignored.
- **Engine-calculated fields are read-only.** Update operations reject
  `requirementAnswer` on all components, `complies` and `complianceMessage`
  on fan systems, and `pressureDropCredit` on pressure drop credits. Fill
  them in with the
  [client write-back methods](#writing-results-back-to-the-project).
  `maxNameplateHp` on fans is the exception: `update_fan_in_fan_system`
  accepts it, since compliance recalculates it anyway.
- **Changing an input clears the value calculated from it.** Changing a fan's
  `designBrakeHp` clears its `maxNameplateHp`, and changing a pressure drop
  credit's inputs clears its `pressureDropCredit`. Re-run the matching
  write-back method afterwards.

!!! warning "Mechanical requirements"
    Mechanical requirements (`requirementAnswer` on HVAC systems, fan systems,
    plants, and water heaters) are not supported by this package. Save the project,
    then open it on [COMcheck Web](https://comcheck.energycode.pnl.gov/) to fill
    them out.

## Operations

| Function | Description |
|---|---|
| `add_hvac_system_to_project(project, new_hvac_system)` | Add an HVAC system (creates `hvac` if it's `MISSING`) |
| `update_hvac_system_in_project(project, hvac_system_description, updates)` | Update an existing HVAC system |
| `remove_hvac_system_from_project(project, hvac_system_description)` | Remove an HVAC system |
| `assign_fan_system_to_hvac_system(project, hvac_system_description, fan_system_description)` | Link a fan system to an HVAC system (`None` to unlink) |
| `get_hvac_system_keys_from_project(project)` | List all HVAC systems |
| `add_fan_system_to_project(project, new_fan_system)` | Add a fan system (creates `hvac` if it's `MISSING`) |
| `update_fan_system_in_project(project, fan_system_description, updates)` | Update an existing fan system |
| `remove_fan_system_from_project(project, fan_system_description)` | Remove a fan system and unlink it from HVAC systems |
| `get_fan_system_keys_from_project(project)` | List all fan systems |
| `add_fan_to_fan_system(project, fan_system_description, new_fan)` | Add a fan to a fan system |
| `update_fan_in_fan_system(project, fan_system_description, fan_description, updates)` | Update an existing fan |
| `remove_fan_from_fan_system(project, fan_system_description, fan_description)` | Remove a fan |
| `add_pressure_drop_credit_to_fan_system(project, fan_system_description, new_credit)` | Add a pressure drop credit to a fan system |
| `update_pressure_drop_credit_in_fan_system(project, fan_system_description, credit_type, updates)` | Update an existing pressure drop credit |
| `remove_pressure_drop_credit_from_fan_system(project, fan_system_description, credit_type)` | Remove a pressure drop credit |
| `add_hvac_plant_to_project(project, new_hvac_plant)` | Add an HVAC plant (creates `hvac` if it's `MISSING`) |
| `update_hvac_plant_in_project(project, hvac_plant_description, updates)` | Update an existing HVAC plant |
| `remove_hvac_plant_from_project(project, hvac_plant_description)` | Remove an HVAC plant |
| `get_hvac_plant_keys_from_project(project)` | List all HVAC plants |
| `add_water_heater_to_project(project, new_water_heater)` | Add a water heater (initializes `swhSystem` if it's `MISSING`) |
| `update_water_heater_in_project(project, water_heater_description, updates)` | Update an existing water heater |
| `remove_water_heater_from_project(project, water_heater_description)` | Remove a water heater |
| `get_water_heater_keys_from_project(project)` | List all water heaters |

Update operations raise `ValueError` if the component isn't found or the
updates contain read-only fields (see [Key concepts](#key-concepts)).

## Adding an HVAC system and a fan system

Add both, then link them by description:

```python
from comcheck_api.defaults import (
    get_default_hvac_system_template,
    get_default_fan_system_template,
)

hvac_system = get_default_hvac_system_template()
hvac_system.description = "Rooftop Unit 1"
hvac_system.quantity = 2
project = mech_ops.add_hvac_system_to_project(project, hvac_system)

fan_system = get_default_fan_system_template()
fan_system.description = "Supply Fan 1"
project = mech_ops.add_fan_system_to_project(project, fan_system)

project = mech_ops.assign_fan_system_to_hvac_system(
    project, "Rooftop Unit 1", "Supply Fan 1"
)
```

Pass `None` as the fan system description to unlink it.
`add_hvac_system_to_project` and `update_hvac_system_in_project` raise a
`ValueError` if `fanSystemKey` points to a fan system that doesn't exist.

## Adding and updating fans

Fans are stored in `FanSystem.fan[]`. Pass the fan system's description to
every fan operation:

```python
from comcheck_api.defaults import get_default_fan_template

fan = get_default_fan_template()
fan.description = "Fan 1"
project = mech_ops.add_fan_to_fan_system(project, "Supply Fan 1", fan)
```

Changing `designBrakeHp` clears `maxNameplateHp`, so the old value isn't
kept (unless the same update also sets `maxNameplateHp`). Recalculate it with
`client.update_fan_maximum_allowable_hp` (see
[Maximum allowable HP](#maximum-allowable-hp)):

```python
project = mech_ops.update_fan_in_fan_system(
    project, "Supply Fan 1", "Fan 1", {"designBrakeHp": 10.0}
)
project = client.update_fan_maximum_allowable_hp(project, "Supply Fan 1")
```

## Pressure drop credits

Pressure drop credits are stored in `FanSystem.pressureDropCredits[]`. Each
one is identified by its `type` (a `PressureDropTypeOptions` value), which is
unique within a fan system. They only apply to fan systems that use the
`FAN_SYSTEM_MOTOR_BRAKE_HP` compliance method. Adding one to any other fan
system emits a `UserWarning`.

```python
from comcheck_api.types import (
    FanSystemComplianceMethodOptions,
    FanSystemPressureDropCredits,
    HasPressureDropCredits,
    PressureDropTypeOptions,
)

project = mech_ops.update_fan_system_in_project(
    project,
    "Supply Fan 1",
    {
        "complyMethod": FanSystemComplianceMethodOptions.FAN_SYSTEM_MOTOR_BRAKE_HP,
        "hasPressureDropCredits": HasPressureDropCredits.int_1,
    },
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

`type` can't be updated. Remove the credit and add a new one.

The API calculates the credit value, `pressureDropCredit`. Updating a
credit's inputs clears it, so recalculate after you edit credits:

```python
project = client.update_fan_pressure_drop_credits(project, "Supply Fan 1")
project.hvac.fanSystem[0].pressureDropCredits[0].pressureDropCredit  # e.g. 0.12104
```

To get the value of a single credit without changing the project, use
`calculate_fan_pressure_drop_credit` (see [Mechanical calculations](#mechanical-calculations-api)).

## Adding HVAC plants and water heaters

```python
from comcheck_api.defaults import (
    get_default_hvac_plant_template,
    get_default_water_heater_template,
)

plant = get_default_hvac_plant_template()
plant.description = "Chiller 1"
project = mech_ops.add_hvac_plant_to_project(project, plant)

water_heater = get_default_water_heater_template()
water_heater.description = "Water Heater 1"
project = mech_ops.add_water_heater_to_project(project, water_heater)
```

Water heaters are stored in the top-level `swhSystem[]` list, not under
`hvac`. The model class keeps its schema name, `ServiceWaterHeatingSystem`.

## Updating components

Pass only the fields you want to change. Fields you don't pass keep their
values:

```python
project = mech_ops.update_hvac_system_in_project(
    project, "Rooftop Unit 1", {"quantity": 3}
)
project = mech_ops.update_water_heater_in_project(
    project, "Water Heater 1", {"quantity": 2}
)
```

`update_fan_system_in_project` also rejects `fanSystemKey`. Use
`assign_fan_system_to_hvac_system` to link systems instead.

## Removing components

```python
project = mech_ops.remove_fan_from_fan_system(project, "Supply Fan 1", "Fan 1")
project = mech_ops.remove_fan_system_from_project(project, "Supply Fan 1")
project = mech_ops.remove_hvac_system_from_project(project, "Rooftop Unit 1")
project = mech_ops.remove_hvac_plant_from_project(project, "Chiller 1")
project = mech_ops.remove_water_heater_from_project(project, "Water Heater 1")
```

Removing a fan system clears `fanSystemKey` on any HVAC system that
references it.

## Listing components

```python
mech_ops.get_hvac_system_keys_from_project(project)
# [{"description": "...", "systemType": "...", "quantity": ...,
#   "fanSystemKey": "...", "fanSystemDescription": "..."}, ...]

mech_ops.get_fan_system_keys_from_project(project)
# [{"description": "...", "fanSystemKey": "...", "complyMethod": "..."}, ...]

mech_ops.get_hvac_plant_keys_from_project(project)
# [{"description": "...", "plantType": "...", "systemType": "...", "quantity": ...}, ...]

mech_ops.get_water_heater_keys_from_project(project)
# [{"description": "...", "swhSystemType": "...", "fuelType": "...", "quantity": ...}, ...]
```

## Mechanical calculations (API)

`COMcheckClient` calls the mechanical endpoints (`POST /COM/{energyCode}/mechanical/...`)
for efficiency requirements, fan system compliance, and pressure drop credits.
These methods take the components and an energy code; they don't need a saved
project, and they only return results.

| Method | Endpoint | Returns |
|---|---|---|
| `calculate_hvac_system_efficiency(hvac_systems, energy_code, hvac_name=None)` | `hvac-systems/efficiency` | `dict[str, HVACSystemEfficiency]` keyed by description |
| `validate_hvac_system_economizer(hvac_system, energy_code)` | `hvac-systems/economizers-validation` | `EconomizerValidation` |
| `calculate_fan_pressure_drop_credit(credit, energy_code)` | `fan-systems/fan-pressure-credit` | `float` (`pressureDropCredit`) |
| `check_fan_system_compliance(fan_system, energy_code)` | `fan-systems/compliance` | `FanSystemComplianceResult` |
| `calculate_fan_maximum_allowable_hp(fan, energy_code)` | `fan-systems/maximum-allowable-hp` | `float` (`maxNameplateHp`) |
| `calculate_plant_efficiency(plants, energy_code, plant_name=None)` | `plants/efficiency` | `dict[str, PlantEfficiency]` keyed by description |
| `calculate_water_heater_efficiency(water_heaters, energy_code, water_heater_name=None)` | `water-heaters/efficiency` | `dict[str, WaterHeaterEfficiency]` keyed by description |

- The HVAC system, plant, and water heater methods take one component or a list.
  Descriptions in a list must be unique, and the optional `*_name` filter must
  match one of them; otherwise a `ValueError` is raised before the request is sent.
- `validate_hvac_system_economizer` requires a non-empty `description`.
- `calculate_fan_pressure_drop_credit` sends the credit's `type` as the
  `fanPressureCreditType` query parameter; the type must be set and not
  `PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED`.

```python
from comcheck_api import COMcheckClient
from comcheck_api.types import HVACSystem

client = COMcheckClient()
efficiency = client.calculate_hvac_system_efficiency(
    HVACSystem(description="Rooftop Unit 1"), "CEZ_IECC2021"
)
print(efficiency["Rooftop Unit 1"].minCoolingEfficiency)
```

### Maximum allowable HP

Maximum nameplate HP applies to `FAN_SYSTEM_MOTOR_NAMEPLATE_HP` fan systems.
The API sizes the motor from the fan's brake horsepower — about 1.5× below
6 bhp and 1.3× at 6 bhp or more, rounded up to the next standard motor size
(e.g. 3.1 → 5, 13.4 → 20).

- `calculate_fan_maximum_allowable_hp(fan, energy_code)` sends only the fan's
  `designBrakeHp` and `brakeHp` — the endpoint's only inputs, and it uses the
  larger of the two. `designBrakeHp` must be set (otherwise a `ValueError` is
  raised); `brakeHp` is sent as `0` when unset.
- `update_fan_maximum_allowable_hp(project, fan_system_description)` writes
  `maxNameplateHp` onto each fan (see below). For a fan system that uses any
  other compliance method it emits a `UserWarning` and leaves the project
  unchanged.

```python
project = client.update_fan_maximum_allowable_hp(project, "Supply Fan 1")
project.hvac.fanSystem[0].fan[0].maxNameplateHp  # e.g. 5.0
```

### Writing results back to the project

Only fan system and fan results have fields on the project model. These client
methods use `project.control.code`, update the project **in place**, and return
it — call `client.update_project(...)` afterwards to save:

| Method | Writes |
|---|---|
| `update_fan_system_compliance(project, fan_system_description)` | `complies`, `complianceMessage`, `complyMethod`, `hasPressureDropCredits` |
| `update_fan_pressure_drop_credits(project, fan_system_description)` | `pressureDropCredit` on each entry of `pressureDropCredits[]` |
| `update_fan_maximum_allowable_hp(project, fan_system_description)` | `maxNameplateHp` on each fan in `fan[]` that has `designBrakeHp` (fans without it are skipped). `FAN_SYSTEM_MOTOR_NAMEPLATE_HP` fan systems only — others warn and are skipped. |

```python
project = client.update_fan_pressure_drop_credits(project, "Supply Fan 1")
project = client.update_fan_system_compliance(project, "Supply Fan 1")
project = client.update_fan_maximum_allowable_hp(project, "Supply Fan 1")
client.update_project("project-id", project)
```

!!! note "Written-back values are for reference"
    The engine recalculates `complies`, `complianceMessage`,
    `pressureDropCredit`, and `maxNameplateHp` from the fan inputs every time
    — in `check_fan_system_compliance`, in `update_fan_system_compliance`, and
    in the report. Stored values (even wrong ones) don't change the result, so
    writing them back keeps the project in sync with what COMcheck shows; it
    doesn't feed the next calculation. Re-run the write-back methods after
    changing fan inputs so the stored values stay current.

The HVAC system, economizer, plant, and water heater methods only return
results — `HVACSystem`, `HVACPlant`, and `ServiceWaterHeatingSystem` have no
fields for them.

See `examples/project_operations/mechanical_operations.py` and
`examples/client/mechanical.py` for full walkthroughs.

## Related

- [Types Guide — Mechanical](../../types-guide.md#mechanical) — `HVACSystem`, `FanSystem`, `Fan`, `FanSystemPressureDropCredits`, `HVACPlant`, `ServiceWaterHeatingSystem`
- [Project Defaults](../defaults.md) — default templates for every mechanical component
- [COMcheckClient — Mechanical](../client.md#mechanical) — calculation and write-back methods
