# Schema Reference

This document covers three related topics:

1. **Runtime compatibility** — known gaps between the server's actual behavior and the generated models, and how they are handled automatically.
2. **Authoring guidelines** — lessons learned when modifying `comCheck.schema.json` or re-running Pydantic model generation.
3. **Changelog** — every meaningful change introduced in the schema update merged via PR #25.

---

## Background: `MISSING` Sentinel

Many fields in the generated models use `MISSING` (from `pydantic.experimental.missing_sentinel`) as a default instead of `None`. A field with `= MISSING` means:

- **On parse:** the server did not include this field — the model holds `MISSING` rather than failing validation.
- **On serialize:** `model_dump(mode='json')` omits the key entirely — the server does not receive it.

This is the intentional "sparse update" pattern: only fields the server actually sent are round-tripped back. Issues arise when the server *requires* a field on write but omits it on read, or when `MISSING` leaks into the JSON payload.

---

## Part 1: Runtime Compatibility

The `comcheck_api` library bridges between the Python Pydantic models in `core_types.py` (generated from `comCheck.schema.json`) and the live COMcheck backend API. Because the server may return data that predates or diverges from the current schema, `CustomBaseModel` contains several sanitization layers that run automatically on every parse and serialize cycle.

### Issue 1 — `deepcopy` fails on models with `MISSING` fields

**Symptom:** `TypeError: Cannot pickle 'Sentinel' object` when calling `copy.deepcopy()` or `model.model_copy(deep=True)`.

**Root cause:** `MISSING` is a `typing_extensions.Sentinel` that is not picklable. Pydantic's `__deepcopy__` internally uses pickle for nested objects.

**Fix:** `CustomBaseModel.__deepcopy__` copies fields one-by-one, passing `MISSING` through unchanged rather than attempting to deep-copy it.

---

### Issue 2 — Boolean flags serialized as integers

**Symptom:** `HTTP 400: 'instance.isHistoricBuilding' is not of a type(s) boolean`

**Root cause:** The generated schema models boolean flags as `IntEnum` with values `{0, 1}` (e.g. `IsHistoricBuilding`, `CirculationPump`, `HeatTraceTapeInstalled`, `CombinedSystem`, `PoolSystem`). `model_dump(mode='json')` serializes them as integers; the server's JSON Schema validator requires `true`/`false`.

**Affected fields:** `isHistoricBuilding`, `allElectric`, `isRenewable`, `hasBattery`, `hasCharger`, `hasHeatPump`

**Fix:** `CustomBaseModel.model_dump` runs both a `mode='python'` and `mode='json'` dump, then walks them in parallel. Wherever the Python value is an `IntEnum` instance, the corresponding JSON integer is replaced with `bool(value)`.

---

### Issue 3 — Unknown enum values crash on parse

**Symptom:** `ValidationError: Input should be 'ACTIVITY_INVALID_USE', 'ACTIVITY_AUTO_REPAIR', ... [type=enum]` for a value like `'ACTIVITY_COMMON_OFFICE'`.

**Root cause:** Projects created under older schema versions may reference enum values that have since been renamed or removed (e.g. `ACTIVITY_COMMON_OFFICE` → `ACTIVITY_COMMON_OFFICE_OPEN`). The server stores these values verbatim and returns them unchanged.

**Fix — two-validator approach:**

Pydantic runs validators in order: `wrap` → `before` → field validation → `after`. This ordering is used to preserve the original value while still satisfying Pydantic's type checker:

1. **`_preserve_invalid_enum_strings` (`mode='wrap'`)** runs first. It inspects the raw input dict and stashes any string values that are not valid members of their declared `StrEnum` type.
2. **`_sanitize_server_data` (`mode='before'`)** runs next (inside the `handler` call). It replaces the unknown string with the first valid enum member so Pydantic can construct the model without raising a `ValidationError`.
3. After `handler()` returns the constructed model object, `_preserve_invalid_enum_strings` writes the original (unknown) string back onto the field using `object.__setattr__`, bypassing field validation entirely.

The result: the model field holds exactly what the server sent. `model_dump(mode='json')` serializes it as-is, so the value round-trips back to the server unchanged. A `WARNING` is still logged so the drift is visible.

```python
# Server returns an old enum value
project = client.get_project("project-id")
area = project.lighting.wholeBldgUse[0].activityUse[0]

print(area.activityType)  # 'ACTIVITY_COMMON_OFFICE'  ← original value preserved
print(type(area.activityType))  # <class 'str'>  ← not an enum member
```

> **Schema action needed:** When the backend migrates old records to use current enum values, this fallback will no longer be triggered.

---

### Issue 4 — Pydantic serializer `UserWarning` spam

**Symptom:** Dozens of `PydanticSerializationUnexpectedValue: Expected 'MISSING' sentinel` warnings on every `model_dump` call.

**Root cause:** Pydantic's Rust serializer is compiled with the full field schema. When a model instance has `MISSING`-valued fields in `__dict__`, it sees a field count mismatch and warns.

**Fix:** `CustomBaseModel` defines a `model_serializer(mode='plain')` that filters out any `MISSING`-valued entries before the Rust serializer sees them. The serialization output is identical — MISSING fields were already excluded — but the warning is eliminated.

