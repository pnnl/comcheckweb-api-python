# Project Operations Reference

Operation functions are free functions in two modules:

- `comcheck_api.project_operations.project_building_area_operations`
- `comcheck_api.project_operations.project_envelope_operations`

Each function takes a `ComBuilding` and a payload, and returns a new
`ComBuilding`. Treat them as immutable transformations.

## Building area operations

```python
from comcheck_api import project_building_area_operations as ba_ops
```

| Function | Purpose |
|---|---|
| `add_building_area_to_project(project, new_building_area)` | Add a `WholeBldgUse` building area to the project. |
| `update_building_area_in_project(project, building_area_key, updates)` | Update fields of an existing building area by key. |
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

area = get_default_building_area_template()
area.areaDescription = "Open office"
project = ba_ops.add_building_area_to_project(project, area)

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
