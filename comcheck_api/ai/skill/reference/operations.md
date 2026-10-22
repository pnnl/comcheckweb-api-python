# Project Operations Reference

Operation functions are free functions in seven modules:

- `comcheck_api.project_operations.project_building_area_operations`
- `comcheck_api.project_operations.project_envelope_operations`
- `comcheck_api.project_operations.project_interior_lighting_operations`
- `comcheck_api.project_operations.project_exterior_lighting_operations`
- `comcheck_api.project_operations.project_mechanical_operations`
- `comcheck_api.project_operations.project_renewable_operations`
- `comcheck_api.project_operations.project_credit_operations`

Each function takes a `ComBuilding` and a payload, and returns a new
`ComBuilding`. Treat them as immutable transformations.

## Building area operations

```python
from comcheck_api import project_building_area_operations as ba_ops
```

| Function | Purpose |
|---|---|
| `add_building_area_to_project(project, new_building_area)` | Add a `WholeBldgUse` building area to the project. Raises `ValueError` if `areaDescription` already exists. |
| `update_building_area_in_project(project, building_area_key, updates)` | Update fields of an existing building area by key. Raises `ValueError` if the new `areaDescription` collides with another area. |
| `remove_building_area_from_project(project, building_area_key)` | Remove a building area by key. |
| `get_building_area_keys_from_project(project)` | List `[{key, areaDescription}, …]` for the project. |

## Envelope operations

```python
from comcheck_api import project_envelope_operations as env_ops
```

Every envelope `add_*_to_project` call attaches the new component to
a building-area key. Default projects have no areas — add one first:

```python
from comcheck_api.defaults import get_default_building_area_template

area = get_default_building_area_template()  # unique key + areaDescription per call
area.areaDescription = "Open office"  # optional override — must be unique within the project
project = ba_ops.add_building_area_to_project(project, area)  # raises ValueError if areaDescription already exists

area_key = ba_ops.get_building_area_keys_from_project(project)[0]["key"]
```

| Component | Add signature | Update / Remove key |
|---|---|---|
| Roof | `add_roof_to_project(project, building_area_key, new_roof)` | `assemblyType` |
| Above-grade wall | `add_ag_wall_to_project(project, building_area_key, new_ag_wall)` | `assemblyType` |
| Below-grade wall | `add_bg_wall_to_project(project, building_area_key, new_bg_wall)` | `assemblyType` |
| Floor | `add_floor_to_project(project, building_area_key, new_floor)` | `assemblyType` |
| Skylight | `add_skylight_to_project(project, building_area_key, new_skylight, roof=None)` | `assemblyType` |
| Window | `add_window_to_project(project, building_area_key, new_window, wall=None)` | `assemblyType` |
| Door | `add_door_to_project(project, building_area_key, new_door, wall=None)` | `assemblyType` |
| Thermal bridge | `add_thermal_bridge_to_project(project, building_area_key, ag_wall, ...)` | (no update/remove yet) |

The `update_*_in_project` and `remove_*_from_project` functions take
the component's `assemblyType` string, e.g.
`update_ag_wall_in_project(project, ag_wall_assembly_type, updates)`.

## Nesting rules

- Skylights live inside a `Roof`. Pass `roof=` to
  `add_skylight_to_project` to attach to a specific roof; otherwise
  it goes on the first one in the area.
- Windows and doors live inside an above-grade or below-grade wall.
  Pass `wall=` to target a specific wall.
- Thermal bridges always require an `ag_wall=` argument.
- Floors and walls live directly under the building area.

## Working with templates

Always start from `comcheck_api.defaults`:

```python
from comcheck_api.defaults import (
    get_default_project_template,
    get_default_roof_template,
    get_default_ag_wall_template,
    get_default_bg_wall_template,
    get_default_floor_template,
    get_default_window_template,
    get_default_door_template,
    get_default_skylight_template,
    get_default_thermal_bridge_template,
    get_default_building_area_template,
)
```

Each returns a fully-populated Pydantic model with sensible defaults
(Boulder, CO; metal-frame walls; double-pane low-E glazing; etc.).
Customize fields after construction, then attach to a building area:

```python
from comcheck_api.types import OrientationOptions

area_key = ba_ops.get_building_area_keys_from_project(project)[0]["key"]

roof = get_default_roof_template()
roof.grossArea = 6000.0          # field is grossArea, not area
roof.cavityRValue = 38.0
roof.orientation = OrientationOptions.UNSPECIFIED_ORIENTATION
project = env_ops.add_roof_to_project(project, area_key, roof)
```

## Interior lighting operations

```python
from comcheck_api import project_interior_lighting_operations as il_ops
```

