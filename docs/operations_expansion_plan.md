# Operations Expansion Plan

Plan for adding `interior_lighting_operations`, `exterior_lighting_operations`, and
`mechanical_operations` (HVAC system, HVAC plant, fan system, SWH) to the project
following the existing patterns in `project_envelope_operations` and
`project_building_area_operations`.

## Existing pattern (recap)

- Each domain is one module of free functions in `comcheck_api/project_operations/`
  taking a `ComBuilding`, returning a deep-copied/modified one.
- The shape is consistent: `add_X_to_project` / `update_X_in_project` /
  `remove_X_from_project`.
- Mutations go through `CustomBaseModel.append_subcomponent` /
  `update_subcomponent_list` / `remove_from_subcomponent_list`, which spin up a
  `DataManager` keyed off `get_model_info(model)` (`identifier`, optional
  `id_prefix`).
- A thin `XListManager(DataManager[T])` per model lives under
  `managers/components/`. Some carry helper methods to add a child component
  (e.g. `AgWallListManager.add_new_door`).
- Defaults live in `constants/*_constants.py`, are deep-copied through
  `defaults.get_default_*_template()` factories.
- Nested locators (skylight in roof, window/door in wall) use an envelope-specific
  `_find_component_location` helper to pick the right parent before mutating.

The new domains have the same structure but with two wrinkles new code has to
handle:

1. **Two-level nesting** — `Fixture` lives inside `interiorLightingSpace.fixture`,
   and that space lives **either** under `wholeBldgUse[i]` **or** under
   `wholeBldgUse[i].activityUse[j]`.
2. **Singleton subcomponents** — `interiorLightingSpace` and
   `exteriorLightingSpace` are objects, not lists, so they only get `update_*`,
   no add/remove.

## Sample-JSON → identifier choices

| Container | Item | Identifier | Prefix |
|---|---|---|---|
| `lighting.wholeBldgUse[].activityUse[]` | `ActivityUse` | `id` | none |
| `…interiorLightingSpace.fixture[]` (both levels) | `Fixture` | `id` | none |
| `lighting.fixtureSchedule[]` | `FixtureSchedule` | `scheduleFixtureKey` (UUID) | none |
| `lighting.exteriorUse[]` | `ExteriorUse` | `id` | none |
| `lighting.exteriorUse[].exteriorLightingSpace.fixture[]` | `Fixture` | `id` | none |
| `hvac.hvacSystem[]` | `HVACSystem` | `id` | none |
| `hvac.hvacPlant[]` | `HVACPlant` | `id` | none |
| `hvac.fanSystem[]` | `FanSystem` | `fanSystemKey` | none |
| `hvac.fanSystem[].fan[]` | `Fan` | `id` | none |
| `swhSystem[]` (top-level) | `ServiceWaterHeatingSystem` | `id` | none |

These have to be added to `MODEL_TO_ID_INFO` in
`managers/data_manager.py:get_model_info`.

## Plan

### 1. Manager classes — `comcheck_api/managers/components/`

Add two subdirectories mirroring `envelope/`:

- `lighting/`
  - `activity_use.py` → `ActivityUseListManager(DataManager[ActivityUse])` with
    helpers `add_new_fixture(activity_use, fixture)`.
  - `exterior_use.py` → `ExteriorUseListManager(DataManager[ExteriorUse])` with
    `add_new_fixture(exterior_use, fixture)`.
  - `fixture.py` → `FixtureListManager(DataManager[Fixture])`.
  - `fixture_schedule.py` →
    `FixtureScheduleListManager(DataManager[FixtureSchedule])`.
- `mechanical/`
  - `hvac_system.py` → `HVACSystemListManager(DataManager[HVACSystem])`.
  - `hvac_plant.py` → `HVACPlantListManager(DataManager[HVACPlant])`.
  - `fan_system.py` → `FanSystemListManager(DataManager[FanSystem])` with
    `add_new_fan(fan_system, fan)`.
  - `fan.py` → `FanListManager(DataManager[Fan])`.
  - `swh_system.py` →
    `SWHSystemListManager(DataManager[ServiceWaterHeatingSystem])`.

### 2. Constants & defaults

- `comcheck_api/constants/lighting_constants.py` — `DEFAULT_FIXTURE`,
  `DEFAULT_FIXTURE_SCHEDULE`, `DEFAULT_INTERIOR_LIGHTING_SPACE` (already
  partially in `building_area_constants`), `DEFAULT_ACTIVITY_USE`,
  `DEFAULT_EXTERIOR_LIGHTING_SPACE`, `DEFAULT_EXTERIOR_USE`.
