---
name: comcheck-api
description: Use this skill when the user is writing Python code that uses
  the comcheck_api package to build COMcheck project JSON, run compliance
  simulations against the PNNL COMcheck Web API, or work with envelope
  or building-area operations. Triggers on imports of `comcheck_api`,
  mentions of COMcheck/ASHRAE 90.1/IECC compliance, or requests to
  validate building energy code compliance.
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
  users instantiate. Construct with `api_key=...`. The client does
  **not** auto-read any environment variable — read it yourself and
  pass it: `COMcheckClient(api_key=os.environ["COM_API_KEY"])`.
- **Project shape**: a project is a `ComBuilding` Pydantic model with
  lowercase top-level fields: `project` (metadata), `location`,
  `envelope`, `lighting` (which contains `wholeBldgUse[]` — the
  building areas), `hvac`, `renewable`, and `control` (energy code).
  No `Project`/`Control` PascalCase aliases exist.
  The fields `hvac`, `renewable`, and the **interior-lighting fixtures
  inside `activityUse[]`**, plus exterior lighting (`exteriorUse[]`)
  and the shared `fixtureSchedule[]`, exist on the model but have
  **no operation functions** — leave them at template defaults. Only
  `lighting.wholeBldgUse[]` (building areas, including each area's
  own `interiorLightingSpace` singleton) is mutable, via
  `project_building_area_operations`.
- **Operation modules (functional)**: building areas and envelope
  components are added/updated/removed via free functions in
  `project_building_area_operations` and `project_envelope_operations`.
  Each function takes a `ComBuilding` and returns a new `ComBuilding`.
- **Envelope items attach to a building-area key**: every
  `add_*_to_project` envelope function takes
  `(project, building_area_key, new_component)`. Look up the key
  with `ba_ops.get_building_area_keys_from_project(project)` first.
  Default projects have **no** building areas — add one with
  `ba_ops.add_building_area_to_project(...)` before any envelope
  work.
- **Defaults**: `comcheck_api.defaults` has `get_default_*_template()`
  functions that return Pydantic models filled with sensible defaults.
  Always start from these.
- **Simulation flow is async**: `start_run_simulation` returns a
  session ID. Poll `get_simulation_status` until status is
  `"SUCCESS"` (terminal-ok) or `"FAILED"` (terminal-error), then call
  `get_simulation_result`. See `comcheck_api.types.SimulationStatus`
  for known lifecycle values (the catalog isn't exhaustive — only
  the terminal pair is guaranteed stable).

## Quick start

```python
import os
import time

from comcheck_api import COMcheckClient
from comcheck_api.defaults import get_default_project_template
from comcheck_api.types import SimulationStatus

# Client does NOT auto-read COM_API_KEY — pass it in.
client = COMcheckClient(api_key=os.environ["COM_API_KEY"])

# Build a project from a default template
project = get_default_project_template()
project.project.projectTitle = "5,000 sqft office in Seattle"

# Run a simulation
session_id = client.start_run_simulation(project)

# Poll until terminal — SUCCESS or FAILED
while True:
    status = client.get_simulation_status(session_id)
    if status["status"] == SimulationStatus.SUCCESS:
        break
    if status["status"] == SimulationStatus.FAILED:
        raise RuntimeError(f"Simulation failed: {status.get('message')}")
    time.sleep(5)

result = client.get_simulation_result(session_id)
print(result["performanceRating"])
```

## Conventions (do)

- Use `get_default_*_template()` to start any new component, then
  customize. Don't construct `ComBuilding` from scratch.
- Use the operation modules (e.g.,
  `env_ops.add_ag_wall_to_project(project, area_key, wall)`) to
  mutate project structure. Don't manipulate nested dicts directly.
- For envelope items, look up the building-area key first via
  `ba_ops.get_building_area_keys_from_project(project)`. The key
  goes between `project` and the new component in every
  `add_*_to_project` envelope call.
- Set enum-typed fields (`orientation`, `wallType`, `code`, etc.)
  with members from the matching `*Options` enum imported from
  `comcheck_api.types` — not raw strings, which trigger
  Pydantic serialization warnings.
- Pass `api_key=` explicitly to `COMcheckClient(...)`. The SDK does
  **not** auto-load any env var — read it yourself:

  ```python
  from dotenv import load_dotenv
  load_dotenv()
  client = COMcheckClient(api_key=os.environ["COM_API_KEY"])
  ```

  `client.set_api_key(api_key)` is the equivalent post-construction
  setter. Users get a Personal Access Token from the COMcheck Web
  site (Settings → Developer Setting); see the
  [GitHub README](https://github.com/pnnl/comcheckweb-api-python#1-obtain-an-api-key)
  or the
  [Getting Started page](https://pnnl.github.io/comcheckweb-api-python/getting-started/)
  for the full walkthrough.
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
- Don't use `comcheck_api.managers.*` (e.g. `AgWallListManager`,
  `RoofListManager`). Those are internal list-mutation helpers; they
  bypass the validation logic in the operation modules. Always go
  through `project_envelope_operations` and
  `project_building_area_operations` instead.
- Don't add, update, or remove interior lighting (the
  `activityUse[]` fixtures), exterior lighting (`exteriorUse[]`,
  `fixtureSchedule[]`), HVAC/mechanical, or renewable-energy
  components — no operations exist for them. The whole-building
  `interiorLightingSpace` singleton on each `WholeBldgUse` *is*
  editable through `project_building_area_operations`; the per-
  activity lighting nested under `activityUse[]` is not. The
  `COMcheckClient` user methods (`list_projects`, `get_project`,
  `update_project`, `start_run_simulation`, `get_simulation_status`,
  `get_simulation_result`, `set_api_key`) are fully supported and
  fine to use. If asked for an unsupported mutation area, tell the
  user it's not implemented and offer building-area / envelope /
  simulation instead. Confirm operation scope with
  `comcheck_api.list_operations()` (only `building_area` and
  `envelope` groups exist).