---

### Issue 5 — Server sends negative sentinels for unset numeric fields

**Symptom:** `HTTP 400: 'instance.envelope.roof[1].continuousRValue' must be greater than or equal to 0`

**Root cause:** The server uses `-1` (and similar negative values like `-4.545`) as a "not set" sentinel on fields like `continuousRValue`, `propUValue`, `cavityRValue`. The server enforces `>= 0` on write but does not enforce it on read.

**Fix:** `CustomBaseModel._sanitize_server_data` replaces any incoming negative number with the field's declared `default` value, when that default is `>= 0`. A warning is logged.

**Schema fix applied:** Added `"minimum": 0.0` to the following fields in `comCheck.schema.json` where it was missing:

| Definition | Fields updated |
|---|---|
| `AboveGradeWall` (all 3 definitions) | `cavityRValue`, `continuousRValue`, `propUValue`, `grossArea` |
| `BelowGradeWall` | `cavityRValue`, `continuousRValue` |
| `Window` | `cavityRValue`, `continuousRValue` |
| `Door` | `cavityRValue`, `continuousRValue` |
| `Skylight` | `cavityRValue`, `continuousRValue` |
| `Roof` (second definition) | `cavityRValue`, `continuousRValue`, `propUValue` |

---

### Issue 6 — `MISSING` fields included in outbound JSON payload

**Symptom:** `HTTP 400: 'instance.lighting.wholeBldgUse[0].allowedWattage' is not of a type(s) number`

**Root cause:** `MISSING` fields — those the server never sent — were being included in `model_dump(mode='json')` output as unexpected non-typed values (not `null`, not a number). The server's JSON Schema validator rejected them.

**Fix:** The `model_dump` post-processing step (which already diffs Python vs JSON output for Issue 2) now also drops any key whose Python-side value is `MISSING`. The field is simply omitted from the outbound payload.

---

### Issue 7 — `allowanceType` absent on GET, required on PUT

**Symptom:** `ValidationError: Field required [type=missing]` on parse, then `HTTP 400: requires property "allowanceType"` on PUT.

**Root cause:** The server omits `allowanceType` for older envelope records (sends `null` or omits the key entirely), but its write validator requires the field to be present with a valid string value. The field type is `EnvelopeAssemblyAllowanceTypeOptions | MISSING`.

**Affected components:** `AgWall`, `BgWall`, `Window`, `Door`, `Skylight`, `Roof`

**Fix — inbound (parse):** `_sanitize_server_data` maps an incoming `null` for a non-nullable enum field to the first non-null enum member. For `EnvelopeAssemblyAllowanceTypeOptions`, this is `ENV_ALLOWANCE_NONE`.

**Fix — schema:** Removed `allowanceType` from the `required` arrays of all six component definitions in `comCheck.schema.json`. The field remains defined in `properties` — it is optional on read, required on write (enforced by the server).

> **Note:** This is a server-side inconsistency. The long-term fix is for the server to always populate `allowanceType` when returning records, and for the schema to reflect that it is always present. Once the server is updated, the `required` entries can be restored.

---

### Issue 8 — `null` values dropped for non-optional enum fields

**Symptom:** Fields like `adjacentSpaceType`, `exemptionType` (typed as `SomeEnum`, not `SomeEnum | None`) arrive as `null` from the server, causing the Pydantic model to lose them.

**Root cause:** The server sends `null` for fields it considers "not set" even when the generated schema does not allow `null`. The `_sanitize_server_data` validator was dropping these fields (reverting to `MISSING`), which then caused serialization failures or missing required fields on write.

**Fix:** When the field has an enum with a `None`-valued member (`NoneType_None = None`), the incoming `null` is mapped to that enum member rather than dropped. When no such member exists, the field is dropped and a warning is logged.

---

### Logging

All sanitization actions emit `WARNING`-level log messages via `comcheck_api.types.custom_base_model`. To see them:

```python
import logging
logging.basicConfig(level=logging.WARNING)
```

Example output:
```
WARNING  comcheck_api.types.custom_base_model:custom_base_model.py:142
  Replacing unknown enum value 'ACTIVITY_COMMON_OFFICE' with fallback 'ACTIVITY_INVALID_USE'
  for field ActivityUse.activityType

WARNING  comcheck_api.types.custom_base_model:custom_base_model.py:160
  Replacing server sentinel -1 with default 0.0 for field Roof.continuousRValue
```

---

## Part 2: Schema Authoring Guidelines

Takeaways from the most recent round of changes to `comcheck_api/schemas/comCheck.schema.json` and the Pydantic model generation.

### 1. Use `--use-missing-sentinel` for optional fields

Passing `--use-missing-sentinel` to the generator lets fields be marked with a `MISSING` identifier instead of defaulting to a JSON value. When the model is exported back to JSON, `MISSING` fields are omitted entirely.

**Why it matters:** we were hitting problems where fields that weren't present in the original export would default to values we didn't want. The sentinel avoids inventing data — absent stays absent on round-trip.

### 2. Avoid adding redundant `NONE` to enumerations

Adding `NONE` to enums caused a lot of churn, and in many cases an option that already means "none" existed. Example: `SlabInsulationPositionOptions` already has `NO_INSULATION` **and** `NONE`.