Interior lighting spaces are `ActivityUse` objects (aliased as
`InteriorSpace`) nested under `lighting.wholeBldgUse[i].activityUse[]`.
Fixtures are batch-edited via `update_fixtures_in_interior_space`, matched
by `fixtureType` (the schema-documented uniqueness key for fixtures within
a lighting space, not `id`). You can still edit
`interiorSpace.interiorLightingSpace.fixture[]` directly and pass the whole
`InteriorSpace` through `update_interior_space_in_project` if you prefer.

| Function | Purpose |
|---|---|
| `add_interior_space_to_project(project, building_area_key, new_interior_space)` | Add an `InteriorSpace` to a building area. `activityUse.key` is auto-set to `building_area_key`. |
| `update_interior_space_in_project(project, building_area_key, area_description, updates)` | Update an `InteriorSpace` by its `areaDescription`. |
| `update_fixtures_in_interior_space(project, building_area_key, area_description, upserts=[], remove_fixture_types=[])` | Batch add/update/remove fixtures on an `InteriorSpace`, matched by `fixtureType`. Raises `ValueError` on duplicate `fixtureType`s in `upserts` or an unmatched `remove_fixture_types` entry. |
| `remove_interior_space_from_project(project, building_area_key, area_description)` | Remove an `InteriorSpace` by its `areaDescription`. |
| `get_interior_space_keys_from_project(project, building_area_key)` | List `[{areaDescription, activityType}, …]` for a building area. |

Use `get_default_interior_space_template()` as a starting point.
`areaDescription` is the identifier — it is unique within a building area's
`activityUse[]` list and is auto-generated if missing.

Allowed wattage is calculated server-side via two `COMcheckClient` methods,
not an `il_ops` function:

```python
energy_code = str(project.control.code)  # InteriorSpace alone has no control.code

result = client.calculate_interior_space_allowed_wattage(interior_space, energy_code)
# {"spaceAllowedWattage": 560}

results = client.calculate_interior_spaces_allowed_wattage(
    [interior_space, second_interior_space], energy_code
)
# {"Open Office": 560, "Conference Room": 610} — keyed by areaDescription
```

Neither call mutates the `InteriorSpace` objects or writes onto
`allowedWattage` — they return the raw calculation payload.

## Exterior lighting operations

```python
from comcheck_api import project_exterior_lighting_operations as el_ops
```

Exterior lighting areas are `ExteriorUse` objects (aliased as `ExteriorArea`)
in `lighting.exteriorUse[]`. Set a real zone type before exterior compliance
can be evaluated. Fixtures are batch-edited via
`update_fixtures_in_exterior_area`, matched by `fixtureType` (the
schema-documented uniqueness key for fixtures within a lighting space, not
`id`). You can still edit `exteriorArea.exteriorLightingSpace.fixture[]`
directly and pass the whole `ExteriorArea` through
`update_exterior_area_in_project` if you prefer.

| Function | Purpose |
|---|---|
| `set_exterior_lighting_zone_type_in_project(project, zone_type)` | Set `lighting.exteriorLightingZoneType`. Raises `ValueError` for `EXT_ZONE_UNSPECIFIED`, `TypeError` for non-enum values. |
| `add_exterior_area_to_project(project, new_exterior_area)` | Add an `ExteriorArea`. Emits `UserWarning` if zone type is still `EXT_ZONE_UNSPECIFIED`. |
| `update_exterior_area_in_project(project, area_description, updates)` | Update an `ExteriorArea` by its `areaDescription`. |
| `update_fixtures_in_exterior_area(project, area_description, upserts=[], remove_fixture_types=[])` | Batch add/update/remove fixtures on an `ExteriorArea`, matched by `fixtureType`. Raises `ValueError` on duplicate `fixtureType`s in `upserts` or an unmatched `remove_fixture_types` entry. |
| `remove_exterior_area_from_project(project, area_description)` | Remove an `ExteriorArea` by its `areaDescription`. |
| `get_exterior_area_keys_from_project(project)` | List `[{areaDescription, exteriorType}, …]` for the project. |

Use `get_default_exterior_area_template()` as a starting point.
`areaDescription` is the identifier — it is unique within `exteriorUse[]`
and is auto-generated if missing.

## Mechanical operations

```python
from comcheck_api import project_mechanical_operations as mech_ops
```

Mechanical operations manage HVAC systems, fan systems, HVAC plants, and service
water heating. The `hvac` singleton can be `MISSING` and is created automatically
on add. `swhSystem[]` is a top-level list (not under `hvac`).

