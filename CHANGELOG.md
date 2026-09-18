# Changelog

All notable changes to this project are documented in this file.

## [2.0.0] - 2026-09-18

This release tracks a breaking update to the COMcheck Web API schema. **Projects
created or updated with `comcheck-api` < 2.0.0 are not compatible with the current
API** — upgrade with:

```sh
pip install --upgrade comcheck-api
```

### ⚠️ Breaking Changes

- **Enum types restructured.** 26 options enums in `comcheck_api.types.core_types`
  (e.g. `BgWallTypeOptions`, `FuelTypeOptions`, `RequirementAnswerStatus`,
  `OrientationOptions`) changed from `StrEnum` to plain `Enum`, so they no longer
  compare equal to their plain-string values — use `.value` or the enum member
  instead. The remaining ~73 options enums are still `StrEnum` and are unaffected.
  Separately, four enums (`WallTypeOptions`, `FanEfficiencyExceptionTypeOptions`,
  `FanSystemComplianceMethodOptions`, `TrackLightingWattageBasisTypeOptions`) are
  now `RootModel` wrappers around a renamed `*Enum` class (e.g.
  `WallTypeOptionsEnum`); the wrapper holds the member in `.root`, so code that
  used these as enums directly must be updated.
- **Serialization now uses pydantic's `MISSING` sentinel instead of
  `exclude_unset`.** Unset fields in `core_types` models default to
  `MISSING` and `CustomBaseModel` defines a plain `@model_serializer` that drops
  them, so `model_dump()` on its own omits fields that were never set. Two
  consequences:
  - **`exclude_unset=True` is now a no-op** on any `CustomBaseModel`, because a
    plain (`mode="plain"`) serializer bypasses pydantic's field-exclusion logic.
    Code passing `exclude_unset`/`exclude_defaults` to `model_dump()` no longer
    changes the output.
  - Fields with a concrete (non-`MISSING`) default — such as
    `Project.projectTitle`, which defaults to `"New Project"` — are now emitted
    even when never explicitly set, whereas `exclude_unset=True` previously
    dropped them. This changes request payload shape for code that relied on
    partial submissions.
- **Removed `ActivityTypeOptions.ACTIVITY_COMMON_OFFICE`** from the schema and
  generated types. Use `ACTIVITY_COMMON_OFFICE_OPEN` or
  `ACTIVITY_COMMON_OFFICE_ENCLOSED`. Older projects that still carry the removed
  value are preserved verbatim rather than rejected — see `docs/schema.md`.
- **`areaDescription` must now be unique** across `lighting.wholeBldgUse`.
  `add_building_area_to_project()` and `update_building_area_in_project()` raise
  `ValueError` on a duplicate description, where they previously accepted it.
- **New required interior/exterior lighting fields and enums** were added to the
  schema (`comcheck_api/schemas/comCheck.schema.json`), backing the new
  `project_interior_lighting_operations` / `project_exterior_lighting_operations`
  modules. Projects built against the old schema may fail server-side validation
  until re-serialized with this version.
- **Renamed interior/exterior lighting operations and constants** to
  consistently use `InteriorSpace` / `ExteriorArea` terminology instead of
  the schema-generated `ActivityUse` / `ExteriorUse` names (new type aliases
  `comcheck_api.types.common_types.InteriorSpace` and `ExteriorArea` were
  introduced for this):
  - `project_interior_lighting_operations`: `add_interior_lighting_space_to_project()`
    → `add_interior_space_to_project()`, `update_interior_lighting_space_in_project()`
    → `update_interior_space_in_project()`, `remove_interior_lighting_space_from_project()`
    → `remove_interior_space_from_project()`, `get_interior_lighting_space_keys_from_project()`
    → `get_interior_space_keys_from_project()`.
  - `project_exterior_lighting_operations`: `add_exterior_lighting_area_to_project()`
    → `add_exterior_area_to_project()`, `update_exterior_lighting_area_in_project()`
    → `update_exterior_area_in_project()`, `remove_exterior_lighting_area_from_project()`
    → `remove_exterior_area_from_project()`, `get_exterior_lighting_area_keys_from_project()`
    → `get_exterior_area_keys_from_project()`.
  - `comcheck_api.defaults`: `get_default_interior_lighting_space_template()` →
    `get_default_interior_space_template()`, `get_default_exterior_lighting_area_template()`
    → `get_default_exterior_area_template()`.
  - Internal constants `DEFAULT_INTERIOR_LIGHTING_SPACE_AREA` → `DEFAULT_INTERIOR_SPACE_AREA`
    and `DEFAULT_EXTERIOR_LIGHTING_AREA` → `DEFAULT_EXTERIOR_AREA`.