**Action:** before adding `NONE`, check whether the enum already has an equivalent member and reuse it rather than introducing a duplicate.

### 3. Allow `null` as a valid type for many fields

A lot of values arrive as `null` and should *not* be coerced to a default. To handle this correctly we had to explicitly allow `null` as a type for many fields in the JSON schema.

### 4. Exemption types and activity types are likely incomplete

A number of exemption types and activity types were added in PR #25, but coverage may not be complete.

**Action:** cross-reference the enumeration directly in the backend code to confirm all valid exemption/activity types are represented.

### 5. Put `null` inside the enumeration instead of `anyOf: [enum, null]`

Rather than repeating `anyOf: [enumeration, null]` across many fields, add `null` directly to the enumeration itself. This avoids repetition and is simpler to write.

**Note:** when the enum carries the type, you can also drop the `type` keyword on the field — the type is inferred from the enumeration.

### 6. Reconsider `minimum` constraints

`minimum` flags caused failures — e.g. a building with `preAltPropUval` less than 0 failed schema validation and couldn't be loaded into the `ComBuilding` object.

**Open question:** do we actually need `minimum` in the schema? It isn't necessarily enforced by the backend, and its main effect right now is blocking otherwise-valid projects from loading. Consider removing these unless the constraint is genuinely required.

### 7. Drop non-informative descriptions; prefer `title`

Many `description` fields just restate the field name and add nothing.

**Action:** remove descriptions that don't add information. If the text is just a formatted version of the field name, use the `title` keyword instead of `description`.

---

## Part 3: Changelog — PR #25

Every meaningful change introduced in the schema update merged via PR #25. Changes are grouped by category.

---

### 1. Field Additions

#### `ComBuilding`

| Field | Type | Notes |
|---|---|---|
| `bldgUseType` | `$ref BuildingUseTypeOptions` | Legacy alias for `buildingUseType`. Comment: "Legacy enum, only ACTIVITY is valid in the new ComCheck Web." |
| `efficiencyPackageType` | `enum` (string or `null`) | New field. Values: `EFF_PACKAGE_UNKNOWN`, `EFF_PACKAGE_HVAC_PERFORMANCE`, `EFF_PACKAGE_LIGHTING_REDUCED_LPD`, `EFF_PACKAGE_REDUCED_AIR_INFILTRATION`, `EFF_PACKAGE_ENHANCED_ENVELOPE_PERFORMANCE`, `EFF_PACKAGE_ENHANCED_LIGHTING_CONTROLS`, `EFF_PACKAGE_ONSITE_RENEWABLES`, `null`. Default: `null`. |
| `energyCreditMultiplierException` | `enum` (or `null`) | New field. Values: `NO_ENERGY_CREDIT_MULTIPLIER_EXCEPTION`, `ENERGY_CREDIT_MULTIPLIER_EXCEPTION_LOW_ENERGY_BUILDINGS`, `ENERGY_CREDIT_MULTIPLIER_EXCEPTION_PRIMARY_HEAT_PUMP`, `null`. No default declared. |

#### `Door` (fenestration)

| Field | Type | Notes |
|---|---|---|
| `feetAg` | `["number", "null"]` | New field: feet above grade. `minimum: 0.0`, `default: null`. |

#### `Skylight`

| Field | Type | Notes |
|---|---|---|
| `cavityRValue` | `["number", "null"]` | New field: average insulation R-value in cavity. Unit: `h-ft2-F/Btu`, `default: 0.0`. |
| `continuousRValue` | `["number", "null"]` | New field: continuous insulation on the skylight. Unit: `h-ft2-F/Btu`, `default: 0.0`. |

#### `HVACSystem`

| Field | Type | Notes |
|---|---|---|
| `requirementAnswer` | `array` of `$ref Requirements` | New field. `default: []`. |

#### `HVACPlant`

| Field | Type | Notes |
|---|---|---|
| `requirementAnswer` | `array` of `$ref Requirements` | New field. `default: []`. |

#### `InteriorLightingFixture`

| Field | Type | Notes |
|---|---|---|
| `scheduleFixtureKey` | `["string", "null"]` | New field: UUID to identify this fixture schedule. |
| `typeOfFixture` | `["string", "null"]` | New field: type of the fixture. |

---

### 2. Removed Fields / Enum Values Removed

#### `ActivityTypeOptions`

| Removed value | Notes |
|---|---|
| `ACTIVITY_COMMON_OFFICE` | Removed from enum. `ACTIVITY_COMMON_OFFICE_ENCLOSED` and `ACTIVITY_COMMON_OFFICE_OPEN` remain. |

---

### 3. Type Changes

#### `ComBuilding`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `isHistoricBuilding` | `"boolean"` | `"integer"`, `enum: [0, 1]` | Changed from boolean to integer flag. |
| `isNonresidentialConditioning` | `"boolean"` | `["boolean", "null"]` | Made nullable. |
| `isResidentialConditioning` | `"boolean"` | `["boolean", "null"]` | Made nullable. |
| `isSemiheatedConditioning` | `"boolean"` | `["boolean", "null"]` | Made nullable. |
| `constructionType` | `"string"` | `["string", "null"]` | Made nullable. |