| Function | Purpose |
|---|---|
| **HVAC systems** (`hvac.hvacSystem[]`) | |
| `add_hvac_system_to_project(project, new_hvac_system)` | Add an `HVACSystem`. Raises `ValueError` if `fanSystemKey` references a non-existent fan system. |
| `update_hvac_system_in_project(project, hvac_system_description, updates)` | Update an `HVACSystem` by its `description`. Raises `ValueError` for engine-calculated fields (`requirementAnswer`) or invalid `fanSystemKey`. |
| `remove_hvac_system_from_project(project, hvac_system_description)` | Remove an `HVACSystem` by its `description`. |
| `assign_fan_system_to_hvac_system(project, hvac_system_description, fan_system_description)` | Assign a fan system to an HVAC system by copying its UUID into `fanSystemKey`. Pass `fan_system_description=None` to unassign. |
| `get_hvac_system_keys_from_project(project)` | List `[{description, systemType, quantity, fanSystemKey, fanSystemDescription}, …]` for the project. |
| **Fan systems** (`hvac.fanSystem[]`) | |
| `add_fan_system_to_project(project, new_fan_system)` | Add a `FanSystem`. The library sets a new UUID on `fanSystemKey` if it's empty or already used. |
| `update_fan_system_in_project(project, fan_system_description, updates)` | Update a `FanSystem` by its `description`. Raises `ValueError` for engine-calculated fields (`complies`, `complianceMessage`, `requirementAnswer`) or `fanSystemKey` changes. |
| `remove_fan_system_from_project(project, fan_system_description)` | Remove a `FanSystem` by its `description`. Also clears `fanSystemKey` on HVAC systems that reference it. |
| `get_fan_system_keys_from_project(project)` | List `[{description, fanSystemKey, complyMethod}, …]` for the project. |
| **Fans** (nested in `FanSystem.fan[]`) | |
| `add_fan_to_fan_system(project, fan_system_description, new_fan)` | Add a `Fan` to a fan system. |
| `update_fan_in_fan_system(project, fan_system_description, fan_description, updates)` | Update a `Fan` by its `description`. |
| `remove_fan_from_fan_system(project, fan_system_description, fan_description)` | Remove a `Fan` by its `description`. |
| `add_pressure_drop_credit_to_fan_system(project, fan_system_description, new_credit)` | Add a `FanSystemPressureDropCredits`. `type` is unique per fan system; `PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED` raises `ValueError`. Warns unless the fan system's `complyMethod` is `FAN_SYSTEM_MOTOR_BRAKE_HP`. |
| `update_pressure_drop_credit_in_fan_system(project, fan_system_description, credit_type, updates)` | Update a credit's inputs by its `type`. Raises `ValueError` for `type` or `pressureDropCredit` changes; changing an input clears `pressureDropCredit` (recalculate with `client.update_fan_pressure_drop_credits`). |
| `remove_pressure_drop_credit_from_fan_system(project, fan_system_description, credit_type)` | Remove a credit by its `type`. |
| **HVAC plants** (`hvac.hvacPlant[]`) | |
| `add_hvac_plant_to_project(project, new_hvac_plant)` | Add an `HVACPlant`. |
| `update_hvac_plant_in_project(project, hvac_plant_description, updates)` | Update an `HVACPlant` by its `description`. Raises `ValueError` for engine-calculated fields (`requirementAnswer`). |
| `remove_hvac_plant_from_project(project, hvac_plant_description)` | Remove an `HVACPlant` by its `description`. |
| `get_hvac_plant_keys_from_project(project)` | List `[{description, plantType, systemType, quantity}, …]` for the project. |
| **Water heaters** (`swhSystem[]`, top-level) | |
| `add_water_heater_to_project(project, new_water_heater)` | Add a `ServiceWaterHeatingSystem`. |
| `update_water_heater_in_project(project, water_heater_description, updates)` | Update a `ServiceWaterHeatingSystem` by its `description`. Raises `ValueError` for engine-calculated fields (`requirementAnswer`). |
| `remove_water_heater_from_project(project, water_heater_description)` | Remove a `ServiceWaterHeatingSystem` by its `description`. |
| `get_water_heater_keys_from_project(project)` | List `[{description, swhSystemType, fuelType, quantity}, …]` for the project. |

Construct `HVACSystem`, `FanSystem`, `Fan`, `HVACPlant`, and
`ServiceWaterHeatingSystem` directly from `comcheck_api.types.core_types`
(all fields are optional). `description` is the
identifier — it is unique within each list and is auto-generated if missing.

**Fan system keys**: the library sets a new UUID on `fanSystemKey` when you add
a fan system if it's empty or already used. You cannot update `fanSystemKey`
directly — use `assign_fan_system_to_hvac_system` or `remove_fan_system_from_project`
(which clears `fanSystemKey` on referencing HVAC systems). Callers use descriptions
and never handle the UUID directly.

