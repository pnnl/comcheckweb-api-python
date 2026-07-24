# Lighting Operations — Schema & API TODOs

Open issues discovered while building the interior and exterior lighting
examples (`interior_lighting_operations.py`, `exterior_lighting_operations.py`).
Most are server-side schema mismatches that force workarounds in the example
code; the goal is to fix them upstream so the workarounds can be removed.

## Schema issues

- [ ] **Numeric fields typed non-nullable but returned/rejected as null.**
  The API declares many numeric fields (`number`/`integer`) as non-nullable,
  yet it returns `null` for them on read and then rejects those same nulls on
  write.
  - *Workaround:* `normalize_numeric_nulls()` sweeps the project and defaults
    every null numeric field to `0` before each `update_project`.
  - *Fix:* make these fields nullable in the schema (or have the API stop
    returning null for non-nullable fields).

  The fields below are the optional, purely-numeric fields that
  `normalize_numeric_nulls()` will coerce (any of them can trigger the
  `"is not of a type(s) number/integer"` rejection). Grouped by model; those
  reachable from each example are noted.

  **Interior lighting path** (`lighting.wholeBldgUse[]`):
  - `WholeBldgUse`: `allowedWattage`, `ceilingHeight`, `floorArea`,
    `internalLoad`, `powerDensity`, `proposedWattage`
  - `ActivityUse`: `allowedWattage`, `ceilingHeight`, `floorArea`,
    `internalLoad`, `powerDensity`, `proposedWattage`,
    `roomCavityRatioThreshold`
  - `InteriorLightingSpace`: `allowanceFloorArea`, `decorativeArea`,
    `numFixturesAlteredOrAdded`, `postAltTotalWattage`, `preAltNumberFixtures`,
    `preAltTotalWattage`, `primaryDaylight`, `rcrFloorToWorkplaneHeight`,
    `rcrPerimeter`, `rcrWorkplaneToLuminaireHeight`, `roofMonitorToplight`,
    `secondaryDaylight`, `skylightToplight`

  **Exterior lighting path** (`lighting.exteriorUse[]`):
  - `ExteriorUse`: `powerDensity`, `useQuantity`
  - `ExteriorLightingSpace`: `numFixturesAlteredOrAdded`, `postAltTotalWattage`,
    `preAltNumberFixtures`, `preAltTotalWattage`

  **Fixtures** (nested under both, in `*.fixture[]`):
  - `Fixture`: `advControlsAllowanceAperture`, `allowanceFloorArea`,
    `fixtureWattage`, `numberOfLamps`, `powerAllowance`,
    `quantityWithAdvControls`, `trackCircuitBreakerAmps`,
    `trackCircuitBreakerVolts`, `trackCurrentLimiterWattage`, `trackLength`,
    `trackTotalLuminaireWattage`, `trackTransformerWattage`

  **Fixture schedule** (`lighting.fixtureSchedule[]`):
  - `FixtureSchedule`: `trackCircuitBreakerAmps`, `trackCircuitBreakerVolts`,
    `trackCurrentLimiterWattage`, `trackLength`, `trackTotalLuminaireWattage`,
    `trackTransformerWattage`
  - ⚠️ `FixtureSchedule.id` and `FixtureSchedule.lightingId` are typed
    `int | None` (no `str` in the union), so `normalize_numeric_nulls()` will
    **also coerce these identifier fields to `0`** — almost certainly wrong.
    This is a hazard of the blanket sweep: purely-`int` id fields are
    indistinguishable from measurements by the annotation alone.
    - *Fix:* either exclude known id fields by name in the helper, or make id
      fields `str | int | None` in the schema so the sweep skips them (as it
      does for other `id` fields).

  > Note: `normalize_numeric_nulls()` sweeps the whole `ComBuilding` tree, so it
  > also touches numeric fields outside lighting (e.g. envelope, HVAC). The list
  > above covers only the lighting models the two examples exercise.

- [ ] **`fixture.fixtureType` vs `fixture.lightingType` requiredness.**
  In the current schema `lightingType` is required and `fixtureType` is
  optional, but `fixtureType` should be the required field and `lightingType`
  should be optional (it is marked for deprecation).
  - *Fix:* swap requiredness — make `fixtureType` required, `lightingType`
    optional.

- [ ] **Building-area / interior-lighting-space keying.**
  A building area's `areaDescription` should be unique within a project.
  Interior lighting spaces appear to key off `areaDescription` rather than the
  dedicated `key` field.
  - *Fix:* clarify/enforce which field is the identifier and ensure
    uniqueness constraints match.

## Open questions

- [ ] **`activityType` options — code-dependent or generic?**
  Confirm whether the valid `ActivityUse.activityType` options depend on the
  project's energy code, or are a single generic set.

## Source locations

| Item | File | Line (approx.) |
|---|---|---|
| Numeric null workaround | `interior_lighting_operations.py` | `normalize_numeric_nulls` docstring |
| Numeric null workaround | `exterior_lighting_operations.py` | `normalize_numeric_nulls` docstring |
| `fixtureType` requiredness | `interior_lighting_operations.py` | Step 2 (fixture setup) |
| Building-area keying | `interior_lighting_operations.py` | after client setup |
| `activityType` options | `interior_lighting_operations.py` | Step 2 (activity use setup) |