#### `CodeData`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `version` | `"string"` | `["string", "null"]` | Made nullable. |

#### `AgWall`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `heatCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |

#### `BgWall`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `heatCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |

#### `Window`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `propShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `preAltPropShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |

#### `Door`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `preAltPropShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |

#### `Skylight`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `propShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `preAltPropShgc` | `"number"` | `["number", "null"]` | Made nullable. |

#### `Roof`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `purlinSpacing` | `"number"` | `["number", "null"]` | Made nullable. |

#### `Floor`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `slabFullInsulBelowMinRValue` | `"number"` | `["number", "null"]` | Made nullable. |

#### `WholeBldgUse`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `floorArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `powerDensity` | `"number"` | `["number", "null"]` | Made nullable. |
| `internalLoad` | `"number"` | `["number", "null"]` | Made nullable. |
| `allowedWattage` | `"number"` | `["number", "null"]` | Made nullable. |
| `proposedWattage` | `"number"` | `["number", "null"]` | Made nullable. |

#### `ActivityUse`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `floorArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `ceilingHeight` | `"number"` | `["number", "null"]` | Made nullable. |
| `powerDensity` | `"number"` | `["number", "null"]` | Made nullable. |
| `internalLoad` | `"number"` | `["number", "null"]` | Made nullable. |
| `allowedWattage` | `"number"` | `["number", "null"]` | Made nullable. |
| `proposedWattage` | `"number"` | `["number", "null"]` | Made nullable. |

#### `ExteriorUse`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `powerDensity` | `"number"` | `["number", "null"]` | Made nullable. |
| `useQuantity` | `"number"` | `["number", "null"]` | Made nullable. |

#### `InteriorLightingSpace`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `numFixturesAlteredOrAdded` | `["integer", "null"]` with `minimum: 0` | `["integer", "null"]` | `minimum` constraint removed. |
| `primaryDaylight` | `"number"` | `["number", "null"]` | Made nullable. |
| `secondaryDaylight` | `"number"` | `["number", "null"]` | Made nullable. |
| `skylightToplight` | `"number"` | `["number", "null"]` | Made nullable. |
| `roofMonitorToplight` | `"number"` | `["number", "null"]` | Made nullable. |
| `decorativeArea` | `"number"` | `["number", "null"]` | Made nullable. |

#### `InteriorLightingFixture`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `fixtureType` | `"string"` | `["string", "null"]` | Made nullable. |
| `fixtureWattage` | `"number"` | `["number", "null"]` | Made nullable. |
| `quantity` | `"integer"` | `["integer", "null"]` | Made nullable. |
| `quantityWithAdvControls` | `"integer"` | `["integer", "null"]` | Made nullable. |

#### `FixtureSchedule`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `id` | `"integer"` | `["string", "integer"]` | Now also accepts string. |
| `lightingId` | `"integer"` | `["string", "integer"]` | Now also accepts string. |

#### `HVAC`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `fanSystem` | `"array"` | `["array", "null"]` | Made nullable. Added `default: null`. Description capitalised from "fan system" to "Fan system". |

#### `HVACSystem`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `quantity` minimum | `1` | `0` | Minimum quantity lowered from 1 to 0. |

#### `HVACPlant`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `condenserFlowRate` | `"number"` | `["number", "null"]` | Made nullable. |
| `condenserLeavingTemperature` | `"number"` | `["number", "null"]` | Made nullable. |
| `coolingPlantCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `enteringCondenserWaterTemperature` | `"number"` | `["number", "null"]` | Made nullable. |
| `evaporatorLeavingTemperature` | `"number"` | `["number", "null"]` | Made nullable. |
| `heatingPlantCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `heatRecovery` | `"boolean"` | `["integer", "null"]`, `enum: [0, 1, null]` | Changed from boolean to integer flag with null support. |
| `heatPumpSimultaneousCoolingAndHeating` | `"boolean"` | `["integer", "null"]`, `enum: [0, 1, null]` | Changed from boolean to integer flag with null support. |
| `leavingChilledWaterTemperature` | `"number"` | `["number", "null"]` | Made nullable. |
| `propCoolingPlantEfficiencyPartial` | `"number"` | `["number", "null"]` | Made nullable. |
| `propCoolingPlantEfficiency` | `"number"` | `["number", "null"]` | Made nullable. |
| `propHeatingPlantEfficiency` | `"number"` | `["number", "null"]` | Made nullable. |
| `quantity` minimum | `1.0` | `0` | Minimum quantity lowered from 1 to 0. |
| `systemType` | `"string"` | `["string", "null"]` | Made nullable. |
| `twoPipeSystem` | `"boolean"` | `["integer", "null"]`, `enum: [0, 1, null]` | Changed from boolean to integer flag with null support. |
| `waterloopHeatPump` | `"boolean"` | `["integer", "null"]`, `enum: [0, 1, null]` | Changed from boolean to integer flag with null support. |