## Common patterns

### Adding a building area, then an above-grade wall

`get_default_project_template()` starts with **zero building
areas** — add one before attaching any envelope component.

```python
from comcheck_api import (
    project_envelope_operations as env_ops,
    project_building_area_operations as ba_ops,
)
from comcheck_api.defaults import (
    get_default_building_area_template,
    get_default_ag_wall_template,
)
from comcheck_api.types import OrientationOptions

# 1. Add the building area (no areas exist by default).
area = get_default_building_area_template()
area.areaDescription = "Open office"
project = ba_ops.add_building_area_to_project(project, area)

# 2. Look up its key.
area_key = ba_ops.get_building_area_keys_from_project(project)[0]["key"]

# 3. Attach the wall to that area.
wall = get_default_ag_wall_template()
wall.description = "South wall"
wall.orientation = OrientationOptions.SOUTH   # use the enum, not "SOUTH"
wall.grossArea = 4800.0                        # field is grossArea, not area
project = env_ops.add_ag_wall_to_project(project, area_key, wall)
```

### Listing the user's projects and updating one

```python
projects = client.list_projects()
target = next(p for p in projects if p["name"] == "My office")  # key is "name", not "title"
project_obj = client.get_project(target["_id"])     # note the underscore
project_obj.project.projectTitle = "My office (revised)"
client.update_project(project_id=target["_id"], project_data=project_obj)
```

`list_projects()` returns **raw, untyped dicts** straight from the API
(no TypedDict enforces the shape). Each entry looks like:
`{"_id", "name", "energyCode", "status", "sharing", "ownedByMe",
"lastUpdated"}`. The display name is under `"name"` — there is **no
`"title"` key** (matching on `"title"` silently fails with
`StopIteration`/`KeyError`).

`get_project(project_id, mode="json")` returns a raw dict instead of
a `ComBuilding` model — handy when you just need the JSON shape.

### Polling a simulation with a timeout

```python
import time
from comcheck_api.types import SimulationStatus

session_id = client.start_run_simulation(project)
deadline = time.time() + 300  # 5 min
while time.time() < deadline:
    status = client.get_simulation_status(session_id)
    if status["status"] == SimulationStatus.SUCCESS:
        result = client.get_simulation_result(session_id)
        break
    if status["status"] == SimulationStatus.FAILED:
        raise RuntimeError(f"Simulation failed: {status.get('message')}")
    time.sleep(5)
else:
    raise TimeoutError(f"Simulation {session_id} did not complete in 5 min")
```

## Gotchas

- **Field names are lowercase camelCase**, not PascalCase.
  `project.project.projectTitle`, `project.control.code`,
  `project.lighting.wholeBldgUse[0].areaDescription`. There is no
  `Project`, `Control`, `WholeBldgUse` (top-level), or `.title`.
- **AG/BG wall area field is `grossArea`**, not `area`. Same for
  roofs/floors/windows/doors. Setting `.area` silently does nothing
  because Pydantic models reject unknown attributes only in strict
  mode.
- **Use enum members for typed fields**: `OrientationOptions.NORTH`,
  `WallTypeOptions.WOOD_FRAME_16_AG_WALL`,
  `EnergyCodeOptions.CEZ_90_1_2022`. Setting them to raw strings
  works at runtime but emits `PydanticSerializationUnexpectedValue`
  warnings every time the model serializes.
- **There is no `STEEL_FRAME` wall type — steel framing maps to
  `METAL_FRAME_*`.** `WallTypeOptions` members are `WOOD_FRAME_16/24`,
  `METAL_FRAME_16/24`, `METAL_WALL_WO_TB`, `METAL_BLDG`, `CONCRETE`,
  `MASONRY`, `OTHER` (each suffixed `_AG_WALL`). A user asking for a
  "steel-frame wall" wants `WallTypeOptions.METAL_FRAME_16_AG_WALL`
  (or `_24_`).
- **`COMcheckClient(api_key=...)` does not auto-read env vars.** No
  `COM_API_KEY` fallback exists in `__init__`. Pass it explicitly.
- **`SimulationStatus` is a known-values catalog, not an exhaustive
  contract.** The server may emit lifecycle values not yet in the
  enum (e.g. `EVALUATING` was added in a later version). The
  `status` field comes back as a plain `str` so unknown values
  don't crash polling. Only `SUCCESS` and `FAILED` are guaranteed
  terminal — break/raise on those, keep polling for everything
  else (don't enumerate non-terminals).
- **A 500 from `start_run_simulation` usually means bad project
  data, not a server outage.** All HTTP errors surface as the same
  `COMCheckHTTPError` — there is no validation-specific exception, so
  a payload the engine rejects (e.g. a malformed shape like assigning
  a list to an object field, or project state the engine won't
  accept) comes back as a bare HTTP 500, indistinguishable from a
  real outage. To tell them apart, simulate a fresh
  `get_default_project_template()` project: if that succeeds, the 500
  is your project data, not the server. Inspect
  `COMCheckHTTPError.status_code` / `.response_data` for detail.

## When you need more detail

- For the authoritative list of what's implemented → call
  `comcheck_api.list_operations()`. Only operations it returns are
  supported.
- For envelope assemblies (roof, walls, floor, windows, doors,
  skylights, thermal bridges) → read `reference/operations.md`.
- For Pydantic model field-level details → read `reference/types.md`.
- For the simulation start/poll/fetch flow → read
  `reference/simulation.md`.
- To validate generated code against a mocked client → run
  `scripts/validate_code.py`.
