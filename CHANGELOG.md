# Changelog

All notable changes to this project are documented in this file.

## [Unreleased] - targeting 2.0.0

This release tracks a breaking update to the COMcheck Web API schema. **Projects
created or updated with `comcheck-api` < 2.0.0 are not compatible with the current
API** — upgrade with:

```sh
pip install --upgrade comcheck-api
```

### ⚠️ Breaking Changes

- **Enum types restructured.** Nearly every options enum in `comcheck_api.types.core_types`
  (e.g. `WallTypeOptions`, `BgWallTypeOptions`, `FuelTypeOptions`,
  `RequirementAnswerStatus`, and others) changed from `StrEnum` to plain `Enum`,
  and some (`WallTypeOptions`, `FanEfficiencyExceptionTypeOptions`,
  `FanSystemComplianceMethodOptions`, `TrackLightingWattageBasisTypeOptions`) are
  now `RootModel` wrappers around a renamed `*Enum` class. Code comparing these
  values against plain strings, or importing the old enum names directly, will
  need to be updated.
- **`model_dump()` calls in `COMcheckClient` no longer pass `exclude_unset=True`.**
  Methods that send project data to the API (`update_project`, `update_uvalues`,
  `check_UA_compliance`, `check_requirements`, `generate_report`,
  `start_run_simulation`) now always serialize the full model instead of only the
  fields explicitly set. This changes request payload shape for any code relying
  on partial submissions.
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

### Documentation

- Updated `docs_site` (interior/exterior lighting operations pages,
  types-guide), the AI skill (`SKILL.md`, `reference/operations.md`,
  `reference/types.md`), and `examples/` to reflect the renamed
  functions/constants and to document the new batch fixture operations and
  the renamed allowed-wattage methods.

### Migration notes

- If you pin `comcheck-api`, bump the pin to `>=2.0.0` and re-test any code that
  imports enum types from `comcheck_api.types.core_types` or that relies on
  partial (`exclude_unset`) payloads.
- Projects saved with an older client version should be re-fetched and
  re-submitted with 2.0.0+ to pick up the new required lighting fields.
- Update any code calling the renamed interior/exterior lighting operations,
  defaults, or allowed-wattage client/service methods listed above.

## [1.0.7] and earlier

Latest version published on PyPI prior to this release was `1.0.7`. See git
history prior to this file's creation for details on earlier releases.