#### `FanSystem`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `description2` | `"string"` | `["string", "null"]` | Made nullable. |
| `fanSystemKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `hasPressureDropCredits` | `["boolean", "integer"]` | `enum: [0, 1, null]` | Changed to nullable enum. |

#### `Fan`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `fanDesignEfficiency` | `"number"` | `["number", "null"]` | Made nullable. |
| `maxNameplateHp` | `"number"` with `minimum: 0.0` | `["number", "null"]` | Made nullable; `minimum` constraint removed. |
| `nameplateHp` | `"number"` with `minimum: 0.0` | `"number"` | `minimum` constraint removed (type unchanged). |
| `totalFanEfficiency` | `"number"` | `["number", "null"]` | Made nullable. |

#### `PressureDrop`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `recoveryEffectiveness` | `"number"`, `minimum: 0.0`, `maximum: 1.0` | `["number", "null"]`, `minimum: 0.0` | Made nullable; `maximum: 1.0` constraint removed. |
| `verticalDuctLength` | `"number"` | `["number", "null"]` | Made nullable. |

#### `ServiceWaterHeatingSystem`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `circulationPump` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `heatTraceTapeInstalled` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `combinedSystem` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `poolSystem` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `heatPumpPoolHeater` (renamed from `heatpumpPoolHeater`) | `"boolean"` | `["boolean", "null"]`, `enum: [0, 1, null]`, `default: null` | Renamed (camelCase fix) and made nullable. |
| `quantity` minimum | `1` | `0` | Minimum quantity lowered from 1 to 0. |
| `requirementAnswer` | `"array"` (no items defined) | `"array"` with `items: $ref Requirements`, `default: []` | Items type now specified. |

#### `EnergyCreditPackage`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |

#### `Renewable`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `numberOfFloors` minimum | `1` | `0` | Minimum floors lowered from 1 to 0. |
| `largestThreeFloorArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `requiredCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `proposedCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `roofAreaForRenewable` | `"number"` | `["number", "null"]` | Made nullable. |

---

### 4. Constraint Changes

#### `ComBuilding`

| Field | Change |
|---|---|
| `performanceRating` | `minimum: 0.0` removed. |
| `energyCreditPerformanceRating` | `minimum: 0.0` removed. |

#### `AgWall`

| Field | Change |
|---|---|
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |
| `continuousDeratedRValue` | `default: 0.0` removed (now has no default). |
| `propUValue` | `minimum: 0.0` removed. |
| `grossArea` | `minimum: 0.0` removed. |

#### `BgWall`

| Field | Change |
|---|---|
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |
| `propUValue` | `minimum: 0.0` removed. |

#### `Window`

| Field | Change |
|---|---|
| `propUValue` | `minimum: 0.0` removed. |
| `propShgc` | No constraint change (minimum still 0.0). |
| `preAltPropUval` | `default: 0.0` removed. |
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |

#### `Door`

| Field | Change |
|---|---|
| `propUValue` | `minimum: 0.0` removed. |
| `preAltPropUval` | `default: 0.0` removed. |
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |

#### `Skylight`

| Field | Change |
|---|---|
| `propUValue` | `minimum: 0.0` removed. |
| `preAltPropUval` | `default: 0.0` removed. |

#### `Roof`

| Field | Change |
|---|---|
| `highAlbedoRoofReqType` | Typo `"defualt"` corrected to `"default"`. |
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |
| `propUValue` | `minimum: 0.0` removed. |

#### `Floor`

| Field | Change |
|---|---|
| `cavityRValue` | Type changed to nullable. |
| `propUValue` | `minimum: 0.0` removed. |

#### `InteriorLightingSpace`

| Field | Change |
|---|---|
| `numFixturesAlteredOrAdded` | `minimum: 0` removed. |

#### `HVACSystem`

| Field | Change |
|---|---|
| `quantity` | `minimum` changed from `1` to `0`. |

#### `HVACPlant`

| Field | Change |
|---|---|
| `quantity` | `minimum` changed from `1.0` to `0`. |
| `efficiencyRequirementException` | `default: "EFF_EXCEPTION_UNSPECIFIED"` removed. |

#### `ServiceWaterHeatingSystem`

| Field | Change |
|---|---|
| `quantity` | `minimum` changed from `1` to `0`. |
| `swhSystemSubType` | `default: "UNKNOWN_SWH_SYSTEM_SUB_TYPE"` removed. |
| `efficiencyRequirementException` | `default: "EFF_EXCEPTION_UNSPECIFIED"` removed. |

#### `Envelope` (`useOrientationDetails`)

| Field | Change |
|---|---|
| `useOrientationDetails` | `default: true` replaced with `const: true`. This field must now always equal `true`. |

---

### 5. Structural / `$ref` Changes

#### `anyOf` → direct `$ref` (null support moved into enum)

Several fields that previously used `anyOf: [{type: null}, {$ref: ...}]` have been changed to a bare `$ref`. Nullability is now provided by the enum definition itself (which has had `null` added as an enum value).

| Definition | Field |
|---|---|
| `AgWall` | `adjacentSpaceBuildingType` |
| `AgWall` | `allowanceType` |
| `BgWall` | `adjacentSpaceBuildingType` |
| `BgWall` | `allowanceType` |
| `Roof` | `adjacentSpaceBuildingType` |
| `Roof` | `allowanceType` |
| `Window` | `adjacentSpaceBuildingType` |
| `Window` | `allowanceType` |
| `Window` | `frameType` |
| `Door` | `adjacentSpaceBuildingType` |
| `Door` | `allowanceType` |
| `Door` | `frameType` |
| `Skylight` | `adjacentSpaceBuildingType` |
| `Skylight` | `allowanceType` |
| `Skylight` | `frameType` |
| `Floor` | `allowanceType` |
| `InteriorLightingFixture` | `allowanceType` |
| `InteriorLightingFixture` | `ballast` |
| `InteriorLightingFixture` | `trackLightingWattageBasisType` |
| `FixtureSchedule` | `trackLightingWattageBasisType` |

