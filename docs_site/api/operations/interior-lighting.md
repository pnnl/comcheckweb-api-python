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
from comcheck_api.types.core_types import ActivityTypeOptions, LightingTypeOptions

# A building area must exist first
area = get_default_building_area_template()
project = ba_ops.add_building_area_to_project(project, area)
area_key = area.key

# Build the fixture
fixture = get_default_fixture_template()
fixture.description = "Recessed LED"
fixture.lightingType = LightingTypeOptions.LED
fixture.fixtureWattage = 20.0
fixture.quantity = 10

# Attach the fixture to the activity use before adding
activity_use = get_default_interior_lighting_space_template()
activity_use.areaDescription = "Open Office"
activity_use.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE
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
    {"interiorLightingSpace": updated_space.model_dump(mode="python", exclude_unset=True)},
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
# [{"areaDescription": "Open Office", "activityType": "ACTIVITY_COMMON_OFFICE"}, ...]
```
