# Schema Changelog — comCheck.schema.json

This document describes every meaningful change introduced in the schema update merged via PR #25.
Changes are grouped by category. Within each category entries are listed by definition and field name.

---

## 1. Field Additions

### `ComBuilding`

| Field | Type | Notes |
|---|---|---|
| `bldgUseType` | `$ref BuildingUseTypeOptions` | Legacy alias for `buildingUseType`. Comment: "Legacy enum, only ACTIVITY is valid in the new ComCheck Web." |
| `efficiencyPackageType` | `enum` (string or `null`) | New field. Values: `EFF_PACKAGE_UNKNOWN`, `EFF_PACKAGE_HVAC_PERFORMANCE`, `EFF_PACKAGE_LIGHTING_REDUCED_LPD`, `EFF_PACKAGE_REDUCED_AIR_INFILTRATION`, `EFF_PACKAGE_ENHANCED_ENVELOPE_PERFORMANCE`, `EFF_PACKAGE_ENHANCED_LIGHTING_CONTROLS`, `EFF_PACKAGE_ONSITE_RENEWABLES`, `null`. Default: `null`. |
| `energyCreditMultiplierException` | `enum` (or `null`) | New field. Values: `NO_ENERGY_CREDIT_MULTIPLIER_EXCEPTION`, `ENERGY_CREDIT_MULTIPLIER_EXCEPTION_LOW_ENERGY_BUILDINGS`, `ENERGY_CREDIT_MULTIPLIER_EXCEPTION_PRIMARY_HEAT_PUMP`, `null`. No default declared. |

### `Door` (fenestration)

| Field | Type | Notes |
|---|---|---|
| `feetAg` | `["number", "null"]` | New field: feet above grade. `minimum: 0.0`, `default: null`. |

### `Skylight`

| Field | Type | Notes |
|---|---|---|
| `cavityRValue` | `["number", "null"]` | New field: average insulation R-value in cavity. Unit: `h-ft2-F/Btu`, `default: 0.0`. |
| `continuousRValue` | `["number", "null"]` | New field: continuous insulation on the skylight. Unit: `h-ft2-F/Btu`, `default: 0.0`. |

### `HVACSystem`

| Field | Type | Notes |
|---|---|---|
| `requirementAnswer` | `array` of `$ref Requirements` | New field. `default: []`. |

### `HVACPlant`

| Field | Type | Notes |
|---|---|---|
| `requirementAnswer` | `array` of `$ref Requirements` | New field. `default: []`. |

### `InteriorLightingFixture`

| Field | Type | Notes |
|---|---|---|
| `scheduleFixtureKey` | `["string", "null"]` | New field: UUID to identify this fixture schedule. |
| `typeOfFixture` | `["string", "null"]` | New field: type of the fixture. |

---

## 2. Removed Fields / Enum Values Removed

### `ActivityTypeOptions`

| Removed value | Notes |
|---|---|
| `ACTIVITY_COMMON_OFFICE` | Removed from enum. `ACTIVITY_COMMON_OFFICE_ENCLOSED` and `ACTIVITY_COMMON_OFFICE_OPEN` remain. |

---

## 3. Type Changes

### `ComBuilding`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `isHistoricBuilding` | `"boolean"` | `"integer"`, `enum: [0, 1]` | Changed from boolean to integer flag. |
| `isNonresidentialConditioning` | `"boolean"` | `["boolean", "null"]` | Made nullable. |
| `isResidentialConditioning` | `"boolean"` | `["boolean", "null"]` | Made nullable. |
| `isSemiheatedConditioning` | `"boolean"` | `["boolean", "null"]` | Made nullable. |
| `constructionType` | `"string"` | `["string", "null"]` | Made nullable. |

### `CodeData`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `version` | `"string"` | `["string", "null"]` | Made nullable. |

### `AgWall`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `heatCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |

### `BgWall`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `heatCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |

### `Window`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `propShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `preAltPropShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |

### `Door`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `preAltPropShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |

### `Skylight`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `propShgc` | `"number"` | `["number", "null"]` | Made nullable. |
| `preAltPropShgc` | `"number"` | `["number", "null"]` | Made nullable. |

### `Roof`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `purlinSpacing` | `"number"` | `["number", "null"]` | Made nullable. |

