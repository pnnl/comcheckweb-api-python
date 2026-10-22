# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- Renewable energy operations module (`project_renewable_operations`) for managing on-site renewable systems and off-site procurement
- `set_renewable_exception_in_project` — set the renewable exception on a project
- `update_renewable_in_project` — update scalar fields on the renewable singleton
- `add_renewable_system_to_project` / `update_renewable_system_in_project` / `remove_renewable_system_from_project` — manage on-site renewable systems
- `get_renewable_system_keys_from_project` — list all renewable systems in a project
- `add_offsite_renewable_procurement_to_project` / `update_offsite_renewable_procurement_in_project` / `remove_offsite_renewable_procurement_from_project` — manage offsite renewable procurement
- `get_offsite_renewable_procurement_keys_from_project` — list all offsite renewable procurements
- `get_default_renewable_system_template` and `get_default_offsite_renewable_procurement_template` default templates
- `COMcheckClient.area_for_renewable` — calculate `largestThreeFloorArea` and `roofAreaForRenewable` via `POST /renewable/area-for-renewable` and write them onto `project.renewable`
- `COMcheckClient.renewable_capacity` — calculate required/proposed renewable capacity and off-site renewable energy via `POST /renewable/renewable-capacity` and write them onto `project.renewable`
- `COMCheckApiService.area_for_renewable` and `COMCheckApiService.renewable_capacity` service methods
- `examples/client/renewable.py` example
- `RenewableSystem` and `OffsiteRenewableProcurement` added to `MODEL_TO_ID_INFO` with auto-generated descriptions
- Mechanical operations module (`project_mechanical_operations`) for managing HVAC systems, fan systems, HVAC plants, and water heaters
- `add_hvac_system_to_project` / `update_hvac_system_in_project` / `remove_hvac_system_from_project` — manage HVAC systems
- `assign_fan_system_to_hvac_system` — assign a fan system to an HVAC system by description (copies the UUID into `fanSystemKey`)
- `get_hvac_system_keys_from_project` — list all HVAC systems with their fan system links
- `add_fan_system_to_project` / `update_fan_system_in_project` / `remove_fan_system_from_project` — manage fan systems
- `get_fan_system_keys_from_project` — list all fan systems
- `add_fan_to_fan_system` / `update_fan_in_fan_system` / `remove_fan_from_fan_system` — manage fans within fan systems
- `add_hvac_plant_to_project` / `update_hvac_plant_in_project` / `remove_hvac_plant_from_project` — manage HVAC plants
- `get_hvac_plant_keys_from_project` — list all HVAC plants
- `add_water_heater_to_project` / `update_water_heater_in_project` / `remove_water_heater_from_project` — manage water heaters
- `get_water_heater_keys_from_project` — list all water heaters
- Automatic `fanSystemKey` UUID generation and validation for fan systems
- `HVACSystemListManager`, `FanSystemListManager`, `HVACPlantListManager`, `WaterHeaterListManager` in `comcheck_api.managers.components.mechanical`
- `HVACSystem`, `FanSystem`, `Fan`, `HVACPlant`, `ServiceWaterHeatingSystem` added to `MODEL_TO_ID_INFO` with auto-generated descriptions ("HVAC System", "Fan System", "Fan", "Plant", "Water Heater")
- Mechanical API calls on `COMcheckClient` (`POST /{energyCode}/mechanical/...`): `calculate_water_heater_efficiency`, `calculate_hvac_system_efficiency`, `validate_hvac_system_economizer`, `calculate_plant_efficiency`, `calculate_fan_pressure_drop_credit`, `check_fan_system_compliance`, `calculate_fan_maximum_allowable_hp`
- `COMcheckClient.update_fan_system_compliance` and `COMcheckClient.update_fan_pressure_drop_credits` — calculate fan system compliance / pressure drop credits and write them onto the project's fan system
- Matching `COMCheckApiService` service methods, and `WaterHeaterEfficiency`, `HVACSystemEfficiency`, `EconomizerValidation`, `PlantEfficiency`, `FanSystemComplianceResult` result types
- `examples/client/mechanical.py` example
- Energy credit operations module (`project_credit_operations`) for managing energy credits (`efficiencyPackages`) per building area
- `add_energy_credit_to_project` / `update_energy_credit_in_project` / `remove_energy_credit_from_project` — manage a building area's energy credits
- `get_energy_credit_keys_from_project` — list the energy credits in a project
- `set_energy_credit_multiplier_exception_in_project` and `set_core_and_shell_credit_in_project` — set the project-level credit fields
- `COMcheckClient.calculate_energy_credits` — calculate proposed and required energy credits via `POST /update-energy-credits`, returning an `EnergyCreditResult`
- `COMCheckApiService.update_energy_credits` service method
- `EnergyCreditResult`, `BuildingAreaCredit`, and `EnergyCreditMessage` response models
- `examples/client/credits.py` example
- Schema: Vermont 2024 credit types (`VT2024EnergyCreditTypeOptions`), all eight `EnergyCreditMultiplierException` values, and the `EfficiencyPackage` inputs read by the IECC 2024 / Vermont 2024 credits (`onSiteRenewableCapacity`, `airInfiltrationMeasurementType`, `demandResponseSignal`, `demandResponseRequired`, `ventilationShiftIncluded`, `sumOfGuestRoomFloorAreaWithKitchens`, `sumOfTotalGuestRoomFloorArea`, `tsprProposed`, `tsprTarget`, `tsprReference`, `tsprMpf`)

