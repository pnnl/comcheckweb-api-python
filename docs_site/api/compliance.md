# Compliance & Reports

Beyond running a full simulation, the client exposes lighter-weight checks
and a PDF report generator.

## Check compliance

`check_compliance(project)` evaluates a project against its energy code and
returns the per-category compliance status.

```python
from comcheck_api import COMcheckClient
from comcheck_api.defaults import get_default_project_template

client = COMcheckClient(api_key="your-key")
project = get_default_project_template()

compliance = client.check_compliance(project)
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