#### `AgWall.otherWallType`

Changed from bare `$ref AgWallOtherTypeOptions` to `anyOf: [{type: null}, {$ref: ...}]`. Null is now explicitly permitted.

#### `WholeBldgUse.interiorLightingSpace`

Changed from bare `$ref InteriorLightingSpace` to `anyOf: [{$ref: ...}, {type: null}]`. Null is now explicitly permitted.

#### `ActivityUse.interiorLightingSpace`

Changed from bare `$ref InteriorLightingSpace` to `anyOf: [{$ref: ...}, {type: null}]`. Null is now explicitly permitted.

#### `ExteriorUse.exteriorLightingSpace`

Changed from bare `$ref ExteriorLightingSpace` to `anyOf: [{$ref: ...}, {type: null}]`. Null is now explicitly permitted.

#### `InteriorLightingFixture.advControlAllowanceType` → renamed to `advControlsAllowanceType`

Field renamed from `advControlAllowanceType` to `advControlsAllowanceType`. Also changed from bare `$ref` with no default to `$ref` with `default: null`.

---

### 6. `required` Array Changes

#### `InteriorLightingFixture`

| Change | Notes |
|---|---|
| `lightingType` removed from required | `lightingType` is no longer required. |
| `fixtureType` added to required | `fixtureType` is now required (replacing `lightingType`). |

#### `FixtureSchedule`

| Change | Notes |
|---|---|
| `lightingType` removed from required | `lightingType` is no longer required. |

*All other `required` array changes in the diff are purely formatting (inline → multi-line) with no semantic difference.*

---

### 7. New Enum Values

#### `EnergyCodeOptions`

Added: `CEZ_IECC2009`, `CEZ_IECC2012`, `CEZ_IECC2024_APPXCF`, `CEZ_90_1_2007`, `CEZ_90_1_2010`, `NONE`

#### `StateRegionEnergyCodeOptions`

Added: `CEZ_NYS2024_IECC2024`, `CEZ_NYS2025_9012022`, `CEZ_NYC2025_IECC2024`, `CEZ_NYC2025_9012022`, `CEZ_VT2024_IECC2021`, `CEZ_LA2021_IECC2021`, `NONE`

#### `ProjectTypeOptions`

Added: `NONE`, `null`. Also dropped the explicit `"type": "string"` constraint.

#### `AirBarrierComplianceTypeOptions`

Added: `AIR_BARRIER_OPTION_CONTINUITY_PLAN`

#### `AgWallTypeOptions`

Added: `OTHER_BG_WALL`, `OTHER_FRAME`, `null`. `METAL_BLDG_AG_WALL` description changed from "Metal Building Wall" to "Metal Building Wall Without Thermal Break".

#### `BgWallTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `RoofTypeOptions`

Added: `METAL_ROOF_W_THERMAL_BREAK`

#### `HighAlbedoRoofReqTypeOptions`

Added: `HA_ROOF_REQ_SOLAR_REFLECTANCE`

#### `FloorTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `SlabInsulationPositionOptions`

Added: `NONE` as an additional alias.

#### `AgWallConstructionDetailsTypeOptions`

Added: `AG_WALL_CONSTRUCTION_DETAILS_UNKNOWN`, `AG_WALL_CONSTRUCTION_DETAILS_HORIZONTAL_Z_GIRTS`, `AG_WALL_CONSTRUCTION_DETAILS_VERTICAL_Z_GIRTS`, `AG_WALL_CONSTRUCTION_DETAILS_Z_GIRTS_THERMAL_BROKEN`

#### `EnvelopeAssemblyAllowanceTypeOptions`

Added: `NONE`, `null`. Dropped explicit `"type": "string"` constraint.

#### `CMUTypeOptions`

Added: `NONE`, `null`. Dropped explicit `"type": "string"` constraint.

#### `ConcreteDensityOptions`

Added: `85`, `135`, `null`. Dropped explicit `"type": "integer"` constraint.

#### `ConcreteThicknessOptions`

Added: `3`, `4`, `5`, `7`, `9`, `11`, `null`. Dropped explicit `"type": "integer"` constraint.

#### `EnvelopeAssemblyExemptionOptions`

Added: `NONE`

#### `FurringTypeOptions`

Added: `NONE` at the beginning of the enum.

#### `OrientationOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `AltExemptTypeOptions`

Added: `EXEMPT_HISTORIC_CHARACTERISTIC`, `EXEMPT_LIGHTING_SPACE_REPLACEMENT_LT_20_PCT_LOAD`

#### `FenestrationFrameTypeOptions`

