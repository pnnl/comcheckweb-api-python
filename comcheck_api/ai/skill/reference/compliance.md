# Compliance, Requirements & Reports Reference

Three client methods evaluate a project without running the full
async simulation flow. All three accept a `ComBuilding` and serialize
it for you — pass the project model directly.

```python
from comcheck_api import COMcheckClient
client = COMcheckClient(api_key="...")
```

| Method | Returns | Purpose |
|---|---|---|
| `client.check_compliance(project)` | `dict` | Per-category compliance status for the project. |
| `client.check_requirements(project)` | `dict` | The applicable requirements for the project. |
| `client.generate_report(project, ...)` | `dict` | Generate a PDF report; returns `{url, expires, fileName}`. |

## check_compliance

Returns a dict with a top-level `mandatoryRequirementsMet` flag and a
status object for each category:

- `envelopeStatus`
- `interiorLightingStatus`
- `exteriorLightingStatus`
- `renewableStatus`
- `energyCreditStatus`

```python
compliance = client.check_compliance(project)
if compliance["mandatoryRequirementsMet"]:
    ...
```

## check_requirements

Returns the applicable requirements payload for the project. Like
`check_compliance`, it's a single synchronous call — no polling.

```python
requirements = client.check_requirements(project)
```

## generate_report

Builds a PDF report. The PDF is stored in S3; the API returns a
**short-lived presigned URL** (expires within a few minutes) plus the
file name:

```python
report = client.generate_report(project)
# {"url": "...", "expires": "in 5 minutes", "fileName": "report...pdf"}
```

### Signature

```python
client.generate_report(
    project,
    envelope=True,
    extlighting=True,
    intlighting=True,
    mechanical=True,
    download=False,
    download_dir=None,
)
```

- The four section flags toggle which sections appear in the report
  (all default to `True`).
- `download=True` fetches the PDF from the presigned URL and saves it
  using the server-provided `fileName`. `download_dir` defaults to the
  user's `~/Downloads` folder.

```python
report = client.generate_report(project, download=True)                      # ~/Downloads
report = client.generate_report(project, download=True, download_dir="./out")
```

## Don't

- Don't try to open the report in a browser from library code — this
  method intentionally returns metadata only. If a browser is wanted,
  the caller does `webbrowser.open(report["url"])`.
- Don't cache the presigned `url` — it expires within minutes.
  Re-call `generate_report` to get a fresh one.
