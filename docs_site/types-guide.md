# Types Guide

The `comcheck_api` library is fully typed with Pydantic models and `StrEnum`/`Enum` option types defined in `comcheck_api.types.core_types`. Understanding these types is essential for correctly building and modifying COMcheck projects.

## Importing Types

All types are re-exported from `comcheck_api.types`, so you can import them directly:

```python
from comcheck_api.types import (
    # Models
    ComBuilding,
    Envelope,
    Roof,
    AgWall,
    Window,

    # Enum options
    EnergyCodeOptions,
    WholeBuildingTypeOptions,
    OrientationOptions,
    RoofTypeOptions,
    WallTypeOptions,
)
```

## Type Categories

There are two categories of types:

### Models (Pydantic)

Models represent the data structures returned by and sent to the COMcheck API. They provide auto-completion, validation, and serialization.

```python
from comcheck_api.types import ComBuilding, Roof

# Models validate on construction
project: ComBuilding = client.get_project("project-id")

# Access nested attributes with full type hints
roof: Roof = project.envelope.roof[0]
print(roof.roofType)       # IDE shows available attributes
print(roof.orientation)    # typed as OrientationOptions | None
```

### Enum Options (`StrEnum` / `Enum`)

Enum options define the valid values for fields like building types, orientations, energy codes, etc. Using them prevents typos and gives you IDE auto-completion for all valid choices.

```python
from comcheck_api.types import (
    EnergyCodeOptions,
    WholeBuildingTypeOptions,
    OrientationOptions,
)

# Set the energy code
project.control.code = EnergyCodeOptions.CEZ_90_1_2022

# Use building type options
area.wholeBldgType = WholeBuildingTypeOptions.WHOLE_BUILDING_OFFICE

# Set orientation
wall.orientation = OrientationOptions.NORTH
```

To see all valid values for an enum, use your IDE's auto-complete on the enum class, or inspect it at runtime:

```python
from comcheck_api.types import EnergyCodeOptions

# List all valid energy codes
for code in EnergyCodeOptions:
    print(code.name, "=", code.value)
```

## Common Types by Domain

Each domain below has a matching project operations
module for adding, updating, and removing its components:

| Domain | Operations module | Page |
|---|---|---|
| Building Area | `project_building_area_operations` | [Building Area](api/operations/building-area.md) |
| Envelope | `project_envelope_operations` | [Envelope](api/operations/envelope.md) |
| Interior Lighting | `project_interior_lighting_operations` | [Interior Lighting](api/operations/interior-lighting.md) |
| Exterior Lighting | `project_exterior_lighting_operations` | [Exterior Lighting](api/operations/exterior-lighting.md) |
| Mechanical | `project_mechanical_operations` | [Mechanical](api/operations/mechanical.md) |
| Credits | `project_credit_operations` | [Credits](api/operations/credits.md) |
| Renewable | `project_renewable_operations` | [Renewable Energy](api/operations/renewable-energy.md) |

### Project Structure

The top-level model is `ComBuilding`, which contains all project data:

| Attribute | Model | Description |
|---|---|---|
| — | `ComBuilding` | Top-level project model |
| `project` | `Project` | Project info (name, address) |
| `location` | `Location` | Geographic location |
| `envelope` | `Envelope` | Envelope assemblies (roofs, walls, floors, fenestration) |
| `lighting` | `Lighting` | Building areas, interior lighting spaces, and exterior lighting areas |
| `hvac` | `HVAC` | HVAC systems, fan systems, and HVAC plants |
| `swhSystem` | `list[ServiceWaterHeatingSystem]` | Service water heating systems |
| `efficiencyPackages` | `list[EfficiencyPackage]` | Energy credits |
| `renewable` | `Renewable` | On-site renewable systems and off-site procurement |

```python
from comcheck_api.types import ComBuilding

project: ComBuilding = client.get_project("project-id")
project.project             # Project
project.location            # Location
project.envelope            # Envelope
project.lighting            # Lighting
project.hvac                # HVAC
project.swhSystem           # list[ServiceWaterHeatingSystem]
project.efficiencyPackages  # list[EfficiencyPackage]
project.renewable           # Renewable
```

### Building Area

| Model | Description | Key Options |
|---|---|---|
| `WholeBldgUse` | Building use area — parent of envelope components, interior lighting spaces, and energy credits | `WholeBuildingTypeOptions` |

See also: [Building Area operations](api/operations/building-area.md).

### Envelope Components

| Model | Description | Key Options |
|---|---|---|
| `Roof` | Roof assembly | `RoofTypeOptions`, `RoofInsulationTypeOptions` |
| `Floor` | Floor assembly | `FloorTypeOptions` |
| `AgWall` | Above-grade wall | `WallTypeOptions`, `AgWallConstructionDetailsTypeOptions` |
| `BgWall` | Below-grade wall | `BgWallTypeOptions` |
| `Window` | Window component | `FenestrationFrameTypeOptions`, `GlazingTypeOptions` |
| `Door` | Door component | `DoorTypeOptions` |
| `Skylight` | Skylight component | `SkylightCurbTypeOptions`, `GlazingTypeOptions` |
| `ThermalBridge` | Thermal bridge | `ThermalBridgeTypeOptions` |