### Changed
- `ComBuilding.efficiencyPackages` is now typed `list[EfficiencyPackage]` (was `list[Any]`); the schema used `item` instead of `items`, so entries were never validated
- `remove_building_area_from_project` also removes the building area's energy credits
- `CustomBaseModel._get_normalized_subcomponent_info` now extracts element type from list annotations when `subcomponent_name` is given, fixing type lookup for `hvacSystem`, `fanSystem`, `hvacPlant`, and `swhSystem`
- `CustomBaseModel._get_subcomponent_list` now normalizes `None` to `[]` for optional list fields (e.g., `hvac.fanSystem`)
- Skill validation no longer blocks `hvac` or `swhSystem` — mechanical operations are now fully supported

### Deprecated
- `EfficiencyPackage.renewableCapacity` — use `onSiteRenewableCapacity`. The API still accepts it and copies it to `onSiteRenewableCapacity`.



## [2.1.0] - 2026-10-16

### Added

- **`use_backstop_compliance` option for `generate_report()`.** Set
  `use_backstop_compliance=True` to evaluate the report using envelope backstop
  compliance; the generated PDF then includes an Envelope Backstop Compliance
  Certificate page. Sent to the API as `useBackstopCompliance` and defaults to
  `False`, so existing calls are unchanged.

### Documentation

- Documented the backstop compliance option in the Compliance & Reports page,
  the AI skill references, and `examples/client/compliance_and_report.py`.

## [2.0.1] - 2026-09-18

Reverts the enum renames introduced in 2.0.0. If you updated code to use the
`*OptionsEnum` names or `.root` accessors, those changes must be undone —
upgrading from 2.0.0 is otherwise a drop-in.

### ⚠️ Breaking Changes (relative to 2.0.0)

- **The four `*OptionsEnum` renames are reverted.** `WallTypeOptions`,
  `FanSystemComplianceMethodOptions`, `FanEfficiencyExceptionTypeOptions`, and
  `TrackLightingWattageBasisTypeOptions` are plain enum classes again, and the
  `WallTypeOptionsEnum` / `FanSystemComplianceMethodOptionsEnum` /
  `FanEfficiencyExceptionTypeOptionsEnum` /
  `TrackLightingWattageBasisTypeOptionsEnum` classes no longer exist. Member
  access works directly (`WallTypeOptions.WOOD_FRAME_16_AG_WALL`) and the `.root`
  accessor is gone. No `RootModel` enum wrappers remain.
  - Three are `StrEnum` and compare equal to their string values again:
    `WallTypeOptions` (11 members), `FanEfficiencyExceptionTypeOptions` (16),
    `FanSystemComplianceMethodOptions` (2).
  - `TrackLightingWattageBasisTypeOptions` (7 members) is a plain `Enum`, so it
    does **not** compare equal to plain strings — a `StrEnum` cannot hold the
    `None` member this field still requires (see below).

### Fixed

- **Root cause of the 2.0.0 enum churn.** The renames were never a deliberate
  design change: `core_types.py` is generated by `datamodel-codegen`
  (`tools/generate_core_types.py`), which must wrap an enum in a `RootModel` when
  a schema definition declares `"type": "string"` *and* lists `null` as an enum
  member — a contradictory combination, since a `StrEnum` cannot hold `None`.
  Codegen renamed the enum to `*OptionsEnum` to free the name for the wrapper.
  Exactly four definitions in `comCheck.schema.json` had that combination; all
  four are now fixed at the schema level, so the generated types are clean.
- **Nullability made explicit for `TrackLightingWattageBasisTypeOptions`.** The
  API returns `null` for `trackLightingWattageBasisType` on real projects, so
  removing `null` outright made `get_project()` raise `ValidationError` on
  existing data. The definition now declares `"type": ["string", "null"]` —
  matching `AdvancedControlsAllowanceTypeOptions` — which keeps `null` valid
  without a wrapper.
- Removed the redundant `null` enum member from
  `FanEfficiencyExceptionTypeOptions` (which already has explicit `UNSPECIFIED`
  and `NONE` members), `WallTypeOptions`, and
  `FanSystemComplianceMethodOptions`. These three fields now reject an explicit
  `null`; leaving them unset is still valid and serializes as omitted.

### Migration notes

- Replace `<Name>OptionsEnum.MEMBER` with `<Name>Options.MEMBER`, and drop any
  `.root` access on these four types.
- String comparisons work again for `WallTypeOptions`,
  `FanEfficiencyExceptionTypeOptions`, and `FanSystemComplianceMethodOptions`.
  Keep using `.value` or enum members for
  `TrackLightingWattageBasisTypeOptions`.
- Stop sending an explicit `null` for `wallType`,
  `fanEfficiencyExceptionType`, or `fanSystemComplianceMethod`; omit the field
  instead.

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
  **Superseded in 2.0.1 — these four renames were reverted; prefer upgrading
  straight to 2.0.1 rather than adopting the `*OptionsEnum` names.**
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
- `x-client-version` request header, sent on every API call so the server can
  identify the client version. Resolved from the installed package metadata, and
  falls back to `"unknown"` when running from a source checkout with no installed
  distribution.

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
