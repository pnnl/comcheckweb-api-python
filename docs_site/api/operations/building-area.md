# Building Area Operations

Building areas are stored in `lighting.wholeBldgUse[]`, one `WholeBldgUse`
per area. A building area is the parent of envelope components, interior
lighting spaces, and energy credits, so add one before adding any of those.

```python
from comcheck_api import project_building_area_operations as ba_ops
```

## Key concepts

- **Building areas are identified by `key`.** Update and remove operations
  find a building area by its `key`. Other components point to it through
  `bldgUseKey` (envelope components, energy credits). Interior spaces use
  `key` instead.
- **`areaDescription` must be unique** within `lighting.wholeBldgUse[]`. The
  check is case-sensitive. Adding or renaming an area to a description that's
  already used raises a `ValueError`.
- **Use the default template for new areas.**
  `get_default_building_area_template()` returns an area with a new unique
  `key` and `areaDescription` every time you call it.
- **`interiorLightingSpace` is filled in for you.** If it's `None` when you
  add the area, it's set from the default template.
- **Removing a building area also removes its energy credits**
  (`efficiencyPackages` entries with a matching `bldgUseKey`).

## Operations

| Function | Description |
|---|---|
| `add_building_area_to_project(project, new_building_area)` | Add a new building area |
| `update_building_area_in_project(project, building_area_key, updates)` | Update an existing building area |
| `remove_building_area_from_project(project, building_area_key)` | Remove a building area and its energy credits |
| `get_building_area_keys_from_project(project)` | List the `key` and `areaDescription` of all building areas |

## Adding a building area

```python
from comcheck_api.defaults import get_default_building_area_template
from comcheck_api.types import WholeBuildingTypeOptions

area = get_default_building_area_template()
area.areaDescription = "Office Area"
area.wholeBldgType = WholeBuildingTypeOptions.WHOLE_BUILDING_OFFICE
area.floorArea = 10000.0

project = ba_ops.add_building_area_to_project(project, area)
area_key = area.key
```

## Updating a building area

Pass only the fields you want to change. Fields you don't pass keep their
values:

```python
project = ba_ops.update_building_area_in_project(
    project,
    area_key,
    {"floorArea": 12000.0, "areaDescription": "Office Area - Level 1"},
)
```

Raises `ValueError` if `building_area_key` is not found, or if the new
`areaDescription` already belongs to another building area.

## Removing a building area

```python
project = ba_ops.remove_building_area_from_project(project, area_key)
```

## Listing building areas

```python
keys = ba_ops.get_building_area_keys_from_project(project)
# [{"key": "3f2c...", "areaDescription": "Office Area"}, ...]
```

See `examples/project_operations/building_area_operations.py` for a full walkthrough.

## Related

- [Types Guide — Building Area](../../types-guide.md#building-area) — `WholeBldgUse`, `WholeBuildingTypeOptions`
- [Envelope](envelope.md), [Interior Lighting](interior-lighting.md), [Credits](credits.md) — components that belong to a building area
- [Project Defaults](../defaults.md) — `get_default_building_area_template`
