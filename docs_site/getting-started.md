# Getting Started

!!! note "Supported Sections"
    Currently, only **Building Area**, **Envelope**, and **Compliance Simulation** operations are fully supported. Interior lighting, exterior lighting, mechanical, credits, and renewable energy sections are planned but not yet implemented. See the [home page](index.md#current-status) for the full status table.

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

### Modify a project with envelope operations

```python
from comcheck_api import COMcheckClient, project_envelope_operations
from comcheck_api.defaults import (
    get_default_roof_template,
    get_default_ag_wall_template,
)

client = COMcheckClient(api_key="your-key")
project = client.get_project("project-id")

# Add a roof
roof = get_default_roof_template()
project = project_envelope_operations.add_roof_to_project(
    project, building_area_key="area-key", new_roof=roof
)

# Add an above-grade wall
wall = get_default_ag_wall_template()
project = project_envelope_operations.add_ag_wall_to_project(
    project, building_area_key="area-key", new_ag_wall=wall
)

# Save changes
client.update_project("project-id", project)
```

### Run a compliance simulation

```python
import time
from comcheck_api import COMcheckClient

client = COMcheckClient(api_key="your-key")
project = client.get_project("project-id")

# Start simulation
session_id = client.start_run_simulation(project)

# Poll for completion
while True:
    status = client.get_simulation_status(session_id)
    if status["status"] == "COMPLETED":
        break
    time.sleep(2)

# Get results
result = client.get_simulation_result(session_id)
print(f"Performance Rating: {result['performanceRating']}")
```

### Work with building areas

```python
from comcheck_api import project_building_area_operations
from comcheck_api.defaults import (
    get_default_building_area_template,
)

# Add a building area
area = get_default_building_area_template()
project = project_building_area_operations.add_building_area_to_project(
    project, new_building_area=area
)

# List building area keys
keys = project_building_area_operations.get_building_area_keys_from_project(project)
```

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