### `Floor`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `cavityRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `continuousRValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `propUValue` | `"number"` | `["number", "null"]` | Made nullable. |
| `grossArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `slabFullInsulBelowMinRValue` | `"number"` | `["number", "null"]` | Made nullable. |

### `WholeBldgUse`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `floorArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `powerDensity` | `"number"` | `["number", "null"]` | Made nullable. |
| `internalLoad` | `"number"` | `["number", "null"]` | Made nullable. |
| `allowedWattage` | `"number"` | `["number", "null"]` | Made nullable. |
| `proposedWattage` | `"number"` | `["number", "null"]` | Made nullable. |

### `ActivityUse`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `floorArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `ceilingHeight` | `"number"` | `["number", "null"]` | Made nullable. |
| `powerDensity` | `"number"` | `["number", "null"]` | Made nullable. |
| `internalLoad` | `"number"` | `["number", "null"]` | Made nullable. |
| `allowedWattage` | `"number"` | `["number", "null"]` | Made nullable. |
| `proposedWattage` | `"number"` | `["number", "null"]` | Made nullable. |

### `ExteriorUse`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `powerDensity` | `"number"` | `["number", "null"]` | Made nullable. |
| `useQuantity` | `"number"` | `["number", "null"]` | Made nullable. |

### `InteriorLightingSpace`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `numFixturesAlteredOrAdded` | `["integer", "null"]` with `minimum: 0` | `["integer", "null"]` | `minimum` constraint removed. |
| `primaryDaylight` | `"number"` | `["number", "null"]` | Made nullable. |
| `secondaryDaylight` | `"number"` | `["number", "null"]` | Made nullable. |
| `skylightToplight` | `"number"` | `["number", "null"]` | Made nullable. |
| `roofMonitorToplight` | `"number"` | `["number", "null"]` | Made nullable. |
| `decorativeArea` | `"number"` | `["number", "null"]` | Made nullable. |

### `InteriorLightingFixture`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `fixtureType` | `"string"` | `["string", "null"]` | Made nullable. |
| `fixtureWattage` | `"number"` | `["number", "null"]` | Made nullable. |
| `quantity` | `"integer"` | `["integer", "null"]` | Made nullable. |
| `quantityWithAdvControls` | `"integer"` | `["integer", "null"]` | Made nullable. |

### `FixtureSchedule`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `id` | `"integer"` | `["string", "integer"]` | Now also accepts string. |
| `lightingId` | `"integer"` | `["string", "integer"]` | Now also accepts string. |

### `HVAC`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `fanSystem` | `"array"` | `["array", "null"]` | Made nullable. Added `default: null`. Description capitalised from "fan system" to "Fan system". |

### `HVACSystem`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `quantity` minimum | `1` | `0` | Minimum quantity lowered from 1 to 0. |

### `HVACPlant`

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

### `FanSystem`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `description2` | `"string"` | `["string", "null"]` | Made nullable. |
| `fanSystemKey` | `"string"` | `["string", "null"]` | Made nullable. |
| `hasPressureDropCredits` | `["boolean", "integer"]` | `enum: [0, 1, null]` | Changed to nullable enum. |

### `Fan`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `fanDesignEfficiency` | `"number"` | `["number", "null"]` | Made nullable. |
| `maxNameplateHp` | `"number"` with `minimum: 0.0` | `["number", "null"]` | Made nullable; `minimum` constraint removed. |
| `nameplateHp` | `"number"` with `minimum: 0.0` | `"number"` | `minimum` constraint removed (type unchanged). |
| `totalFanEfficiency` | `"number"` | `["number", "null"]` | Made nullable. |

### `PressureDrop`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `recoveryEffectiveness` | `"number"`, `minimum: 0.0`, `maximum: 1.0` | `["number", "null"]`, `minimum: 0.0` | Made nullable; `maximum: 1.0` constraint removed. |
| `verticalDuctLength` | `"number"` | `["number", "null"]` | Made nullable. |

