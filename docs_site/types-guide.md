# Types Guide

The `comcheck_api` library is fully typed with Pydantic models and `StrEnum`/`IntEnum` option types defined in `comcheck_api.types.core_types`. Understanding these types is essential for correctly building and modifying COMcheck projects.

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

### Enum Options (`StrEnum` / `IntEnum`)

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

### Project Structure

The top-level model is `ComBuilding`, which contains all project data:

| Model | Description |
|---|---|
| `ComBuilding` | Top-level project model |
| `Project` | Project info (name, address) |
| `Location` | Geographic location |
| `Envelope` | All envelope assemblies (roofs, walls, floors) |
| `Lighting` | Lighting data (building areas, exterior) |
| `HVAC` | HVAC systems |

```python
from comcheck_api.types import ComBuilding

project: ComBuilding = client.get_project("project-id")
project.project       # Project
project.location      # Location
project.envelope      # Envelope
project.lighting      # Lighting
```

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

```python
from comcheck_api.types import Roof, RoofTypeOptions, OrientationOptions

# Type hints show you what fields are available
roof = Roof(
    roofType=RoofTypeOptions.ATTIC_ROOF_WITH_WOOD_JOIST,
    orientation=OrientationOptions.NORTH,
    # ... IDE auto-completes all fields
)
```

### Building Area & Lighting

| Model | Description | Key Options |
|---|---|---|
| `WholeBldgUse` | Building use area | `WholeBuildingTypeOptions` |
| `ActivityUse` | Activity area within a building use | `ActivityTypeOptions` |
| `ExteriorUse` | Exterior lighting use | `ExteriorUseTypeOptions` |
| `Fixture` | Lighting fixture | `LightingTypeOptions` |
| `FixtureSchedule` | Fixture schedule | - |
| `LightingControls` | Lighting controls | `LightingControlTypeOptions` |

### Mechanical

| Model | Description | Key Options |
|---|---|---|
| `HVACSystem` | HVAC system | `CoolingEquipmentTypeOptions`, `FuelTypeOptions` |
| `HVACPlant` | HVAC plant | `BoilerDraftTypeOptions` |
| `Fan` | Fan | `FanEfficiencyExceptionTypeOptions` |
| `FanSystem` | Fan system | `FanSystemComplianceMethodOptions` |
| `ServiceWaterHeatingSystem` | Water heating | `SWHSystemDrawPatternTypeOptions` |

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
