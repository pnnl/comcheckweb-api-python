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

Each envelope component has a consistent triplet:
`add_*_to_project`, `update_*_in_project`, `remove_*_from_project`.
Plus the special `add_thermal_bridge_to_project` (no
update/remove yet).

| Component | Add | Update | Remove |
|---|---|---|---|
| Roof | `add_roof_to_project` | `update_roof_in_project` | `remove_roof_from_project` |
| Above-grade wall | `add_ag_wall_to_project` | `update_ag_wall_in_project` | `remove_ag_wall_from_project` |
| Below-grade wall | `add_bg_wall_to_project` | `update_bg_wall_in_project` | `remove_bg_wall_from_project` |
| Floor | `add_floor_to_project` | `update_floor_in_project` | `remove_floor_from_project` |
| Skylight | `add_skylight_to_project` | `update_skylight_in_project` | `remove_skylight_from_project` |
| Window | `add_window_to_project` | `update_window_in_project` | `remove_window_from_project` |
| Door | `add_door_to_project` | `update_door_in_project` | `remove_door_from_project` |
| Thermal bridge | `add_thermal_bridge_to_project` | — | — |

## Nesting rules

- Skylights nest under a `Roof`.
- Windows, doors, thermal bridges nest under an above-grade or
  below-grade wall.
- Floors are top-level.

The `add_*_to_project` functions accept the parent component
identifier (or auto-place under the first matching parent) — see
the existing `examples/project_operations/envelope_operations.py`
for current calling conventions.

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
Customize fields after construction:

```python
roof = get_default_roof_template()
roof.area = 6000.0
roof.cavityRValue = 38.0
project = env_ops.add_roof_to_project(project, roof)
```