- **Renamed allowed-wattage client/service methods** to match the same
  `InteriorSpace` terminology: `COMcheckClient.calculate_activity_use_allowed_wattage()`
  → `calculate_interior_space_allowed_wattage()`, and
  `calculate_activity_uses_allowed_wattage()` → `calculate_interior_spaces_allowed_wattage()`.
  The matching `COMCheckApiService` methods were renamed from
  `activity_use_allowed_wattage()` / `activity_uses_allowed_wattage()` to
  `interior_space_allowed_wattage()` / `interior_spaces_allowed_wattage()`.
  The underlying HTTP endpoints (`/{energy_code}/activity-use/allowed-wattage`,
  `/{energy_code}/activity-uses/allowed-wattage`) are unchanged.

### Added

- Interior lighting allowed-wattage calculation:
  `COMcheckClient.calculate_interior_space_allowed_wattage()` and
  `calculate_interior_spaces_allowed_wattage()`, backed by new
  `/{energy_code}/activity-use/allowed-wattage` and
  `/{energy_code}/activity-uses/allowed-wattage` API endpoints.
- `project_exterior_lighting_operations` and `project_interior_lighting_operations`
  modules for building up lighting sections of a project.
- `update_fixtures_in_interior_space()` and `update_fixtures_in_exterior_area()`
  for batch adding, updating, and removing fixtures on a lighting space in one
  call, matched by `fixtureType` (the schema-documented uniqueness key for
  fixtures within a lighting space, not `id`). Raises `ValueError` on
  duplicate `fixtureType`s within a batch or an unmatched removal.
- New energy code options (`CEZ_IECC2009`, `CEZ_IECC2012`, `CEZ_IECC2024_APPXCF`,
  `CEZ_90_1_2007`, `CEZ_90_1_2010`, `NONE`).
- `docs/schema.md`, documenting the schema and how unknown/removed enum values
  from older projects are handled.

### Documentation

- Updated `docs_site` (interior/exterior lighting operations pages,
  types-guide), the AI skill (`SKILL.md`, `reference/operations.md`,
  `reference/types.md`), and `examples/` to reflect the renamed
  functions/constants and to document the new batch fixture operations and
  the renamed allowed-wattage methods.

### Migration notes

- If you pin `comcheck-api`, bump the pin to `>=2.0.0` and re-test any code that
  imports enum types from `comcheck_api.types.core_types` or that relies on
  partial (`exclude_unset`) payloads. Note that `exclude_unset=True` is now
  ignored — if you need to suppress a field, leave it unset so it stays `MISSING`
  rather than assigning `None`.
- Requires `pydantic>=2.12.5` for the `MISSING` sentinel
  (`pydantic.experimental.missing_sentinel`). This is an experimental pydantic
  API; if it is unavailable the serializer falls back to emitting all fields.
- Projects saved with an older client version should be re-fetched and
  re-submitted with 2.0.0+ to pick up the new required lighting fields.
- Update any code calling the renamed interior/exterior lighting operations,
  defaults, or allowed-wattage client/service methods listed above.
- Replace `ACTIVITY_COMMON_OFFICE` with `ACTIVITY_COMMON_OFFICE_OPEN` or
  `ACTIVITY_COMMON_OFFICE_ENCLOSED`, and ensure each building area has a unique
  `areaDescription`.

## [1.0.7] and earlier

Latest version published on PyPI prior to this release was `1.0.7`. See git
history prior to this file's creation for details on earlier releases.
