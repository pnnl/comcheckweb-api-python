# Exterior Lighting Operations

Exterior lighting is managed at the **`ExteriorArea`** granularity. In the
COMcheck API schema, an exterior lighting area is represented by the
`ExteriorUse` model, aliased as `ExteriorArea`. Each `ExteriorArea` lives
directly under `lighting.exteriorUse[]` (no parent building area needed) and
carries exactly one singleton `ExteriorLightingSpace` whose `fixture[]` holds
the fixtures.

## Key concepts

- **Fixtures are batch-edited by `fixtureType`.** Use
  `update_fixtures_in_exterior_area` to add, update, and/or remove fixtures
  on an area in one call — fixtures are matched by `fixtureType` (the
  schema-documented uniqueness key for fixtures within a lighting space),
  not `id`. You can still edit `exteriorLightingSpace.fixture[]` directly
  and pass the whole `ExteriorArea` through `update_exterior_area_in_project`
  if you prefer.

## Zone type

Exterior compliance requires a real zone type on
`lighting.exteriorLightingZoneType`.  Set it with
`set_exterior_lighting_zone_type_in_project` **before** exterior compliance
can be evaluated.  Adding an `ExteriorArea` while the zone is still
`EXT_ZONE_UNSPECIFIED` emits a `UserWarning` (not an error) so you can build
up a project incrementally.

## areaDescription uniqueness

`areaDescription` must be unique within `lighting.exteriorUse[]`. It is the
identifier used by update and remove operations. If missing, a unique value is
auto-generated with the prefix `"Ext Area"`.

## Operations

```python
from comcheck_api import project_exterior_lighting_operations as el_ops
```

| Function | Description |
|---|---|
| `set_exterior_lighting_zone_type_in_project(project, zone_type)` | Set the project-level exterior lighting zone type (rejects `EXT_ZONE_UNSPECIFIED`) |
| `add_exterior_area_to_project(project, new_exterior_area)` | Add a new ExteriorArea |
| `update_exterior_area_in_project(project, area_description, updates)` | Update an existing ExteriorArea (including its fixtures) |
| `update_fixtures_in_exterior_area(project, area_description, upserts=[], remove_fixture_types=[])` | Batch add/update/remove fixtures, matched by `fixtureType` |
| `remove_exterior_area_from_project(project, area_description)` | Remove an ExteriorArea and its fixtures |
| `get_exterior_area_keys_from_project(project)` | List all exterior areas in the project |

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

## Adding an ExteriorArea with fixtures

```python
from comcheck_api.defaults import get_default_exterior_area_template, get_default_fixture_template
from comcheck_api.types.core_types import ExteriorUseTypeOptions

# fixtureType is the required identifier (a description string); lightingType
# is optional and marked for deprecation.
fixture = get_default_fixture_template()
fixture.description = "Parking LED"
fixture.fixtureType = "Parking LED"
fixture.fixtureWattage = 150.0
fixture.quantity = 8

exterior_area = get_default_exterior_area_template()
exterior_area.areaDescription = "Main Parking Area"
exterior_area.exteriorType = ExteriorUseTypeOptions.EXTERIOR_PARKING_AREA
exterior_area.useQuantity = 5000.0
exterior_area.exteriorLightingSpace = exterior_area.exteriorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = el_ops.add_exterior_area_to_project(project, exterior_area)
```

## Updating an ExteriorArea

Pass only the fields you want to change — unchanged fields (including
fixtures) are preserved:

```python
project = el_ops.update_exterior_area_in_project(
    project,
    "Main Parking Area",
    {"useQuantity": 6000.0},
)
```

## Batch adding, updating, and removing fixtures

`update_fixtures_in_exterior_area` matches fixtures by `fixtureType` —
upserts either add a new fixture or replace an existing one with the same
`fixtureType`; `remove_fixture_types` deletes by `fixtureType`. It handles
the read-modify-write of `exteriorLightingSpace.fixture[]` internally, so
there's no need to fetch and merge the existing fixture list by hand:

```python
new_fixture = get_default_fixture_template()
new_fixture.description = "Entrance LED"
new_fixture.fixtureType = "Entrance LED"
new_fixture.fixtureWattage = 80.0

project = el_ops.update_fixtures_in_exterior_area(
    project,
    "Main Parking Area",
    upserts=[new_fixture],
)
```

Update one fixture and remove another in the same call:

```python
updated_fixture = get_default_fixture_template()
updated_fixture.fixtureType = "Parking LED"  # matches an existing fixture
updated_fixture.fixtureWattage = 120.0

project = el_ops.update_fixtures_in_exterior_area(
    project,
    "Main Parking Area",
    upserts=[updated_fixture],
    remove_fixture_types=["Entrance LED"],
)
```

Raises `ValueError` if two upserts share a `fixtureType`, or if a
`remove_fixture_types` entry doesn't match any current fixture.

You can still edit `exteriorLightingSpace.fixture[]` directly and pass the
whole `ExteriorArea` through `update_exterior_area_in_project` — e.g. to
clear all fixtures at once:

```python
project = el_ops.update_exterior_area_in_project(
    project,
    "Main Parking Area",
    {"exteriorLightingSpace": {"fixture": []}},  # removes all fixtures
)
```

## Removing an ExteriorArea

```python
project = el_ops.remove_exterior_area_from_project(project, "Main Parking Area")
```

## Listing exterior areas

```python
keys = el_ops.get_exterior_area_keys_from_project(project)
# [{"areaDescription": "Main Parking Area", "exteriorType": "EXTERIOR_PARKING_AREA"}, ...]
```
