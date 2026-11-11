# COMcheck API — Python Package

Type-safe Python client for the PNNL's [COMcheck Web](https://comcheck.energycode.pnl.gov/) for building energy code compliance verification.

## Current Status

This package is under active development. Here is the current support status for each section:

| Section | Status |
|---|---|
| Building Area | Supported |
| Envelope (roofs, walls, floors, windows, doors, skylights, thermal bridges) | Supported |
| Interior Lighting | Supported |
| Exterior Lighting | Supported |
| Compliance Simulation | Supported |
| Mechanical | Supported (requirements must be filled out on COMcheck Web) |
| Credits | Supported |
| Renewable Energy | Supported |

Mechanical requirements (`requirementAnswer` on HVAC systems, fan systems, plants, and water heaters) are not supported by this package. Save the project, then open it on [COMcheck Web](https://comcheck.energycode.pnl.gov/) to fill them out.

## Features

- **Type-safe** --- Pydantic models for all API inputs and outputs
- **Envelope management** --- Roofs, walls, floors, windows, doors, skylights, and thermal bridges
- **Lighting management** --- Interior lighting (activity uses + fixtures) and exterior lighting (uses, zone type + fixtures)
- **Compliance simulation** --- Start simulations and retrieve results programmatically
- **Validation** --- JSON schema validation and Pydantic type checking at every boundary

## Quick Start

```python
from comcheck_api import COMcheckClient

# Initialize the client
client = COMcheckClient(api_key="your-api-key")

# Fetch a project
project = client.get_project("project-id")

# Run a compliance simulation
session_id = client.start_run_simulation(project)
status = client.get_simulation_status(session_id)
result = client.get_simulation_result(session_id)
```

## Installation

```bash
pip install comcheck_api
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add comcheck_api
```

## Requirements

- Python >= 3.12
- A valid COMcheck API key

## Package Overview

| Module | Description |
|--------|-------------|
| [`comcheck_api.client`](api/client.md) | High-level client interface (`COMcheckClient`), including [simulation](api/simulation.md) and [compliance & reports](api/compliance.md) |
| [`comcheck_api.project_operations`](api/operations/building-area.md) | [Building area](api/operations/building-area.md), [envelope](api/operations/envelope.md), [interior lighting](api/operations/interior-lighting.md), [exterior lighting](api/operations/exterior-lighting.md), [mechanical](api/operations/mechanical.md), [credits](api/operations/credits.md), and [renewable energy](api/operations/renewable-energy.md) operations |
| [`comcheck_api.defaults`](api/defaults.md) | Default templates for projects and building components |
| [`comcheck_api.introspection`](api/introspection.md) / [`comcheck_api.validation`](api/introspection.md) | Runtime discovery of SDK capabilities and project data validation |
| [`comcheck_api.types`](types-guide.md) | Pydantic models for projects and building components |
