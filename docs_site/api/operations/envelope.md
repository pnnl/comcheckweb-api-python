# Envelope Operations

Envelope components are stored under `ComBuilding.envelope`. Roofs, above-
and below-grade walls, and floors sit in `envelope.roof[]`, `agWall[]`,
`bgWall[]`, and `floor[]`. Windows, doors, skylights, and thermal bridges
are nested inside their parent wall or roof.

```python
from comcheck_api import project_envelope_operations as env_ops
```

## Key concepts

- **Roofs, walls, and floors belong to a building area.** Pass the building
  area's `key` as `building_area_key` when you add one. It's written to the
  component's `bldgUseKey`.
- **Windows and doors go on a wall, and skylights go on a roof.** Pass the
  parent as `wall=` (an `AgWall` or `BgWall`) or `roof=`. A parent is
  required for non-alteration projects, and its `bldgUseKey` must match
  `building_area_key`. In alteration projects (`ProjectTypeOptions.ALTERATION`)
  these components are added without a parent, directly to
  `envelope.window[]`, `envelope.door[]`, or `envelope.skylight[]`.
- **Thermal bridges belong to an above-grade wall.** They can't exist
  without a parent.
- **Components are identified by `assemblyType`.** Update and remove
  operations find a component by its `assemblyType`. If it's missing or
  already used, a unique value is generated (e.g. `"Roof:Roof 1"`,
  `"AgWall:Ext Wall 1"`, `"Window:Window 1"`). Window, door, and skylight
  operations search every wall or roof, so you don't pass the parent.
- **A building area must exist first.** Add one with
  [`add_building_area_to_project`](building-area.md).

## Operations

| Function | Description |
|---|---|
| `add_roof_to_project(project, building_area_key, new_roof)` | Add a roof to a building area |
| `update_roof_in_project(project, roof_assembly_type, updates)` | Update an existing roof |
| `remove_roof_from_project(project, roof_assembly_type)` | Remove a roof |
| `add_ag_wall_to_project(project, building_area_key, new_ag_wall)` | Add an above-grade wall to a building area |
| `update_ag_wall_in_project(project, ag_wall_assembly_type, updates)` | Update an existing above-grade wall |
| `remove_ag_wall_from_project(project, ag_wall_assembly_type)` | Remove an above-grade wall |
| `add_bg_wall_to_project(project, building_area_key, new_bg_wall)` | Add a below-grade wall to a building area |
| `update_bg_wall_in_project(project, bg_wall_assembly_type, updates)` | Update an existing below-grade wall |
| `remove_bg_wall_from_project(project, bg_wall_assembly_type)` | Remove a below-grade wall |
| `add_floor_to_project(project, building_area_key, new_floor)` | Add a floor to a building area |
| `update_floor_in_project(project, floor_assembly_type, updates)` | Update an existing floor |
| `remove_floor_from_project(project, floor_assembly_type)` | Remove a floor |
| `add_window_to_project(project, building_area_key, new_window, wall=None)` | Add a window to a wall |
| `update_window_in_project(project, window_assembly_type, updates)` | Update an existing window |
| `remove_window_from_project(project, window_assembly_type)` | Remove a window |
| `add_door_to_project(project, building_area_key, new_door, wall=None)` | Add a door to a wall |
| `update_door_in_project(project, door_assembly_type, updates)` | Update an existing door |
| `remove_door_from_project(project, door_assembly_type)` | Remove a door |
| `add_skylight_to_project(project, building_area_key, new_skylight, roof=None)` | Add a skylight to a roof |
| `update_skylight_in_project(project, skylight_assembly_type, updates)` | Update an existing skylight |
| `remove_skylight_from_project(project, skylight_assembly_type)` | Remove a skylight |
| `add_thermal_bridge_to_project(project, building_area_key, ag_wall, ...)` | Add a thermal bridge to an above-grade wall |

## Adding roofs, walls, and floors

