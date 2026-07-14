# Exterior Lighting Operations

Exterior lighting is managed at the **`ExteriorUse`** granularity.  Each
`ExteriorUse` lives directly under `lighting.exteriorUse[]` (no parent
building area needed) and carries exactly one singleton
`ExteriorLightingSpace` whose `fixture[]` holds the fixtures.

## Zone type

Exterior compliance requires a real zone type on
`lighting.exteriorLightingZoneType`.  Set it with
`set_exterior_lighting_zone_type_in_project` **before** exterior compliance
can be evaluated.  Adding an `ExteriorUse` while the zone is still
`EXT_ZONE_UNSPECIFIED` emits a `UserWarning` (not an error) so you can build
up a project incrementally.

## Operations

```python
from comcheck_api import project_exterior_lighting_operations as el_ops
```

| Function | Description |
|---|---|
| `set_exterior_lighting_zone_type_in_project(project, zone_type)` | Set the project-level exterior lighting zone type (rejects `EXT_ZONE_UNSPECIFIED`) |
| `add_exterior_lighting_area_to_project(project, new_exterior_lighting_area)` | Add a new ExteriorUse |
| `update_exterior_lighting_area_in_project(project, area_description, updates)` | Update an existing ExteriorUse (including its fixtures) |
| `remove_exterior_lighting_area_from_project(project, area_description)` | Remove an ExteriorUse and its fixtures |
| `get_exterior_lighting_area_keys_from_project(project)` | List all exterior uses in the project |

## Setting the zone type

```python
from comcheck_api import project_exterior_lighting_operations as el_ops
from comcheck_api.types.core_types import ExteriorLightingZoneTypeOptions

project = el_ops.set_exterior_lighting_zone_type_in_project(
    project, ExteriorLightingZoneTypeOptions.EXT_ZONE_NEIGHBORHOOD_BUS_DISTRICT
)
```

`EXT_ZONE_UNSPECIFIED` is rejected with a `ValueError`.  A raw string raises
a `TypeError` — always use the enum.

## Adding an ExteriorUse with fixtures

```python
from comcheck_api.defaults import get_default_exterior_lighting_area_template, get_default_fixture_template
from comcheck_api.types.core_types import ExteriorUseTypeOptions, LightingTypeOptions

fixture = get_default_fixture_template()
fixture.description = "Parking LED"
fixture.lightingType = LightingTypeOptions.LED
fixture.fixtureWattage = 150.0
fixture.quantity = 8

exterior_use = get_default_exterior_lighting_area_template()
exterior_use.areaDescription = "Main Parking Area"
exterior_use.exteriorType = ExteriorUseTypeOptions.EXTERIOR_PARKING_AREA
exterior_use.useQuantity = 5000.0
exterior_use.exteriorLightingSpace = exterior_use.exteriorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = el_ops.add_exterior_lighting_area_to_project(project, exterior_use)
```

## Updating an ExteriorUse

Pass only the fields you want to change — unchanged fields (including
fixtures) are preserved:

```python
project = el_ops.update_exterior_lighting_area_in_project(
    project,
    "Main Parking Area",
    {"useQuantity": 6000.0},
)
```

## Adding a fixture to an existing ExteriorUse

Retrieve the current `exteriorLightingSpace`, append to its `fixture[]`, then
pass it back through `update_exterior_lighting_area_in_project`:

```python
exterior_uses = project.get_by_path("lighting.exteriorUse")
eu = next(e for e in exterior_uses if e.areaDescription == "Main Parking Area")
existing_fixtures = list(eu.exteriorLightingSpace.fixture or [])

new_fixture = get_default_fixture_template()
new_fixture.description = "Entrance LED"
new_fixture.fixtureWattage = 80.0

updated_space = eu.exteriorLightingSpace.model_copy(
    deep=True,
    update={"fixture": existing_fixtures + [new_fixture]},
)
project = el_ops.update_exterior_lighting_area_in_project(
    project,
    "Main Parking Area",
    {"exteriorLightingSpace": updated_space.model_dump(mode="python", exclude_unset=True)},
)
```

## Removing a fixture

Pass `exteriorLightingSpace` with the desired `fixture[]` (omit the fixtures
you want to remove):

```python
project = el_ops.update_exterior_lighting_area_in_project(
    project,
    "Main Parking Area",
    {"exteriorLightingSpace": {"fixture": []}},  # removes all fixtures
)
```

## Removing an ExteriorUse

```python
project = el_ops.remove_exterior_lighting_area_from_project(project, "Main Parking Area")
```

## Listing exterior uses

```python
keys = el_ops.get_exterior_lighting_area_keys_from_project(project)
# [{"areaDescription": "Main Parking Area", "exteriorType": "EXTERIOR_PARKING_AREA"}, ...]
```