## Renewable energy operations

```python
from comcheck_api import project_renewable_operations as rn_ops
```

Renewable energy is managed at the project level through the
`ComBuilding.renewable` singleton. Renewable requirements only apply under
some energy codes; the operations don't check `control.code` — ask the user
whether the project needs renewables. Exception and on-site systems coexist — setting an
exception does not preclude adding renewable systems. **Confirm with the user
before adding off-site procurement** (not always present on projects).

| Function | Purpose |
|---|---|
| `set_renewable_exception_in_project(project, renewable_exception)` | Set `renewable.renewableException`. Raises `ValueError` for `NoneType_None`, `TypeError` for non-enum values. |
| `update_renewable_in_project(project, updates)` | Update scalar fields on the renewable singleton. Raises `ValueError` for engine-calculated, API-calculated, or list fields. |
| `add_renewable_system_to_project(project, new_renewable_system)` | Add an on-site `RenewableSystem`. |
| `update_renewable_system_in_project(project, renewable_system_description, updates)` | Update a `RenewableSystem` by its `description`. |
| `remove_renewable_system_from_project(project, renewable_system_description)` | Remove a `RenewableSystem` by its `description`. |
| `get_renewable_system_keys_from_project(project)` | List `[{description, renewableSystemType, renewableSystemCapacity, renewableSystemCapacityUnit}, …]` for the project. Works for any code. |
| `add_offsite_renewable_procurement_to_project(project, new_procurement)` | Add an `OffsiteRenewableProcurement`. **Confirm with user first.** |
| `update_offsite_renewable_procurement_in_project(project, procurement_description, updates)` | Update an `OffsiteRenewableProcurement` by its `description`. |
| `remove_offsite_renewable_procurement_from_project(project, procurement_description)` | Remove an `OffsiteRenewableProcurement` by its `description`. |
| `get_offsite_renewable_procurement_keys_from_project(project)` | List `[{description, offsiteRenewableProcurementType, offsiteRenewableEnergy}, …]` for the project. Works for any code. |

Use `get_default_renewable_system_template()` and
`get_default_offsite_renewable_procurement_template()` as starting points.
`description` is the identifier — it is unique within each list and is
auto-generated if missing.

## Energy credit operations

```python
from comcheck_api import project_credit_operations as cr_ops
```

Energy credits live in the flat `project.efficiencyPackages` list. Each
`EfficiencyPackage` belongs to a building area (`bldgUseKey` =
`WholeBldgUse.key`) and is identified by its `type`; a building area holds
at most one credit per type. The operations don't check `control.code` —
pick credit types from the enum for the project's code family.

| Function | Notes |
|---|---|
| `add_energy_credit_to_project(project, building_area_key, new_energy_credit)` | Sets `bldgUseKey`. Raises `ValueError` if the building area is missing or already has that credit type. |
| `update_energy_credit_in_project(project, building_area_key, credit_type, updates)` | Revalidates the merged entry. Raises `ValueError` for `type` / `bldgUseKey` updates (remove + add instead). |
| `remove_energy_credit_from_project(project, building_area_key, credit_type)` | Remove one credit. |
| `get_energy_credit_keys_from_project(project, building_area_key=None)` | List `[{bldgUseKey, type}, …]`, optionally for one building area. |
| `set_energy_credit_multiplier_exception_in_project(project, multiplier_exception)` | Set `energyCreditMultiplierException` (IECC 2024 Appendix C/F). Raises `TypeError` for non-enum values. |
| `set_core_and_shell_credit_in_project(project, core_and_shell_credit)` | Set `projectCoreAndShellCredit`; `None` clears it. Raises `ValueError` for negative values. |

`remove_building_area_from_project` also removes the building area's
energy credits. Use `client.calculate_energy_credits(project)` for the
proposed and required credits.

## U-value calculation requires a construction type

When `update_uvalues` (or `start_run_simulation`) recalculates assembly
u-values, the engine needs a valid construction-type field to classify
each assembly — `roofType` for roofs, `wallType` for walls, etc. If it's
missing or null, the engine falls back to an `"Other"` classification,
returns a `propUValue` of `0.0`, and the response comes back with
`assemblyType: "Other"` instead of the value you sent. Because the client
matches results back by `assemblyType`, an `"Other"` result won't match
your assembly and its u-value is silently left unchanged.

The default templates set these fields (e.g. `roofType=ABOVE_DECK_ROOF`),
so this only bites when you build an assembly by hand or clear the type.
Keep the construction-type field populated:

```python
from comcheck_api.types import RoofTypeOptions

roof.roofType = RoofTypeOptions.ABOVE_DECK_ROOF   # don't leave this null
```
