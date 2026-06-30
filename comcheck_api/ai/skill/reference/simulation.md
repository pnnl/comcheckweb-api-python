# Simulation Flow Reference

Simulations are asynchronous on the server side. Three-step pattern:

1. **Start** — submit the project, receive a session ID.
2. **Poll** — repeatedly check status until it reports `SUCCESS`
   (terminal-ok) or `FAILED` (terminal-error).
3. **Fetch** — retrieve the result by session ID.

## Status values

`get_simulation_status(...)["status"]` is a string. Known values are
enumerated in `comcheck_api.types.SimulationStatus` (a `StrEnum`),
but **the catalog is not exhaustive** — the server may emit values
the SDK doesn't yet enumerate. The status field is typed as `str`
specifically so unknown values pass through without crashing the
polling loop. Only the terminal pair (`SUCCESS` / `FAILED`) is
guaranteed stable; treat anything else as "still in progress."

| Value | Terminal? | Meaning |
|---|---|---|
| `INITIALIZING` | no | Server is preparing the run |
| `GENERATING_BASELINE` | no | Building the baseline (code-minimum) model |
| `GENERATING_PROPOSED` | no | Building the proposed (user) model |
| `RUNNING_SIMULATIONS` | no | Energy simulations are executing |
| `CALCULATING_RESULTS` | no | Post-processing performance metrics |
| `EVALUATING` | no | Evaluating compliance results |
| `SUCCESS` | **yes** | Result is ready; call `get_simulation_result` |
| `FAILED` | **yes** | Simulation failed; check the `message` field |
| (any other value) | no | Future / unknown server state — keep polling |

Because `SimulationStatus` is a `StrEnum`, `==` works against both
the enum member and the raw string:
``status == SimulationStatus.SUCCESS`` and
``status == "SUCCESS"`` are equivalent.

## Methods

```python
from comcheck_api import COMcheckClient
client = COMcheckClient(api_key="...")
```

| Method | Returns | Purpose |
|---|---|---|
| `client.start_run_simulation(project, project_id=None)` | `str` (session ID) | Kick off the simulation. Always refreshes the envelope u-values first (via `update_uvalues`). If `project_id` is provided, the project is also saved/updated. |
| `client.update_uvalues(project)` | `ComBuilding` | Calculate assembly u-values and write them back onto the project's `agWall`, `bgWall`, `roof`, and `floor` assemblies (matched by `assemblyType`). Mutates and returns the same project. Called automatically by `start_run_simulation`. |
| `client.get_simulation_status(session_id)` | `dict` | Current status. Fields: `sessionId`, `status` (see the Status values table above), optional `message`. |
| `client.get_simulation_result(session_id)` | `dict` | Final result. Fields: `sessionId`, `performanceRating`, `energyCreditPerformanceRating`, `proposedBpf`, `baselineBpf`. |

### Loading an existing project to simulate

| Method | Returns | Notes |
|---|---|---|
| `client.list_projects()` | `list[dict]` | Each project dict uses **`_id`** (with the underscore), not `id`. |
| `client.get_project(project_id, mode="python")` | `ComBuilding` | Default. Returns a Pydantic model you can pass straight into `start_run_simulation`. |
| `client.get_project(project_id, mode="json")` | `dict` | Returns the raw project JSON instead of a parsed model. |

## Polling pattern

Always include a timeout. 5 minutes is a safe default for a typical
small/medium project.

```python
import time
from comcheck_api.types import SimulationStatus

session_id = client.start_run_simulation(project)
deadline = time.time() + 300

while time.time() < deadline:
    status = client.get_simulation_status(session_id)
    if status["status"] == SimulationStatus.SUCCESS:
        break
    if status["status"] == SimulationStatus.FAILED:
        raise RuntimeError(f"Simulation failed: {status.get('message')}")
    time.sleep(5)
else:
    raise TimeoutError(f"Simulation {session_id} did not complete in 5 minutes")

result = client.get_simulation_result(session_id)
```

## Result interpretation

- `performanceRating` is the primary pass/fail metric — typically
  expressed as a percentage margin against the baseline. Positive =
  better than baseline = pass.
- `proposedBpf` / `baselineBpf` are Building Performance Factors for
  the proposed and baseline (code-minimum) buildings.
- `energyCreditPerformanceRating` is the credit rating used when
  optional measures (renewables, advanced controls, etc.) are
  included.

## Don't

- Don't poll faster than every 5 seconds — the backend rate-limits.
- Don't run multiple concurrent simulations from the same API key
  unless you've confirmed your quota allows it.
- Don't drop the `session_id` — there's no recovery without it.
