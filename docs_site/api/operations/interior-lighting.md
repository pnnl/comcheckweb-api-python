# Interior Lighting Operations

Interior lighting is managed at the **`ActivityUse`** granularity.  Each
`ActivityUse` belongs to a `WholeBldgUse` (building area) and carries exactly
one singleton `InteriorLightingSpace` whose `fixture[]` holds the fixtures.

## Key concepts

- **No fixture-level operations.** To add, change, or remove a fixture, edit
  the `activityUse`'s `interiorLightingSpace.fixture[]` list and pass the whole
  `ActivityUse` through `update_interior_lighting_space_in_project`.
- **ActivityUse.key** is always set to the parent `WholeBldgUse.key` — the
  add operation sets this automatically.
- **`areaDescription` must be unique** within a building area's `activityUse[]`
  list. It is the identifier used by update and remove operations. If missing,
  a unique value is auto-generated with the prefix `"Space"`.
- A building area must exist before adding activity uses — add one with
  `project_building_area_operations.add_building_area_to_project` first.

## Operations

```python
from comcheck_api import project_interior_lighting_operations as il_ops
```

| Function | Description |
|---|---|
| `add_interior_lighting_space_to_project(project, building_area_key, new_interior_lighting_space)` | Add a new ActivityUse to a building area |
| `update_interior_lighting_space_in_project(project, building_area_key, area_description, updates)` | Update an existing ActivityUse (including its fixtures) |
| `remove_interior_lighting_space_from_project(project, building_area_key, area_description)` | Remove an ActivityUse and its fixtures |
| `get_interior_lighting_space_keys_from_project(project, building_area_key)` | List all activity uses in a building area |

## Adding an ActivityUse with fixtures

```python
from comcheck_api import (
    project_building_area_operations as ba_ops,
    project_interior_lighting_operations as il_ops,
)
from comcheck_api.defaults import (
    get_default_building_area_template,
    get_default_interior_lighting_space_template,
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

# Attach the fixture to the activity use before adding
activity_use = get_default_interior_lighting_space_template()
activity_use.areaDescription = "Open Office"
activity_use.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
activity_use.floorArea = 2000.0
activity_use.interiorLightingSpace = activity_use.interiorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = il_ops.add_interior_lighting_space_to_project(project, area_key, activity_use)
```

## Updating an ActivityUse

Pass only the fields you want to change — unchanged fields (including fixtures)
are preserved:

```python
project = il_ops.update_interior_lighting_space_in_project(
    project,
    area_key,
    "Open Office",
    {"floorArea": 2500.0},
)
```

## Adding a fixture to an existing ActivityUse

Retrieve the current `interiorLightingSpace`, append to its `fixture[]`, then
pass it back through `update_interior_lighting_space_in_project`:

```python
whole_use = project.get_by_path("lighting.wholeBldgUse")
ba = next(a for a in whole_use if a.key == area_key)
au = next(au for au in ba.activityUse if au.areaDescription == "Open Office")
existing_fixtures = list(au.interiorLightingSpace.fixture or [])

new_fixture = get_default_fixture_template()
new_fixture.description = "Pendant LED"
new_fixture.fixtureWattage = 35.0

updated_space = au.interiorLightingSpace.model_copy(
    deep=True,
    update={"fixture": existing_fixtures + [new_fixture]},
)
project = il_ops.update_interior_lighting_space_in_project(
    project,
    area_key,
    "Open Office",
    {"interiorLightingSpace": updated_space.model_dump(mode="python")},
)
```

## Removing a fixture

Pass `interiorLightingSpace` with the desired `fixture[]` (simply omit the
fixture you want to remove):

```python
project = il_ops.update_interior_lighting_space_in_project(
    project,
    area_key,
    "Open Office",
    {"interiorLightingSpace": {"fixture": []}},  # removes all fixtures
)
```

## Removing an ActivityUse

```python
project = il_ops.remove_interior_lighting_space_from_project(project, area_key, "Open Office")
```

## Listing activity uses

```python
keys = il_ops.get_interior_lighting_space_keys_from_project(project, area_key)
# [{"areaDescription": "Open Office", "activityType": "ACTIVITY_COMMON_OFFICE_OPEN"}, ...]
```

## Calculating allowed wattage

Allowed wattage is calculated server-side via two `COMcheckClient` methods,
not the `il_ops` free functions above. Both take the energy code as an
explicit string (there's no project to pull `control.code` from) — an
`ActivityUse` alone doesn't carry an energy code:

```python
energy_code = str(project.control.code)

# Single ActivityUse
result = client.calculate_activity_use_allowed_wattage(activity_use, energy_code)
# {"spaceAllowedWattage": 560}

# A list of ActivityUse objects
results = client.calculate_activity_uses_allowed_wattage(
    [activity_use, second_activity_use], energy_code
)
# {"Open Office": 560, "Conference Room": 610} — keyed by areaDescription
```

These calls don't mutate the `ActivityUse` objects passed in or write the
result onto `allowedWattage` — they return the raw calculation payload for
the caller to use as needed.