```python
from comcheck_api.defaults import (
    get_default_roof_template,
    get_default_ag_wall_template,
    get_default_floor_template,
)

area_key = project.lighting.wholeBldgUse[0].key

roof = get_default_roof_template()
roof.assemblyType = "Roof:Main Roof"
project = env_ops.add_roof_to_project(project, area_key, roof)

wall = get_default_ag_wall_template()
wall.assemblyType = "AgWall:North Wall"
project = env_ops.add_ag_wall_to_project(project, area_key, wall)

floor = get_default_floor_template()
project = env_ops.add_floor_to_project(project, area_key, floor)
```

`add_bg_wall_to_project` works the same way with
`get_default_bg_wall_template()`.

## Adding windows, doors, and skylights

Pass the parent component from the project as `wall=` or `roof=`:

```python
from comcheck_api.defaults import (
    get_default_window_template,
    get_default_door_template,
    get_default_skylight_template,
)

north_wall = next(
    w for w in project.envelope.agWall if w.assemblyType == "AgWall:North Wall"
)
main_roof = next(
    r for r in project.envelope.roof if r.assemblyType == "Roof:Main Roof"
)

window = get_default_window_template()
window.assemblyType = "Window:North Window"
project = env_ops.add_window_to_project(project, area_key, window, wall=north_wall)

door = get_default_door_template()
project = env_ops.add_door_to_project(project, area_key, door, wall=north_wall)

skylight = get_default_skylight_template()
project = env_ops.add_skylight_to_project(project, area_key, skylight, roof=main_roof)
```

Raises `ValueError` if the parent is missing in a non-alteration project, or
if its `bldgUseKey` doesn't match `building_area_key`.

## Adding a thermal bridge

`add_thermal_bridge_to_project` takes the thermal bridge inputs as keyword
arguments instead of a model:

```python
from comcheck_api.types import ThermalBridgeTypeOptions

project = env_ops.add_thermal_bridge_to_project(
    project,
    area_key,
    north_wall,
    thermal_bridge_type=ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER,
    psi_factor=0.2,
    thermal_bridge_length=100.0,
)
```

| Argument | Default |
|---|---|
| `thermal_bridge_type` | `ThermalBridgeTypeOptions.THERMAL_BRIDGE_OTHER` |
| `thermal_bridge_category` | `ThermalBridgeCategoryOptions.THERMAL_BRIDGE_UNCATEGORIZED` |
| `thermal_bridge_compliance_type` | `ThermalBridgeComplianceTypeOptions.THERMAL_BRIDGE_NON_PRESCRIPTIVE` |
| `psi_factor`, `chi_factor`, `thermal_bridge_length` | `0.0` |
| `number_of_points` | `0` |

Raises `ValueError` if the wall isn't in the project or its `bldgUseKey`
doesn't match `building_area_key`.

## Updating components

Pass only the fields you want to change. Fields you don't pass keep their
values:

```python
project = env_ops.update_roof_in_project(
    project, "Roof:Main Roof", {"grossArea": 8000.0}
)
project = env_ops.update_window_in_project(
    project, "Window:North Window", {"grossArea": 250.0}
)
```

Window, door, and skylight updates raise `ValueError` if no component with
that `assemblyType` is found.

## Removing components

```python
project = env_ops.remove_window_from_project(project, "Window:North Window")
project = env_ops.remove_ag_wall_from_project(project, "AgWall:North Wall")
```

Removing a wall or roof also removes the windows, doors, skylights, and
thermal bridges on it.

## Calculating U-values (API)

`COMcheckClient.update_uvalues` sends the envelope to the COMcheck Web API.
It writes the calculated U-values back onto the matching `agWall`, `bgWall`,
`roof`, and `floor` components (matched by `assemblyType`). It updates the
project in place and returns it:

```python
project = client.update_uvalues(project)
print(project.envelope.agWall[0].propUValue)
```

See `examples/project_operations/envelope_operations.py` for a full walkthrough.

## Related

- [Types Guide — Envelope Components](../../types-guide.md#envelope-components) — `Roof`, `AgWall`, `BgWall`, `Floor`, `Window`, `Door`, `Skylight`, `ThermalBridge`
- [Building Area](building-area.md) — add the parent building area first
- [Project Defaults](../defaults.md) — default templates for every envelope component
- [COMcheckClient — Envelope](../client.md#envelope) — `update_uvalues`