Added: `NON_METAL`, `NONE`, `METAL_FRAME_24_AG_WALL`, `GLASS_DOOR`, `METAL_THERMAL_BREAK`, `OTHER_DOOR`, `INSUL_METAL_DOOR`, `NO_INSUL_SINGLE_METAL_DOOR`, `WOOD_FRAME_16_AG_WALL`, `ALL_WOOD_JOIST_TRUSS_FLOOR`, `METAL_FRAME_16_AG_WALL`, `WOOD_DOOR`, `null`. Dropped explicit `"type": "string"` constraint.

#### `GlazingTypeOptions`

Added: `OTHER_GLAZING`, `NONE`

#### `SolarTypeOptions`

Added: `NONE`

#### `PerfDataTypeOptions`

Added: `NONE`, `PERF_TYPE_UNSPECIFIED`

#### `GlazingMaterialTypeOptions`

Added: `NONE`

#### `DoorTypeOptions`

Added: `METAL_W_THERMAL_BREAK`

#### `LightingAllowanceTypeOptions`

Added: `ALLOWANCE_ADVANCED_CONTROLS`, `ALLOWANCE_DECORATIVE_APPEARANCE_LOBBIES`, `ALLOWANCE_DECORATIVE_APPEARANCE_OTHER`, `ALLOWANCE_ELECTRICAL_MECHANICAL`, `ALLOWANCE_VIDEO_CONFERENCE`, `NONE`, `null`. Dropped explicit `"type": "string"` constraint.

#### `LightingExemptionTypeOptions`

Added: `EXEMPTION_APPROVED_SAFETY`, `EXEMPTION_DWELL_UNIT_CONTROLLED`, `EXEMPTION_EMERGENCY_AUTOOFF`, `EXEMPTION_HIGHLIGHT_HAZARDS`, `EXEMPTION_INDUSTRIAL_PRODUCTION`, `EXEMPTION_MANUFACTURER_AS_PART_OF_EQUIP`, `EXEMPTION_POOLS_WATER`, `EXEMPTION_REQUIRED_EGRESS`, `EXEMPTION_TEMP_LIGHTING`, `EXEMPTION_THEME_PARK_ELEMENTS`, `EXEMPTION_HIGHLIGHT_MONUMENT`, `EXEMPTION_TRANSPORTATION_MARKER`, `EXEMPTION_TRANSPORTATION_SITE`, `EXEMPTION_EMERGENCY_LIGHT_OFF_NORMAL_BUSINESS_HRS`, `EXEMPTION_MUSEUM_DISPLAY`, `EXEMPTION_SEARCHLIGHTS`, `EXEMPTION_SLEEPING_UNIT`, `EXEMPTION_VISUALLY_IMPAIRED`

#### `TrackLightingWattageBasisTypeOptions`

Added: `NONE`, `null`

#### `AdvancedControlsAllowanceTypeOptions`

Added: `null`. Changed `type` from `"string"` to `["string", "null"]`.

#### `WholeBuildingTypeOptions`

Added: `WHOLE_BUILDING_INVALID_USE`

#### `ExteriorLightingZoneTypeOptions`

Added: `EXT_ZONE_UNDEVELOPED`

#### `ThermalBridgeComplianceTypeOptions`

Fixed typo: `"  THERMAL_BRIDGE_AS_DESIGNED"` (leading spaces) corrected to `"THERMAL_BRIDGE_AS_DESIGNED"`. Added `null`. Dropped explicit `"type": "string"` constraint.

#### `CondenserTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `EconomizerTypeOptions`

Added: `FLUID_ECONOMIZER`

#### `FuelTypeOptions`

Added: `OIL_RESIDUAL`, `null`. Dropped explicit `"type": "string"` constraint.

#### `BoilerDraftTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `ChillerTypeOptions`

Added: `CENTRIFUGAL_NON_STANDARD`, `null`. Dropped explicit `"type": "string"` constraint.

#### `CoolingPlantTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `HeatingPlantTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `HeatPumpChillerHeatingSourceConditionOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `HeatPumpChillerLeavingHeatingWaterTempOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `HeatPumpChillerTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `HeatRejectionTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `FanSystemComplianceMethodOptions`

Added: `null`

#### `FanEfficiencyExceptionTypeOptions`

Added: `NONE`, `null`

#### `SWHSystemDrawPatternTypeOptions`

Added: `NO_COOLING_EQUIPMENT`, `null`. Dropped explicit `"type": "string"` constraint.

#### `SWHFuelTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `EquipmentEfficiencyRequirementExceptionOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `RenewableExceptionOptions`

Added: `RENEWABLE_ONSITE_EXCEPTION_IECC2024_LOW_FLOOR_AREA`, `null`. Dropped explicit `"type": "string"` constraint.

#### `BallastTypeOptions`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `RequirementAnswerStatus`

Added: `null`. Dropped explicit `"type": "string"` constraint.

#### `CompliancePathOptions`

Added: `COMPLIANCE_PATH_A`, `COMPLIANCE_PATH_B`, `COMPLIANCE_PATH_UNKNOWN`

#### `ActivityTypeOptions`

