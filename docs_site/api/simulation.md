# Simulation

COMcheck evaluates whether a building design meets energy code requirements
by running a compliance simulation. The simulation compares the proposed
building envelope against baseline performance factors and returns a
**performance rating** that indicates pass/fail status.

## Workflow

A simulation run follows three steps:

1. **Start** the simulation with a project.
2. **Poll** for completion.
3. **Retrieve** the results.

```python
import time
from comcheck_api import COMcheckClient

client = COMcheckClient(api_key="your-key")
project = client.get_project("project-id")

# 1. Start
session_id = client.start_run_simulation(project)

# 2. Poll
while True:
    status = client.get_simulation_status(session_id)
    if status["status"] == "COMPLETED":
        break
    time.sleep(2)

# 3. Results
result = client.get_simulation_result(session_id)
print(f"Performance Rating: {result['performanceRating']}")
```

## Running without a saved project

You can simulate a project that only exists locally without saving it to the
server first. Build a project from the default template, configure it, and
pass it directly:

```python
from comcheck_api import COMcheckClient
from comcheck_api.defaults import get_default_project_template
from comcheck_api.types.core_types import EnergyCodeOptions

client = COMcheckClient(api_key="your-key")

project = get_default_project_template()
project.control.code = EnergyCodeOptions.CEZ_90_1_2022

session_id = client.start_run_simulation(project)
```

## Running for an existing project

When you pass a `project_id`, the client saves the project via
`update_project` before launching the simulation:

```python
session_id = client.start_run_simulation(project, project_id="your-project-id")
```

## Envelope u-values

`start_run_simulation` always refreshes the calculated envelope u-values
before submitting, by calling `update_uvalues(project)`. This fetches the
proposed/effective u-values for the envelope assemblies and writes them
back onto the matching `agWall`, `bgWall`, `roof`, and `floor` components
(matched by `assemblyType`). Only these assembly types receive calculated
u-values, and `effectiveUFactor` applies to `agWall` only.

You normally don't need to call it yourself, but it's available when you
want refreshed u-values on a project outside the simulation flow:

```python
project = client.update_uvalues(project)
```

!!! warning "Each assembly needs a construction type"
    The engine classifies an assembly by its construction-type field
    (`roofType`, `wallType`, …) to calculate its u-value. If that field is
    missing or null, the engine returns an `"Other"` classification with a
    `propUValue` of `0.0`, and the result won't match your assembly — so its
    u-value is silently left unchanged. The default templates set these
    fields; keep them populated if you build an assembly by hand.

## Simulation status

`get_simulation_status` returns a dict with:

| Key | Description |
| --- | --- |
| `sessionId` | The session identifier |
| `status` | `"RUNNING"`, `"COMPLETED"`, or `"FAILED"` |
| `message` | Optional details (present on failure) |

## Simulation results

`get_simulation_result` returns a dict with:

| Key | Description |
| --- | --- |
| `sessionId` | The session identifier |
| `performanceRating` | Overall compliance rating |
| `energyCreditPerformanceRating` | Rating including energy credits |
| `proposedBpf` | Proposed building performance factor |
| `baselineBpf` | Baseline building performance factor |
