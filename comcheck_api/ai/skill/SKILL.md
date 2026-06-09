---
name: comcheck-api
description: Use this skill when the user is writing Python code that uses
  the comcheck_api package to build COMcheck project JSON, run compliance
  simulations against the PNNL COMcheck Web API, or work with envelope,
  lighting, mechanical, or building-area operations. Triggers on imports
  of `comcheck_api`, mentions of COMcheck/ASHRAE 90.1/IECC compliance,
  or requests to validate building energy code compliance.
---

# COMcheck API Python Client Skill

## When to use this skill

Triggers:
- The user imports `comcheck_api` or asks for help with it.
- The user mentions COMcheck, ASHRAE 90.1, IECC, or commercial building
  energy code compliance.
- The user wants to build, update, or run a simulation on a COMcheck
  project from Python.

## Core concepts

- **Single entry point**: `COMcheckClient` is the only client class
  users instantiate. Construct with `api_key=...` or rely on the
  `COM_API_KEY` env var.
- **Project shape**: a project is a `ComBuilding` Pydantic model. It
  contains: `Project` (metadata), `Location`, `Envelope`, `WholeBldgUse[]`
  (building areas), `HVAC`, `Lighting`, `Renewable`, and `Control`.
- **Operation classes (functional)**: building areas and envelope
  components are added/updated/removed via free functions in
  `project_building_area_operations` and `project_envelope_operations`.
  Each function takes a `ComBuilding` and returns a new `ComBuilding`.
- **Defaults**: `comcheck_api.defaults` has `get_default_*_template()`
  functions that return Pydantic models filled with sensible defaults.
  Always start from these.
- **Simulation flow is async**: `start_run_simulation` returns a
  session ID. Poll `get_simulation_status` until status is `complete`,
  then call `get_simulation_result`.

## Quick start

```python
from comcheck_api import COMcheckClient
from comcheck_api.defaults import get_default_project_template

client = COMcheckClient(api_key="your-key")

# Build a project from a default template
project = get_default_project_template()
project.Project.title = "5,000 sqft office in Seattle"

# Save it (creates server-side project, returns ID via list)
# Update if you have an existing ID:
# updated = client.update_project(project_id="123", project_data=project)

# Run a simulation
session_id = client.start_run_simulation(project)

# Poll until complete
import time
while True:
    status = client.get_simulation_status(session_id)
    if status["status"] == "complete":
        break
    time.sleep(5)

result = client.get_simulation_result(session_id)
print(result["performanceRating"])
```

## Conventions (do)

- Use `get_default_*_template()` to start any new component, then
  customize. Don't construct `ComBuilding` from scratch.
- Use the operation classes (e.g.,
  `project_envelope_operations.add_ag_wall_to_project(project, wall)`)
  to mutate project structure. Don't manipulate nested dicts directly.
- Read the API key from `COM_API_KEY` env var by default; let users
  pass `api_key=...` to override.
- Wrap network calls in try/except and catch `COMCheckHTTPError`,
  `COMCheckConnectionError`, `COMCheckValidationError`,
  `COMCheckSimulationError`, `COMCheckProjectNotFoundError`.
- The package uses `httpx`, not `requests`.

## Conventions (don't)

- Don't construct project JSON by hand — use templates + operation
  functions.
- Don't suggest `requests` — the SDK is `httpx`-based.
- Don't import private modules (anything starting with `_`).
- Don't poll `get_simulation_status` faster than every 5 seconds.
- Don't put the API key in source code; use env var or argument.

## Common patterns

### Adding an above-grade wall

```python
from comcheck_api import project_envelope_operations as envelope_ops
from comcheck_api.defaults import get_default_ag_wall_template

wall = get_default_ag_wall_template()
wall.name = "South wall"
wall.area = 4800.0
project = envelope_ops.add_ag_wall_to_project(project, wall)
```

### Listing the user's projects and updating one

```python
projects = client.list_projects()
target = next(p for p in projects if p["title"] == "My office")
project_obj = client.get_project(target["id"])
project_obj.Project.title = "My office (revised)"
client.update_project(project_id=target["id"], project_data=project_obj)
```

### Polling a simulation with a timeout

```python
import time
session_id = client.start_run_simulation(project)
deadline = time.time() + 300  # 5 min
while time.time() < deadline:
    status = client.get_simulation_status(session_id)
    if status["status"] == "complete":
        result = client.get_simulation_result(session_id)
        break
    time.sleep(5)
else:
    raise TimeoutError(f"Simulation {session_id} did not complete in 5 min")
```

## When you need more detail

- For envelope assemblies (roof, walls, floor, windows, doors,
  skylights, thermal bridges) → read `reference/operations.md`.
- For Pydantic model field-level details → read `reference/types.md`.
- For the simulation start/poll/fetch flow → read
  `reference/simulation.md`.
- To validate generated code against a mocked client → run
  `scripts/validate_code.py`.