Added: `ACTIVITY_COMMON_CONFERENCE_CELL`, `ACTIVITY_COMMON_GUESTROOM`, `ACTIVITY_COMMON_PATIENT`, `ACTIVITY_COMMON_WELLNESS_LOUNGE`, `ACTIVITY_GAME_HIGH_LIMITS_GAME`, `ACTIVITY_GAME_SLOTS`, `ACTIVITY_GAME_SPORTSBOOK`, `ACTIVITY_GAME_TABLE_GAMES`, `ACTIVITY_HOSPITAL_TELEMEDICINE_ROOM`, `ACTIVITY_PARKING_DAYLIGHT_TRANSITION_ZONE`, `ACTIVITY_RETAIL_MASSAGE_SPACE`, `ACTIVITY_RETAIL_NAIL_SALON`, `ACTIVITY_RETAIL_NAIL_SALON_MALL`, `ACTIVITY_RETAIL_HAIR_SALON`, `ACTIVITY_SECURITY_SCREEN_TRANSPORTATION_FACILITIES`, `ACTIVITY_SECURITY_SCREEN_TRANSPORTATION_WAIT_AREA`, `ACTIVITY_TRANS_AIRPORT_HANGER`, `ACTIVITY_TRANS_PASSENGER_LOAD`, `ACTIVITY_SECURITY_SCREEN_GENERAL_AREA`, `ACTIVITY_SPORTS_POOL_CLASS1`, `ACTIVITY_SPORTS_POOL_CLASS2`, `ACTIVITY_SPORTS_POOL_CLASS3`, `ACTIVITY_SPORTS_POOL_CLASS4`

Removed: `ACTIVITY_COMMON_OFFICE`

---

### 8. Default Value Changes

| Definition | Field | Old default | New default |
|---|---|---|---|
| `AgWall` | `continuousDeratedRValue` | `0.0` | *(removed)* |
| `Window` | `preAltPropUval` | `0.0` | *(removed)* |
| `Door` | `preAltPropUval` | `0.0` | *(removed)* |
| `Skylight` | `preAltPropUval` | `0.0` | *(removed)* |
| `HVACPlant` | `efficiencyRequirementException` | `"EFF_EXCEPTION_UNSPECIFIED"` | *(removed)* |
| `ServiceWaterHeatingSystem` | `swhSystemSubType` | `"UNKNOWN_SWH_SYSTEM_SUB_TYPE"` | *(removed)* |
| `ServiceWaterHeatingSystem` | `efficiencyRequirementException` | `"EFF_EXCEPTION_UNSPECIFIED"` | *(removed)* |
| `ServiceWaterHeatingSystem` | `heatPumpPoolHeater` (renamed) | *(none)* | `null` |
| `ServiceWaterHeatingSystem` | `circulationPump` | *(none)* | `0` |
| `ServiceWaterHeatingSystem` | `heatTraceTapeInstalled` | *(none)* | `0` |
| `ServiceWaterHeatingSystem` | `combinedSystem` | *(none)* | `0` |
| `ServiceWaterHeatingSystem` | `poolSystem` | *(none)* | `0` |
| `InteriorLightingFixture` | `advControlsAllowanceType` | *(none)* | `null` |
| `HVAC` | `fanSystem` | *(none)* | `null` |

---

### 9. Miscellaneous / Formatting-only

A large portion of the diff consists of converting compact inline JSON arrays like `["string", "null"]` into multi-line form. These are cosmetic changes with **no semantic impact** on validation.

The schema `version` field at the root was bumped from `"0.0.1"` to `"0.0.2"`.

---

### 10. Post-merge corrections

After review, the boolean → integer changes in PR #25 were reverted. The backend treats these fields as booleans semantically (`0 = false`, `1 = true`), and the server accepts and returns `true`/`false`. Modeling them as `integer enum [0, 1]` required a runtime `IntEnum → bool` conversion workaround in `CustomBaseModel.model_dump` and introduced unnecessary `IntEnum` wrapper classes in `core_types.py`. All nine fields were restored to their original `boolean` types.

| Definition | Field | PR #25 change | Reverted to |
|---|---|---|---|
| `ComBuilding` | `isHistoricBuilding` | `integer enum [0, 1]` | `boolean`, default `false` |
| `HVACSystem` | `heatRecovery` | `integer enum [0, 1, null]` | `["boolean", "null"]` |
| `HVACSystem` | `heatPumpSimultaneousCoolingAndHeating` | `integer enum [0, 1, null]` | `["boolean", "null"]` |
| `HVACPlant` | `twoPipeSystem` | `integer enum [0, 1, null]` | `["boolean", "null"]` |
| `HVACPlant` | `waterloopHeatPump` | `integer enum [0, 1, null]` | `["boolean", "null"]` |
| `ServiceWaterHeatingSystem` | `circulationPump` | `integer enum [0, 1]`, default `0` | `boolean`, default `false` |
| `ServiceWaterHeatingSystem` | `heatTraceTapeInstalled` | `integer enum [0, 1]`, default `0` | `boolean`, default `false` |
| `ServiceWaterHeatingSystem` | `combinedSystem` | `integer enum [0, 1]`, default `0` | `boolean`, default `false` |
| `ServiceWaterHeatingSystem` | `poolSystem` | `integer enum [0, 1]`, default `0` | `boolean`, default `false` |

The `IsHistoricBuilding`, `CirculationPump`, `HeatTraceTapeInstalled`, `CombinedSystem`, and `PoolSystem` `IntEnum` classes were removed from `core_types.py` as a result.
