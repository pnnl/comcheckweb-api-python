# Interior Lighting Operations

Interior lighting is managed at the **`InteriorSpace`** granularity. In the
COMcheck API schema, an interior lighting space is represented by the
`ActivityUse` model, aliased as `InteriorSpace`. Each `InteriorSpace` belongs
to a `WholeBldgUse` (building area) and carries exactly one singleton
`InteriorLightingSpace` whose `fixture[]` holds the fixtures.

## Key concepts

- **Fixtures are batch-edited by `fixtureType`.** Use
  `update_fixtures_in_interior_space` to add, update, and/or remove fixtures
  on a space in one call — fixtures are matched by `fixtureType` (the
  schema-documented uniqueness key for fixtures within a lighting space),
  not `id`. You can still edit `interiorLightingSpace.fixture[]` directly
  and pass the whole `InteriorSpace` through `update_interior_space_in_project`
  if you prefer.
- **InteriorSpace.key** is always set to the parent `WholeBldgUse.key` — the
  add operation sets this automatically.
- **`areaDescription` must be unique** within a building area's `activityUse[]`
  list. It is the identifier used by update and remove operations. If missing,
  a unique value is auto-generated with the prefix `"Space"`.
- A building area must exist before adding interior spaces — add one with
  `project_building_area_operations.add_building_area_to_project` first.

## Operations

```python
from comcheck_api import project_interior_lighting_operations as il_ops
```

| Function | Description |
|---|---|
| `add_interior_space_to_project(project, building_area_key, new_interior_space)` | Add a new InteriorSpace to a building area |
| `update_interior_space_in_project(project, building_area_key, area_description, updates)` | Update an existing InteriorSpace (including its fixtures) |
| `update_fixtures_in_interior_space(project, building_area_key, area_description, upserts=[], remove_fixture_types=[])` | Batch add/update/remove fixtures, matched by `fixtureType` |
| `remove_interior_space_from_project(project, building_area_key, area_description)` | Remove an InteriorSpace and its fixtures |
| `get_interior_space_keys_from_project(project, building_area_key)` | List all interior spaces in a building area |

## Adding an InteriorSpace with fixtures

```python
from comcheck_api import (
    project_building_area_operations as ba_ops,
    project_interior_lighting_operations as il_ops,
)
from comcheck_api.defaults import (
    get_default_building_area_template,
    get_default_interior_space_template,
    get_default_fixture_template,
)
from comcheck_api.types.core_types import ActivityTypeOptions

# A building area must exist first
area = get_default_building_area_template()
project = ba_ops.add_building_area_to_project(project, area)
area_key = area.key

# Build the fixture. fixtureType is the required identifier (a description
# string); lightingType is optional and marked for deprecation.
fixture = get_default_fixture_template()
fixture.description = "Recessed LED"
fixture.fixtureType = "Recessed LED"
fixture.fixtureWattage = 20.0
fixture.quantity = 10

# Attach the fixture to the interior space before adding
interior_space = get_default_interior_space_template()
interior_space.areaDescription = "Open Office"
interior_space.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
interior_space.floorArea = 2000.0
interior_space.interiorLightingSpace = interior_space.interiorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = il_ops.add_interior_space_to_project(project, area_key, interior_space)
```

## Updating an InteriorSpace

Pass only the fields you want to change — unchanged fields (including fixtures)
are preserved:

```python
project = il_ops.update_interior_space_in_project(
    project,
    area_key,
    "Open Office",
    {"floorArea": 2500.0},
)
```

## Batch adding, updating, and removing fixtures

`update_fixtures_in_interior_space` matches fixtures by `fixtureType` —
upserts either add a new fixture or replace an existing one with the same
`fixtureType`; `remove_fixture_types` deletes by `fixtureType`. It handles
the read-modify-write of `interiorLightingSpace.fixture[]` internally, so
there's no need to fetch and merge the existing fixture list by hand:

```python
new_fixture = get_default_fixture_template()
new_fixture.description = "Pendant LED"
new_fixture.fixtureType = "Pendant LED"
new_fixture.fixtureWattage = 35.0

project = il_ops.update_fixtures_in_interior_space(
    project,
    area_key,
    "Open Office",
    upserts=[new_fixture],
)
```

Update one fixture and remove another in the same call:

```python
updated_fixture = get_default_fixture_template()
updated_fixture.description = "Recessed LED"
updated_fixture.fixtureType = "Recessed LED"  # matches an existing fixture
updated_fixture.fixtureWattage = 24.0

project = il_ops.update_fixtures_in_interior_space(
    project,
    area_key,
    "Open Office",
    upserts=[updated_fixture],
    remove_fixture_types=["Pendant LED"],
)
```

Raises `ValueError` if two upserts share a `fixtureType`, or if a
`remove_fixture_types` entry doesn't match any current fixture.

You can still edit `interiorLightingSpace.fixture[]` directly and pass the
whole `InteriorSpace` through `update_interior_space_in_project` — e.g. to
clear all fixtures at once:

```python
project = il_ops.update_interior_space_in_project(
    project,
    area_key,
    "Open Office",
    {"interiorLightingSpace": {"fixture": []}},  # removes all fixtures
)
```

## Removing an InteriorSpace

```python
project = il_ops.remove_interior_space_from_project(project, area_key, "Open Office")
```

## Listing interior spaces

```python
keys = il_ops.get_interior_space_keys_from_project(project, area_key)
# [{"areaDescription": "Open Office", "activityType": "ACTIVITY_COMMON_OFFICE_OPEN"}, ...]
```

## Calculating allowed wattage

Allowed wattage is calculated server-side via two `COMcheckClient` methods,
not the `il_ops` free functions above. Both take the energy code as an
explicit string (there's no project to pull `control.code` from) — an
`InteriorSpace` alone doesn't carry an energy code:

```python
energy_code = str(project.control.code)

# Single InteriorSpace
result = client.calculate_interior_space_allowed_wattage(interior_space, energy_code)
# {"spaceAllowedWattage": 560}

# A list of InteriorSpace objects
results = client.calculate_interior_spaces_allowed_wattage(
    [interior_space, second_interior_space], energy_code
)
# {"Open Office": 560, "Conference Room": 610} — keyed by areaDescription
```

These calls don't mutate the `InteriorSpace` objects passed in or write the
result onto `allowedWattage` — they return the raw calculation payload for
the caller to use as needed.
