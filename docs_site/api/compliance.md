# Compliance & Reports

## UA path vs. full compliance

For ASHRAE 90.1-based codes (and state codes derived from them), there are two
distinct compliance checks:

| Check | Method | What it covers |
|---|---|---|
| UA path | `check_UA_compliance` | Envelope trade-off path only — fast, synchronous |
| Full compliance | `check_UA_compliance` → simulation | All systems (envelope, lighting, mechanical, renewables) |

Use `check_UA_compliance` alone when you only need to verify the envelope
trade-off path. For a complete compliance determination — or to generate an
official report — run the UA check first, and if it passes, launch the full
simulation.

## Full compliance workflow

```python
import time
from comcheck_api import COMcheckClient
from comcheck_api.defaults import get_default_project_template
from comcheck_api.types import SimulationStatus

client = COMcheckClient(api_key="your-key")
project = get_default_project_template()

# Step 1: UA path check
ua = client.check_UA_compliance(project)
if not ua or not ua.get("mandatoryRequirementsMet"):
    print("UA path failed — full simulation not needed.")
else:
    # Step 2: Full simulation
    session_id = client.start_run_simulation(project)
    while True:
        status = client.get_simulation_status(session_id)
        if status["status"] == SimulationStatus.SUCCESS:
            result = client.get_simulation_result(session_id)
            print(f"Full compliance result: {result}")
            break
        if status["status"] == SimulationStatus.FAILED:
            print(f"Simulation failed: {status.get('message')}")
            break
        time.sleep(5)
```

See [Simulation](simulation.md) for details on polling and result fields.

## Check UA path compliance

`check_UA_compliance(project)` evaluates the project's envelope assemblies
against the UA trade-off path and returns the per-category compliance status.

```python
from comcheck_api import COMcheckClient
from comcheck_api.defaults import get_default_project_template

client = COMcheckClient(api_key="your-key")
project = get_default_project_template()

compliance = client.check_UA_compliance(project)
# {
#   "mandatoryRequirementsMet": ...,
#   "envelopeStatus": {...}, "interiorLightingStatus": {...},
#   "exteriorLightingStatus": {...}, "renewableStatus": {...},
#   "energyCreditStatus": {...},
# }
```

## Check requirements

`check_requirements(project)` returns the applicable requirements for a
project.

```python
requirements = client.check_requirements(project)
```

## Generate a PDF report

`generate_report(project, ...)` builds a PDF report. The PDF is stored in S3
and the API returns a short-lived **presigned URL** (it expires within a few
minutes), along with the file name.

```python
report = client.generate_report(project)
# {"url": "...", "expires": "in 5 minutes", "fileName": "report...pdf"}
```

This method does **not** open a browser — as a library it returns the
metadata and lets you decide what to do (e.g. `webbrowser.open(report["url"])`).

### Selecting report sections

Toggle which sections appear in the report (all default to `True`):

```python
report = client.generate_report(
    project,
    envelope=True,
    intlighting=True,
    extlighting=False,
    mechanical=True,
)
```

### Downloading the PDF

Pass `download=True` to fetch the PDF from the presigned URL and save it using
the server-provided file name. `download_dir` defaults to your `~/Downloads`
folder:

```python
report = client.generate_report(project, download=True)                     # ~/Downloads
report = client.generate_report(project, download=True, download_dir="./out")
```
