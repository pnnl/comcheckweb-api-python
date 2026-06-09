# Types Reference

All types are Pydantic models. Import from `comcheck_api.types`.

## Top-level project model

`ComBuilding` is the root project model. It contains:

| Field | Type | Purpose |
|---|---|---|
| `Project` | `Project` | Project metadata: title, address, owner |
| `Location` | `Location` | State, city, climate zone |
| `Envelope` | `Envelope` | Roofs, walls, floors, windows, doors, skylights, thermal bridges |
| `WholeBldgUse` | `list[WholeBldgUse]` | Building area zones (with interior lighting) |
| `HVAC` | `HVAC` | Mechanical systems |
| `Lighting` | `Lighting` | Exterior + interior lighting |
| `Renewable` | `Renewable` | Renewable energy systems |
| `Control` | `Control` | Energy code (CEZ_IECC2018, CEZ_90_1_2022, etc.) |

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
| `WholeBldgUse` | One building area / zone. Has `key`, `areaDescription`, `InteriorLightingSpace`. |
| `InteriorLightingSpace` | Lighting configuration for one area. |

## HVAC

| Model | Purpose |
|---|---|
| `HVAC` | Container. |
| `HVACSystem` | One HVAC system definition. |
| `HVACPlant` | Central plant equipment. |
| `Fan` / `FanSystem` | Fan and fan-system models. |
| `ServiceWaterHeatingSystem` (SWH) | Service water heating. |

## Enums (StrEnum)

Common ones:

| Enum | Examples |
|---|---|
| `EnergyCodeOptions` | `CEZ_IECC2018`, `CEZ_IECC2021`, `CEZ_90_1_2019`, `CEZ_90_1_2022` |
| `ProjectTypeOptions` | `NEW_CONSTRUCTION`, `RETROFIT` |
| `WallTypeOptions` | (see source for full set) |
| `GlazingMaterialTypeOptions` | (see source for full set) |
| `DoorTypeOptions` | (see source for full set) |

For exhaustive enum values, check `comcheck_api/types/` source — these
change with code revisions and are too long to enumerate here.

## Tips

- Pydantic models accept dicts in their constructors and produce
  validated instances — useful when interop with JSON.
- Models export to JSON with `.model_dump_json()`.
- The SDK accepts dicts for inputs but always returns validated
  Pydantic models — that asymmetry is intentional.