See also: [Envelope operations](api/operations/envelope.md).

```python
from comcheck_api.types import Roof, RoofTypeOptions, OrientationOptions

# Type hints show you what fields are available
roof = Roof(
    roofType=RoofTypeOptions.WOOD_STD_JOIST_TRUSS,
    orientation=OrientationOptions.NORTH,
    # ... IDE auto-completes all fields
)
```

### Interior Lighting

| Model | Description | Key Options |
|---|---|---|
| `ActivityUse` | Interior lighting space within a building area, aliased as `InteriorSpace` | `ActivityTypeOptions` |
| `InteriorLightingSpace` | Lighting details of an interior space (fixtures, daylight areas) | - |
| `Fixture` | Lighting fixture | `LightingTypeOptions` |
| `FixtureSchedule` | Fixture schedule | - |
| `LightingControls` | Lighting controls | `LightingControlTypeOptions` |

See also: [Interior Lighting operations](api/operations/interior-lighting.md).

### Exterior Lighting

| Model | Description | Key Options |
|---|---|---|
| `Lighting` | Holds the project-wide exterior lighting zone | `ExteriorLightingZoneTypeOptions` |
| `ExteriorUse` | Exterior lighting area, aliased as `ExteriorArea` | `ExteriorUseTypeOptions` |
| `ExteriorLightingSpace` | Lighting details of an exterior area (fixtures) | - |
| `Fixture` | Lighting fixture | `LightingTypeOptions` |

See also: [Exterior Lighting operations](api/operations/exterior-lighting.md).

!!! tip "InteriorSpace and ExteriorArea aliases"
    `comcheck_api.types.common_types` defines `InteriorSpace = ActivityUse` and
    `ExteriorArea = ExteriorUse`. The `project_interior_lighting_operations`
    and `project_exterior_lighting_operations` modules use these aliases in
    their function signatures to disambiguate interior lighting spaces from
    exterior lighting areas — both are otherwise easy to confuse by name.

### Mechanical

| Model | Description | Key Options |
|---|---|---|
| `HVACSystem` | HVAC system | `CoolingEquipmentTypeOptions`, `FuelTypeOptions` |
| `FanSystem` | Fan system | `FanSystemComplianceMethodOptions` |
| `Fan` | Fan within a fan system | `FanEfficiencyExceptionTypeOptions` |
| `FanSystemPressureDropCredits` | Pressure drop credit within a fan system | `PressureDropTypeOptions` |
| `HVACPlant` | HVAC plant | `BoilerDraftTypeOptions` |
| `ServiceWaterHeatingSystem` | Water heating | `SWHSystemDrawPatternTypeOptions` |

See also: [Mechanical operations](api/operations/mechanical.md).

### Credits

| Model | Description | Key Options |
|---|---|---|
| `EfficiencyPackage` | Energy credit tied to a building area by `bldgUseKey`; its `type` selects the credit | `IECC2024EnergyCreditTypeOptions`, `VT2024EnergyCreditTypeOptions`, `Denver2022EnergyCreditTypeOptions`, `MAS2022EnergyCreditTypeOptions`, `EfficiencyPackageTypeOptions` |
| `ComBuilding` | Project-level `energyCreditMultiplierException` | `EnergyCreditMultiplierException` |

See also: [Credits operations](api/operations/credits.md).

Each energy code family has its own credit type enum — pick the one that
matches `project.control.code`.

### Renewable

| Model | Description | Key Options |
|---|---|---|
| `Renewable` | Renewable section: exception, required/proposed capacity, systems, and off-site procurement | `RenewableExceptionOptions` |
| `RenewableSystem` | On-site renewable system | `RenewableSystemTypeOptions`, `RenewableSystemCapacityUnitOptions` |
| `OffsiteRenewableProcurement` | Off-site renewable energy procurement | `OffsiteRenewableProcurementType` |

See also: [Renewable Energy operations](api/operations/renewable-energy.md).

## Tips

**Use your IDE.** The biggest advantage of these types is auto-completion. When you type `project.envelope.`, your IDE will show all available attributes and their types.

**Check enum values.** If you're unsure what values a field accepts, look at its type annotation. Fields typed as an `Options` enum only accept values from that enum:

```python
from comcheck_api.types import WallTypeOptions

# See all options
list(WallTypeOptions)
```

**Serialize models.** All models support Pydantic's serialization:

```python
# To dict
data = project.model_dump()

# To JSON string
json_str = project.model_dump_json(indent=2)

# Deep copy for modification
copy = project.model_copy(deep=True)
```
