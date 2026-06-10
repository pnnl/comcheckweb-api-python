# Types Reference

All types are Pydantic models. Import from `comcheck_api.types`.

## Top-level project model

`ComBuilding` is the root project model. **All top-level fields are
lowercase camelCase** (no `Project`/`Control`/`Envelope` PascalCase
aliases exist).

| Field | Type | Purpose |
|---|---|---|
| `project` | `Project` | Project metadata. Title is `project.project.projectTitle`; address fields use `projectAddress` / `projectCity` / etc. |
| `location` | `Location` | State, city, climate zone. |
| `envelope` | `Envelope` | Roofs (`roof[]`), AG walls (`agWall[]`), BG walls (`bgWall[]`), floors, windows, doors, skylights. |
| `lighting` | `Lighting` | Holds `wholeBldgUse[]` — the **building areas / zones**. `wholeBldgUse[]` (including each area's `interiorLightingSpace` singleton) is operable; `activityUse[]`, `exteriorUse[]`, and `fixtureSchedule[]` have no operations. |
| `hvac` | `HVAC` | Mechanical systems — no operations; not editable via this SDK. |
| `renewable` | `Renewable` | Renewable energy systems — no operations; not editable via this SDK. |
| `control` | `Control` | Energy code (`control.code`, e.g. `CEZ_IECC2018`, `CEZ_90_1_2022`). |

Building areas (`WholeBldgUse`) are **not top-level** — they live
under `lighting.wholeBldgUse[]`. Use
`ba_ops.get_building_area_keys_from_project(project)` to enumerate
them.

## Envelope component models

| Model | Notes |
|---|---|
| `Envelope` | Container for all envelope components. |
| `Roof` | Skylights nest inside. |
| `AgWall` (above-grade) | Windows, doors, thermal bridges nest inside. |
| `BgWall` (below-grade) | Same nesting as AgWall. |
| `Floor` | Top-level. |
| `Skylight` | Standalone or nested under a `Roof`. |
| `Window` | Standalone or nested under a wall. |
| `Door` | Standalone or nested under a wall. |
| `ThermalBridge` | Nested under a wall. |

## Building area / lighting

| Model | Purpose |
|---|---|
| `WholeBldgUse` | One building area / zone. Lives in `project.lighting.wholeBldgUse[]`. Has `key`, `areaDescription`, `floorArea`, `ceilingHeight`, `interiorLightingSpace`, etc. |
| `InteriorLightingSpace` | Lighting configuration for one area. The singleton attached directly to a `WholeBldgUse` is editable via `update_building_area_in_project`; the same model nested under `activityUse[]` is **not** operable (interior-lighting fixtures live there). |

Every envelope component has a `bldgUseKey` field that ties it to
one of these area keys.

## HVAC

⚠️ Documented for shape only — no add/update/remove operations exist
for any of these models. Leave `project.hvac` at its template default.

| Model | Purpose |
|---|---|
| `HVAC` | Container. |
| `HVACSystem` | One HVAC system definition. |
| `HVACPlant` | Central plant equipment. |
| `Fan` / `FanSystem` | Fan and fan-system models. |
| `ServiceWaterHeatingSystem` (SWH) | Service water heating. |

## Enums (StrEnum)

Always set typed fields with members from the matching `*Options`
enum imported from `comcheck_api.types`. Setting them as raw strings
"works" but emits `PydanticSerializationUnexpectedValue` warnings
on every serialize.

Common ones:

| Enum | Examples |
|---|---|
| `EnergyCodeOptions` | `CEZ_IECC2018`, `CEZ_IECC2021`, `CEZ_90_1_2019`, `CEZ_90_1_2022` |
| `OrientationOptions` | `NORTH`, `EAST`, `SOUTH`, `WEST`, plus diagonals and `UNSPECIFIED_ORIENTATION` |
| `WallTypeOptions` | (see source for full set) |
| `SimulationStatus` | Known: `INITIALIZING`, `GENERATING_BASELINE`, `GENERATING_PROPOSED`, `RUNNING_SIMULATIONS`, `CALCULATING_RESULTS`, `EVALUATING`, `SUCCESS`, `FAILED`. Catalog is **not exhaustive** — only `SUCCESS`/`FAILED` are guaranteed terminal. |

For exhaustive enum values, use
`comcheck_api.lookup_type("WallTypeOptions")` (or any other enum
name) — that's the live source of truth and stays in sync with the
installed SDK.

## Tips

- Pydantic models accept dicts in their constructors and produce
  validated instances — useful when interop with JSON.
- Models export to JSON with `.model_dump_json()`.
- The SDK accepts dicts for inputs but always returns validated
  Pydantic models — that asymmetry is intentional.