- `comcheck_api/constants/mechanical_constants.py` — `DEFAULT_HVAC_SYSTEM`,
  `DEFAULT_HVAC_PLANT`, `DEFAULT_FAN_SYSTEM`, `DEFAULT_FAN`, `DEFAULT_SWH_SYSTEM`.
- Extend `comcheck_api/defaults.py` with `get_default_*_template()` for each new
  constant. Replace the stub `get_default_fixture_schedule_template`
  (currently `NotImplementedError`).

### 3. Operation modules — `comcheck_api/project_operations/`

#### `project_interior_lighting_operations.py`

```
add_activity_use_to_project(project, building_area_key, new_activity_use)
update_activity_use_in_project(project, activity_use_id, updates)
remove_activity_use_from_project(project, activity_use_id)

update_interior_lighting_space_in_project(project, building_area_key, updates, activity_use_id=None)
# updates the singleton lighting space at either bldg-area level or inside the named activity

add_fixture_to_project(project, building_area_key, new_fixture, activity_use_id=None)
update_fixture_in_project(project, fixture_id, updates)
remove_fixture_from_project(project, fixture_id)

add_fixture_schedule_to_project(project, new_fixture_schedule)
update_fixture_schedule_in_project(project, schedule_fixture_key, updates)
remove_fixture_schedule_from_project(project, schedule_fixture_key)
```

Needs a `_find_fixture_location(project, fixture_id) -> (whole_idx, activity_idx_or_None)`
helper analogous to `_find_component_location`.

#### `project_exterior_lighting_operations.py`

```
add_exterior_use_to_project(project, new_exterior_use)
update_exterior_use_in_project(project, exterior_use_id, updates)
remove_exterior_use_from_project(project, exterior_use_id)

update_exterior_lighting_space_in_project(project, exterior_use_id, updates)

add_exterior_fixture_to_project(project, exterior_use_id, new_fixture)
update_exterior_fixture_in_project(project, fixture_id, updates)
remove_exterior_fixture_from_project(project, fixture_id)
```

Exterior fixtures are isolated to a single parent (`exteriorUse`), so this can
be simpler than interior.

#### `project_mechanical_operations.py`

```
add_hvac_system_to_project(project, new_hvac_system)
update_hvac_system_in_project(project, hvac_system_id, updates)
remove_hvac_system_from_project(project, hvac_system_id)

add_hvac_plant_to_project(project, new_hvac_plant)
update_hvac_plant_in_project(project, hvac_plant_id, updates)
remove_hvac_plant_from_project(project, hvac_plant_id)

add_fan_system_to_project(project, new_fan_system)
update_fan_system_in_project(project, fan_system_key, updates)
remove_fan_system_from_project(project, fan_system_key)

add_fan_to_project(project, fan_system_key, new_fan)
update_fan_in_project(project, fan_id, updates)
remove_fan_from_project(project, fan_id)

add_swh_system_to_project(project, new_swh_system)
update_swh_system_in_project(project, swh_system_id, updates)
remove_swh_system_from_project(project, swh_system_id)
```

### 4. Registry / wiring

- Update `MODEL_TO_ID_INFO` in `managers/data_manager.py` per the table above.
- Export the new modules from `comcheck_api/project_operations/__init__.py` and
  `comcheck_api/__init__.py`.
- Add a `_require_activity_use(project, activity_use_id)` helper alongside
  `_require_building_area` in `utilities/project_utilities.py` for the
  fixture/lighting-space ops.

### 5. Tests

Following `tests/project_operation_tests/`:

- `test_interior_lighting_operations.py` — uses `run_flat_assembly_lifecycle`
  for `activityUse`, `fixtureSchedule`, `exteriorUse`;
  `run_nested_assembly_lifecycle` for fixtures (whole-bldg level and
  activity-level — needs a doubly-nested variant).
- `test_exterior_lighting_operations.py`.
- `test_mechanical_operations.py` — flat for `hvacSystem`, `hvacPlant`,
  `fanSystem`, `swhSystem`; nested for `fan` inside `fanSystem`.
- Conftest may need a `_get_or_create_activity_use` fixture mirroring
  `building_area_key`.

### 6. Skill / docs

Append the new operations and conventions to
`comcheck_api/ai/skill/reference/operations.md` so the agent skill knows about
them.

## Open questions

1. **Interior fixture scope** — match the envelope pattern (optional
   `activity_use_id=None` ⇒ falls back to building-area-level interior lighting
   space) or always require explicit scope? The envelope skylight/window
   functions use the optional-parent style, so the natural default is to do the
   same.
2. **Singleton lighting spaces** — confirm we expose them only as `update_*`
   (no add/remove), since they're auto-initialized when their parent area/use
   is created.
