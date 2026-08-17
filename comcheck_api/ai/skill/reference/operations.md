# Project Operations Reference

Operation functions are free functions in four modules:

- `comcheck_api.project_operations.project_building_area_operations`
- `comcheck_api.project_operations.project_envelope_operations`
- `comcheck_api.project_operations.project_interior_lighting_operations`
- `comcheck_api.project_operations.project_exterior_lighting_operations`

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

Interior lighting spaces are `ActivityUse` objects nested under
`lighting.wholeBldgUse[i].activityUse[]`. There are no fixture-level ops —
edit `activityUse.interiorLightingSpace.fixture[]` and pass the whole
`ActivityUse` through `update_interior_lighting_space_in_project`.

| Function | Purpose |
|---|---|
| `add_interior_lighting_space_to_project(project, building_area_key, new_activity_use)` | Add an `ActivityUse` to a building area. `activityUse.key` is auto-set to `building_area_key`. |
| `update_interior_lighting_space_in_project(project, building_area_key, area_description, updates)` | Update an `ActivityUse` by its `areaDescription`. |
| `remove_interior_lighting_space_from_project(project, building_area_key, area_description)` | Remove an `ActivityUse` by its `areaDescription`. |
| `get_interior_lighting_space_keys_from_project(project, building_area_key)` | List `[{areaDescription, activityType}, …]` for a building area. |

Use `get_default_interior_lighting_space_template()` as a starting point.
`areaDescription` is the identifier — it is unique within a building area's
`activityUse[]` list and is auto-generated if missing.

Allowed wattage is calculated server-side via two `COMcheckClient` methods,
not an `il_ops` function:

```python
energy_code = str(project.control.code)  # ActivityUse alone has no control.code

result = client.calculate_activity_use_allowed_wattage(activity_use, energy_code)
# {"spaceAllowedWattage": 560}

results = client.calculate_activity_uses_allowed_wattage(
    [activity_use, second_activity_use], energy_code
)
# {"Open Office": 560, "Conference Room": 610} — keyed by areaDescription
```

Neither call mutates the `ActivityUse` objects or writes onto
`allowedWattage` — they return the raw calculation payload.

## Exterior lighting operations

```python
from comcheck_api import project_exterior_lighting_operations as el_ops
```

Exterior lighting spaces are `ExteriorUse` objects in
`lighting.exteriorUse[]`. Set a real zone type before exterior compliance
can be evaluated. There are no fixture-level ops — edit
`exteriorUse.exteriorLightingSpace.fixture[]` and pass the whole
`ExteriorUse` through `update_exterior_lighting_area_in_project`.

| Function | Purpose |
|---|---|
| `set_exterior_lighting_zone_type_in_project(project, zone_type)` | Set `lighting.exteriorLightingZoneType`. Raises `ValueError` for `EXT_ZONE_UNSPECIFIED`, `TypeError` for non-enum values. |
| `add_exterior_lighting_area_to_project(project, new_exterior_lighting_area)` | Add an `ExteriorUse`. Emits `UserWarning` if zone type is still `EXT_ZONE_UNSPECIFIED`. |
| `update_exterior_lighting_area_in_project(project, area_description, updates)` | Update an `ExteriorUse` by its `areaDescription`. |
| `remove_exterior_lighting_area_from_project(project, area_description)` | Remove an `ExteriorUse` by its `areaDescription`. |
| `get_exterior_lighting_area_keys_from_project(project)` | List `[{areaDescription, exteriorType}, …]` for the project. |

Use `get_default_exterior_lighting_area_template()` as a starting point.
`areaDescription` is the identifier — it is unique within `exteriorUse[]`
and is auto-generated if missing.

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
