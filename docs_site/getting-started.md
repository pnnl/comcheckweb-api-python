# Getting Started

!!! note "Supported Sections"
    Currently, **Building Area**, **Envelope**, **Interior Lighting**, **Exterior Lighting**, **Mechanical**, **Credits**, **Renewable Energy**, and **Compliance Simulation** operations are supported. Mechanical requirements are not supported; fill them out on [COMcheck Web](https://comcheck.energycode.pnl.gov/). See the [home page](index.md#current-status) for the full status table.

## Setup

### 1. Obtain an API Key

Get a Personal Access Token from the
[COMcheck Web site](https://comcheck.energycode.pnl.gov):

1. Log in (or register a new account if you don't have one).
2. Click your **username** in the left-side navigation.
3. From the menu that appears, choose **Settings**.
4. Click **Developer Setting** to open the Personal Access Token
   page.
5. Click **Generate**, then immediately copy the token.

!!! warning "Save it now — shown only once"
    The token is displayed once and cannot be retrieved later. Save
    it to a password manager or your `.env` file before leaving the
    page. If you lose it, generate a new one (the previous token
    becomes invalid).

### 2. Install the package

```bash
pip install comcheck_api
```

### 3. Set your API key

The SDK does **not** auto-load the env var — read it yourself and
pass it in. With `python-dotenv` this is two extra lines:

```bash
# .env file
COM_API_KEY=your-api-key-here
```

```python
import os
from dotenv import load_dotenv
from comcheck_api import COMcheckClient

load_dotenv()

# Option 1: Pass directly at construction
client = COMcheckClient(api_key=os.environ["COM_API_KEY"])

# Option 2: Set later
client = COMcheckClient()
client.set_api_key(os.environ["COM_API_KEY"])
```

## Basic Workflow

Every project operation takes a `ComBuilding`, returns an **updated copy**,
and leaves the original unchanged — always reassign the result
(`project = ...`). Changes are local until you call
`client.update_project(...)`.

### Fetch and inspect a project

```python
from comcheck_api import COMcheckClient

with COMcheckClient(api_key="your-key") as client:
    # List all projects
    projects = client.list_projects()

    # Get a single project as a Pydantic model
    project = client.get_project("project-id")

    # Or as raw JSON dict
    project_dict = client.get_project("project-id", mode="json")
```

### Work with building areas

Envelope components, interior lighting spaces, and energy credits all belong
to a building area, so add one first and keep its `key`.

```python
from comcheck_api import project_building_area_operations
from comcheck_api.defaults import get_default_building_area_template

# Add a building area
area = get_default_building_area_template()
project = project_building_area_operations.add_building_area_to_project(
    project, new_building_area=area
)
area_key = area.key

# List building area keys
keys = project_building_area_operations.get_building_area_keys_from_project(project)
```

See [Building Area](api/operations/building-area.md).

### Envelope

```python
from comcheck_api import project_envelope_operations
from comcheck_api.defaults import (
    get_default_roof_template,
    get_default_ag_wall_template,
)

# Add a roof
roof = get_default_roof_template()
project = project_envelope_operations.add_roof_to_project(
    project, building_area_key=area_key, new_roof=roof
)

# Add an above-grade wall
wall = get_default_ag_wall_template()
project = project_envelope_operations.add_ag_wall_to_project(
    project, building_area_key=area_key, new_ag_wall=wall
)
```

See [Envelope](api/operations/envelope.md).

### Interior lighting

```python
from comcheck_api import project_interior_lighting_operations
from comcheck_api.defaults import (
    get_default_interior_space_template,
    get_default_fixture_template,
)
from comcheck_api.types import ActivityTypeOptions

fixture = get_default_fixture_template()
fixture.description = "Recessed LED"
fixture.fixtureType = "Recessed LED"
fixture.fixtureWattage = 20.0
fixture.quantity = 10

space = get_default_interior_space_template()
space.areaDescription = "Open Office"
space.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE_OPEN
space.floorArea = 2000.0
space.interiorLightingSpace = space.interiorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = project_interior_lighting_operations.add_interior_space_to_project(
    project, building_area_key=area_key, new_interior_space=space
)
```

See [Interior Lighting](api/operations/interior-lighting.md).

### Exterior lighting

```python
from comcheck_api import project_exterior_lighting_operations
from comcheck_api.defaults import get_default_exterior_area_template
from comcheck_api.types import ExteriorLightingZoneTypeOptions

project = project_exterior_lighting_operations.set_exterior_lighting_zone_type_in_project(
    project, ExteriorLightingZoneTypeOptions.EXT_ZONE_NEIGHBORHOOD_BUS_DISTRICT
)

ext_area = get_default_exterior_area_template()
ext_area.areaDescription = "Front Parking Lot"
ext_area.useQuantity = 5000.0
project = project_exterior_lighting_operations.add_exterior_area_to_project(
    project, new_exterior_area=ext_area
)
```

See [Exterior Lighting](api/operations/exterior-lighting.md).

### Mechanical

Mechanical components are identified by their `description`, so give each
one a unique name.

```python
from comcheck_api import project_mechanical_operations
from comcheck_api.defaults import (
    get_default_hvac_system_template,
    get_default_fan_system_template,
    get_default_water_heater_template,
)

hvac = get_default_hvac_system_template()
hvac.description = "RTU-1"
project = project_mechanical_operations.add_hvac_system_to_project(
    project, new_hvac_system=hvac
)

fan_system = get_default_fan_system_template()
fan_system.description = "Fan System 1"
project = project_mechanical_operations.add_fan_system_to_project(
    project, new_fan_system=fan_system
)
project = project_mechanical_operations.assign_fan_system_to_hvac_system(
    project, hvac_system_description="RTU-1", fan_system_description="Fan System 1"
)

water_heater = get_default_water_heater_template()
water_heater.description = "WH-1"
project = project_mechanical_operations.add_water_heater_to_project(
    project, new_water_heater=water_heater
)
```

See [Mechanical](api/operations/mechanical.md).

### Credits

```python
from comcheck_api import project_credit_operations
from comcheck_api.types import EfficiencyPackage, IECC2024EnergyCreditTypeOptions

project = project_credit_operations.add_energy_credit_to_project(
    project,
    building_area_key=area_key,
    new_energy_credit=EfficiencyPackage(
        type=IECC2024EnergyCreditTypeOptions.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ENHANCED_ROOF_R10
    ),
)

# Calculate earned vs. required credits
result = client.calculate_energy_credits(project)
```

See [Credits](api/operations/credits.md).

### Renewable energy

```python
from comcheck_api import project_renewable_operations
from comcheck_api.defaults import get_default_renewable_system_template

pv = get_default_renewable_system_template()
pv.description = "Rooftop PV"
pv.renewableSystemCapacity = 25000.0  # watts
project = project_renewable_operations.add_renewable_system_to_project(
    project, new_renewable_system=pv
)

# Refresh required vs. proposed capacity
project = client.renewable_capacity(project)
```

See [Renewable Energy](api/operations/renewable-energy.md).

### Save and run a compliance simulation

```python
import time
from comcheck_api.types import SimulationStatus

# Save changes
client.update_project("project-id", project)

# Start simulation
session_id = client.start_run_simulation(project)

# Poll until terminal — only SUCCESS and FAILED are guaranteed terminal states.
# Don't poll faster than every 5 seconds.
while True:
    status = client.get_simulation_status(session_id)
    if status["status"] == SimulationStatus.SUCCESS:
        break
    if status["status"] == SimulationStatus.FAILED:
        raise RuntimeError(f"Simulation failed: {status.get('message')}")
    time.sleep(5)

# Get results
result = client.get_simulation_result(session_id)
print(f"Performance Rating: {result['performanceRating']}")
```

See [Simulation](api/simulation.md) and [Compliance & Reports](api/compliance.md).

## Error Handling

```python
from comcheck_api import (
    COMcheckClient,
    COMCheckHTTPError,
    COMCheckConnectionError,
    COMCheckProjectNotFoundError,
)

client = COMcheckClient(api_key="your-key")

try:
    project = client.get_project("nonexistent-id")
except COMCheckProjectNotFoundError as e:
    print(f"Project not found: {e.project_id}")
except COMCheckHTTPError as e:
    print(f"HTTP {e.status_code}: {e}")
except COMCheckConnectionError:
    print("Cannot reach the COMcheck API")
```

## Exporting Data

```python
from comcheck_api.utilities.common import export_to_json

# Export any data to JSON
json_str = export_to_json(project.model_dump(mode="json"))

# Or save to a file
export_to_json(project.model_dump(mode="json"), "my_project.json")
```
