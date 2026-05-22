# Simulation Flow Reference

Simulations are asynchronous on the server side. Three-step pattern:

1. **Start** — submit the project, receive a session ID.
2. **Poll** — repeatedly check status until it reports `complete`.
3. **Fetch** — retrieve the result by session ID.

## Methods

```python
from comcheck_api import COMcheckClient
client = COMcheckClient(api_key="...")
```

| Method | Returns | Purpose |
|---|---|---|
| `client.start_run_simulation(project, project_id=None)` | `str` (session ID) | Kick off the simulation. If `project_id` is provided, the project is also saved/updated. |
| `client.get_simulation_status(session_id)` | `dict` | Current status. Fields: `sessionId`, `status` (`pending` / `running` / `complete` / `error`), optional `message`. |
| `client.get_simulation_result(session_id)` | `dict` | Final result. Fields: `sessionId`, `performanceRating`, `energyCreditPerformanceRating`, `proposedBpf`, `baselineBpf`. |

## Polling pattern

Always include a timeout. 5 minutes is a safe default for a typical
small/medium project.

```python
import time

session_id = client.start_run_simulation(project)
deadline = time.time() + 300

while time.time() < deadline:
    status = client.get_simulation_status(session_id)
    if status["status"] == "complete":
        break
    if status["status"] == "error":
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