### `ServiceWaterHeatingSystem`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `circulationPump` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `heatTraceTapeInstalled` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `combinedSystem` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `poolSystem` | `"boolean"` | `"integer"`, `enum: [0, 1]`, `default: 0` | Changed from boolean to integer flag. |
| `heatPumpPoolHeater` (renamed from `heatpumpPoolHeater`) | `"boolean"` | `["boolean", "null"]`, `enum: [0, 1, null]`, `default: null` | Renamed (camelCase fix) and made nullable. |
| `quantity` minimum | `1` | `0` | Minimum quantity lowered from 1 to 0. |
| `requirementAnswer` | `"array"` (no items defined) | `"array"` with `items: $ref Requirements`, `default: []` | Items type now specified. |

### `EnergyCreditPackage`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `bldgUseKey` | `"string"` | `["string", "null"]` | Made nullable. |

### `Renewable`

| Field | Old type | New type | Notes |
|---|---|---|---|
| `numberOfFloors` minimum | `1` | `0` | Minimum floors lowered from 1 to 0. |
| `largestThreeFloorArea` | `"number"` | `["number", "null"]` | Made nullable. |
| `requiredCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `proposedCapacity` | `"number"` | `["number", "null"]` | Made nullable. |
| `roofAreaForRenewable` | `"number"` | `["number", "null"]` | Made nullable. |

---

## 4. Constraint Changes

### `ComBuilding`

| Field | Change |
|---|---|
| `performanceRating` | `minimum: 0.0` removed. |
| `energyCreditPerformanceRating` | `minimum: 0.0` removed. |

### `AgWall`

| Field | Change |
|---|---|
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |
| `continuousDeratedRValue` | `default: 0.0` removed (now has no default). |
| `propUValue` | `minimum: 0.0` removed. |
| `grossArea` | `minimum: 0.0` removed. |

### `BgWall`

| Field | Change |
|---|---|
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |
| `propUValue` | `minimum: 0.0` removed. |

### `Window`

| Field | Change |
|---|---|
| `propUValue` | `minimum: 0.0` removed. |
| `propShgc` | No constraint change (minimum still 0.0). |
| `preAltPropUval` | `default: 0.0` removed. |
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |

### `Door`

| Field | Change |
|---|---|
| `propUValue` | `minimum: 0.0` removed. |
| `preAltPropUval` | `default: 0.0` removed. |
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |

### `Skylight`

| Field | Change |
|---|---|
| `propUValue` | `minimum: 0.0` removed. |
| `preAltPropUval` | `default: 0.0` removed. |

### `Roof`

| Field | Change |
|---|---|
| `highAlbedoRoofReqType` | Typo `"defualt"` corrected to `"default"`. |
| `cavityRValue` | `minimum: 0.0` removed. |
| `continuousRValue` | `minimum: 0.0` removed. |
| `propUValue` | `minimum: 0.0` removed. |

### `Floor`

| Field | Change |
|---|---|
| `cavityRValue` (Floor def) | `minimum: 0.0` present in context line only; type changed to nullable. |
| `propUValue` (Floor def) | `minimum: 0.0` removed. |

### `InteriorLightingSpace`

| Field | Change |
|---|---|
| `numFixturesAlteredOrAdded` | `minimum: 0` removed. |

### `HVACSystem`

| Field | Change |
|---|---|
| `quantity` | `minimum` changed from `1` to `0`. |

### `HVACPlant`

| Field | Change |
|---|---|
| `quantity` | `minimum` changed from `1.0` to `0`. |
| `efficiencyRequirementException` | `default: "EFF_EXCEPTION_UNSPECIFIED"` removed. |

### `ServiceWaterHeatingSystem`

| Field | Change |
|---|---|
| `quantity` | `minimum` changed from `1` to `0`. |
| `swhSystemSubType` | `default: "UNKNOWN_SWH_SYSTEM_SUB_TYPE"` removed. |
| `efficiencyRequirementException` | `default: "EFF_EXCEPTION_UNSPECIFIED"` removed. |

### `Envelope` (`useOrientationDetails`)

| Field | Change |
|---|---|
| `useOrientationDetails` | `default: true` replaced with `const: true`. This field must now always equal `true` (no other value is valid). |

---

## 5. Structural / `$ref` Changes

### `anyOf` → direct `$ref` (null support removed from schema, now provided by enum)

Several fields that previously used `anyOf: [{type: null}, {$ref: ...}]` have been changed to a bare `$ref`. This means the field **no longer explicitly allows `null` in the JSON Schema sense** — nullability is now expected to come from the enum definition itself (which has had `null` added as an enum value).

Affected fields (definition → field):

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

### `AgWall.otherWallType`

Changed from bare `$ref AgWallOtherTypeOptions` to `anyOf: [{type: null}, {$ref: ...}]`. Null is now explicitly permitted.

### `WholeBldgUse.interiorLightingSpace`

Changed from bare `$ref InteriorLightingSpace` to `anyOf: [{$ref: ...}, {type: null}]`. Null is now explicitly permitted.

### `ActivityUse.interiorLightingSpace`

Changed from bare `$ref InteriorLightingSpace` to `anyOf: [{$ref: ...}, {type: null}]`. Null is now explicitly permitted.

### `ExteriorUse.exteriorLightingSpace`

Changed from bare `$ref ExteriorLightingSpace` to `anyOf: [{$ref: ...}, {type: null}]`. Null is now explicitly permitted.

### `InteriorLightingFixture.advControlAllowanceType` → renamed to `advControlsAllowanceType`

Field renamed from `advControlAllowanceType` to `advControlsAllowanceType`. Also changed from bare `$ref` with no default to `$ref` with `default: null`.

---

## 6. `required` Array Changes

### `InteriorLightingFixture`

| Change | Notes |
|---|---|
| `lightingType` removed from required | `lightingType` is no longer required. |
| `fixtureType` added to required | `fixtureType` is now required (replacing `lightingType`). |

### `FixtureSchedule`

| Change | Notes |
|---|---|
| `lightingType` removed from required | `lightingType` is no longer required. |

*All other `required` array changes in the diff are purely formatting (inline → multi-line) with no semantic difference.*

---

## 7. New Enum Values

### `EnergyCodeOptions` (national codes)

Added values:
- `CEZ_IECC2009`
- `CEZ_IECC2012`
- `CEZ_IECC2024_APPXCF` ("IECC 2024 Appendix CF")
- `CEZ_90_1_2007`
- `CEZ_90_1_2010`
- `NONE` ("Unspecified")

### `StateRegionEnergyCodeOptions`

Added values:
- `CEZ_NYS2024_IECC2024` ("2024 New York State Energy Conservation Code - IECC 2024")
- `CEZ_NYS2025_9012022` ("2025 New York State Energy Conservation Code - 90.1 (2022)")
- `CEZ_NYC2025_IECC2024` ("2025 New York City Energy Conservation Code - IECC 2024")
- `CEZ_NYC2025_9012022` ("2025 New York City Energy Conservation Code - 90.1 (2022)")
- `CEZ_VT2024_IECC2021` ("2024 Vermont Commercial Building Energy Standards")
- `CEZ_LA2021_IECC2021` ("2021 LA Energy Code - 2021 IECC")
- `NONE` ("Unspecified")

### `ProjectTypeOptions`

Added values:
- `NONE` ("Unspecified")
- `null` ("Missing")
- The definition also dropped the explicit `"type": "string"` constraint.

### `AirBarrierComplianceTypeOptions`

Added: `AIR_BARRIER_OPTION_CONTINUITY_PLAN` ("Continuity Plan")

### `AgWallTypeOptions`

Added:
- `OTHER_BG_WALL` ("Other Above Grade Wall Type" — note: description says "Above Grade" but value name says "BG", may be intentional)
- `OTHER_FRAME` ("Other Framing Type")
- `null` ("Unspecified")
- The existing `METAL_BLDG_AG_WALL` description changed from "Metal Building Wall" to "Metal Building Wall Without Thermal Break"

### `BgWallTypeOptions`

Added: `null` ("Unspecified"). Also dropped the explicit `"type": "string"` constraint.

### `RoofTypeOptions`

Added: `METAL_ROOF_W_THERMAL_BREAK` ("Metal Roof with Thermal Break")

### `HighAlbedoRoofReqTypeOptions`

Added: `HA_ROOF_REQ_SOLAR_REFLECTANCE` ("Minimum Solar Reflectance")

### `FloorTypeOptions`

Added: `null` ("Unspecified"). Also dropped the explicit `"type": "string"` constraint.

### `SlabInsulationPositionOptions`

Added: `NONE` ("None") as an additional alias.

### `AgWallConstructionDetailsTypeOptions`

Added:
- `AG_WALL_CONSTRUCTION_DETAILS_UNKNOWN` ("Unknown")
- `AG_WALL_CONSTRUCTION_DETAILS_HORIZONTAL_Z_GIRTS` ("Horizontal Z-Girts")
- `AG_WALL_CONSTRUCTION_DETAILS_VERTICAL_Z_GIRTS` ("Vertical Z-Girts")
- `AG_WALL_CONSTRUCTION_DETAILS_Z_GIRTS_THERMAL_BROKEN` ("Z-Girts with Thermal Break")

### `EnvelopeAssemblyAllowanceTypeOptions`

Added:
- `NONE` ("None")
- `null` ("Unspecified")
- Dropped explicit `"type": "string"` constraint.

### `CMUTypeOptions`

Added:
- `NONE` ("None")
- `null` ("Unspecified")
- Dropped explicit `"type": "string"` constraint.

### `ConcreteDensityOptions`

Added values: `85` ("Light Weight"), `135` (no description added), `null`.
Dropped explicit `"type": "integer"` constraint.

### `ConcreteThicknessOptions`

Added values: `3`, `4`, `5`, `7`, `9`, `11`, `null`.
Dropped explicit `"type": "integer"` constraint.

### `EnvelopeAssemblyExemptionOptions`

Added: `NONE` ("None")

### `FurringTypeOptions`

Added: `NONE` ("None") at the beginning of the enum.

### `OrientationOptions`

Added: `null` ("Null"). Dropped explicit `"type": "string"` constraint.

### `AltExemptTypeOptions`

Added:
- `EXEMPT_HISTORIC_CHARACTERISTIC` ("Alteration to the area is not applicable to historic characteristics.")
- `EXEMPT_LIGHTING_SPACE_REPLACEMENT_LT_20_PCT_LOAD` ("Less than 20% fixture replacement.")

### `FenestrationFrameTypeOptions`

Added values:
- `NON_METAL` ("Non-metal frame")
- `NONE` ("None")
- `METAL_FRAME_24_AG_WALL` ("24-gauge metal-framed wall")
- `GLASS_DOOR` ("Glass door")
- `METAL_THERMAL_BREAK` ("Metal frame with thermal break")
- `OTHER_DOOR` ("Other door")
- `INSUL_METAL_DOOR` ("Insulated metal door")
- `NO_INSUL_SINGLE_METAL_DOOR` ("Non-insulated single metal door")
- `WOOD_FRAME_16_AG_WALL` ("16-gauge wood-framed wall")
- `ALL_WOOD_JOIST_TRUSS_FLOOR` ("All-wood joist/truss floor")
- `METAL_FRAME_16_AG_WALL` ("16-gauge metal-framed wall")
- `WOOD_DOOR` ("Wood door")
- `null` ("Unspecified")

Also dropped explicit `"type": "string"` constraint.

### `GlazingTypeOptions`

Added:
- `OTHER_GLAZING`
- `NONE` ("None")

### `SolarTypeOptions`

Added: `NONE` ("None")

### `PerfDataTypeOptions`

Added:
- `NONE` ("None")
- `PERF_TYPE_UNSPECIFIED` ("Unspecified")

### `GlazingMaterialTypeOptions`

Added: `NONE` ("None")

### `DoorTypeOptions`

Added: `METAL_W_THERMAL_BREAK` ("Metal with Thermal Break")

### `LightingAllowanceTypeOptions`

Added:
- `ALLOWANCE_ADVANCED_CONTROLS` ("Advanced Controls")
- `ALLOWANCE_DECORATIVE_APPEARANCE_LOBBIES` ("Decorative Appearance, Lobbies")
- `ALLOWANCE_DECORATIVE_APPEARANCE_OTHER` ("Decorative Appearance, Other")
- `ALLOWANCE_ELECTRICAL_MECHANICAL` ("Electrical/Mechanical Equipment")
- `ALLOWANCE_VIDEO_CONFERENCE` ("Video conference")
- `NONE` ("None")
- `null` ("Unspecified")
- Dropped explicit `"type": "string"` constraint.

### `LightingExemptionTypeOptions`

Added:
- `EXEMPTION_APPROVED_SAFETY` ("Approved Safety Lighting")
- `EXEMPTION_DWELL_UNIT_CONTROLLED` ("Dwelling Unit Lighting Controlled by Occupant")
- `EXEMPTION_EMERGENCY_AUTOOFF` (description "Emergency Lighting Auto-off During Operating Hours" — duplicated from existing entry)
- `EXEMPTION_HIGHLIGHT_HAZARDS` (no description added in diff)
- `EXEMPTION_INDUSTRIAL_PRODUCTION` ("Industrial Production")
- `EXEMPTION_MANUFACTURER_AS_PART_OF_EQUIP`
- `EXEMPTION_POOLS_WATER`
- `EXEMPTION_REQUIRED_EGRESS` ("Lighting Required for Egress")
- `EXEMPTION_TEMP_LIGHTING` ("Temporary Lighting")
- `EXEMPTION_THEME_PARK_ELEMENTS` ("Theme Park Elements")
- `EXEMPTION_HIGHLIGHT_MONUMENT` ("Highlight Monument")
- `EXEMPTION_TRANSPORTATION_MARKER` ("Transportation Marker")
- `EXEMPTION_TRANSPORTATION_SITE` ("Transporation Site Lighting" — typo in source)
- `EXEMPTION_EMERGENCY_LIGHT_OFF_NORMAL_BUSINESS_HRS` ("Emergency Lighting Auto-off During Operating Hours")
- `EXEMPTION_MUSEUM_DISPLAY` ("Museum Display")
- `EXEMPTION_SEARCHLIGHTS` ("Searchlights")
- `EXEMPTION_SLEEPING_UNIT`
- `EXEMPTION_VISUALLY_IMPAIRED` ("Visually Impaired")

### `TrackLightingWattageBasisTypeOptions`

Added:
- `NONE` ("None")
- `null` ("Unspecified")

### `AdvancedControlsAllowanceTypeOptions`

Added: `null`. Also changed `type` from `"string"` to `["string", "null"]`.

### `WholeBuildingTypeOptions`

Added: `WHOLE_BUILDING_INVALID_USE` ("Invalid Use")

### `ExteriorLightingZoneTypeOptions`

Added: `EXT_ZONE_UNDEVELOPED` ("Undeveloped area (LZ1)")

### `ThermalBridgeComplianceTypeOptions`

- Fixed typo: `"  THERMAL_BRIDGE_AS_DESIGNED"` (leading spaces) corrected to `"THERMAL_BRIDGE_AS_DESIGNED"`.
- Added `null` ("Unspecified").
- Dropped explicit `"type": "string"` constraint.

### `CondenserTypeOptions`

Added: `null` ("Unspecified"). Dropped explicit `"type": "string"` constraint.

### `EconomizerTypeOptions`

Added: `FLUID_ECONOMIZER` ("Fluid")

### `FuelTypeOptions`

Added:
- `OIL_RESIDUAL` ("Residual Oil")
- `null` ("Unspecified")
- Dropped explicit `"type": "string"` constraint.

### `BoilerDraftTypeOptions`

Added: `null` ("Unspecified"). Dropped explicit `"type": "string"` constraint.

### `ChillerTypeOptions`

Added:
- `CENTRIFUGAL_NON_STANDARD`
- `null` ("Unspecified")
- Dropped explicit `"type": "string"` constraint.

### `CoolingPlantTypeOptions`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `HeatingPlantTypeOptions`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `HeatPumpChillerHeatingSourceConditionOptions`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `HeatPumpChillerLeavingHeatingWaterTempOptions`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `HeatPumpChillerTypeOptions`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `HeatRejectionTypeOptions`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `FanSystemComplianceMethodOptions`

Added: `null` ("Missing")

### `FanEfficiencyExceptionTypeOptions`

Added:
- `NONE` ("None")
- `null` ("Missing")

### `SWHSystemDrawPatternTypeOptions`

Added:
- `NO_COOLING_EQUIPMENT` ("No Cooling Equipment")
- `null` ("Missing")
- Dropped explicit `"type": "string"` constraint.

### `SWHFuelTypeOptions`

Added: `null` ("Unspecified"). Dropped explicit `"type": "string"` constraint.

### `EquipmentEfficiencyRequirementExceptionOptions`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `RenewableExceptionOptions`

Added:
- `RENEWABLE_ONSITE_EXCEPTION_IECC2024_LOW_FLOOR_AREA` ("Building effective floor area is less than 5,000 ft2")
- `null` ("Unspecified")
- Dropped explicit `"type": "string"` constraint.

### `BallastTypeOptions`

Added: `null` ("Unspecified"). Dropped explicit `"type": "string"` constraint.

### `RequirementAnswerStatus`

Added: `null` ("Missing"). Dropped explicit `"type": "string"` constraint.

### `CompliancePathOptions`

Added:
- `COMPLIANCE_PATH_A` ("Path A") — new canonical form
- `COMPLIANCE_PATH_B` ("Path B") — new canonical form
- `COMPLIANCE_PATH_UNKNOWN` ("Unknown")

### `ActivityTypeOptions`

Added:
- `ACTIVITY_COMMON_CONFERENCE_CELL`
- `ACTIVITY_COMMON_GUESTROOM`
- `ACTIVITY_COMMON_PATIENT`
- `ACTIVITY_COMMON_WELLNESS_LOUNGE`
- `ACTIVITY_GAME_HIGH_LIMITS_GAME`
- `ACTIVITY_GAME_SLOTS`
- `ACTIVITY_GAME_SPORTSBOOK`
- `ACTIVITY_GAME_TABLE_GAMES`
- `ACTIVITY_HOSPITAL_TELEMEDICINE_ROOM`
- `ACTIVITY_PARKING_DAYLIGHT_TRANSITION_ZONE`
- `ACTIVITY_RETAIL_MASSAGE_SPACE`
- `ACTIVITY_RETAIL_NAIL_SALON`
- `ACTIVITY_RETAIL_NAIL_SALON_MALL`
- `ACTIVITY_RETAIL_HAIR_SALON`
- `ACTIVITY_SECURITY_SCREEN_TRANSPORTATION_FACILITIES`
- `ACTIVITY_SECURITY_SCREEN_TRANSPORTATION_WAIT_AREA`
- `ACTIVITY_TRANS_AIRPORT_HANGER`
- `ACTIVITY_TRANS_PASSENGER_LOAD`
- `ACTIVITY_SECURITY_SCREEN_GENERAL_AREA`
- `ACTIVITY_SPORTS_POOL_CLASS1`
- `ACTIVITY_SPORTS_POOL_CLASS2`
- `ACTIVITY_SPORTS_POOL_CLASS3`
- `ACTIVITY_SPORTS_POOL_CLASS4`

Removed:
- `ACTIVITY_COMMON_OFFICE`

---

## 8. Default Value Changes

| Definition | Field | Old default | New default |
|---|---|---|---|
| `AgWall.continuousDeratedRValue` | — | `0.0` | *(removed)* |
| `Window.preAltPropUval` | — | `0.0` | *(removed)* |
| `Door.preAltPropUval` | — | `0.0` | *(removed)* |
| `Skylight.preAltPropUval` | — | `0.0` | *(removed)* |
| `HVACPlant.efficiencyRequirementException` | — | `"EFF_EXCEPTION_UNSPECIFIED"` | *(removed)* |
| `ServiceWaterHeatingSystem.swhSystemSubType` | — | `"UNKNOWN_SWH_SYSTEM_SUB_TYPE"` | *(removed)* |
| `ServiceWaterHeatingSystem.efficiencyRequirementException` | — | `"EFF_EXCEPTION_UNSPECIFIED"` | *(removed)* |
| `ServiceWaterHeatingSystem.heatPumpPoolHeater` (renamed) | — | *(none)* | `null` |
| `ServiceWaterHeatingSystem.circulationPump` | — | *(none)* | `0` |
| `ServiceWaterHeatingSystem.heatTraceTapeInstalled` | — | *(none)* | `0` |
| `ServiceWaterHeatingSystem.combinedSystem` | — | *(none)* | `0` |
| `ServiceWaterHeatingSystem.poolSystem` | — | *(none)* | `0` |
| `InteriorLightingFixture.advControlsAllowanceType` | — | *(none)* | `null` |
| `HVAC.fanSystem` | — | *(none)* | `null` |

---

## 9. Miscellaneous / Formatting-only

A large portion of the diff consists of converting compact inline JSON arrays like `["string", "null"]` into multi-line form. These are cosmetic changes with **no semantic impact** on validation.

Additionally, the schema `version` field at the root was bumped from `"0.0.1"` to `"0.0.2"`.

---

## 10. Post-merge corrections

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
