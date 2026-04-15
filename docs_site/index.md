# COMcheck API - Python Client

Type-safe Python client for the PNNL's [COMcheck Web](https://comcheck.energycode.pnl.gov/) for building energy code compliance verification.

## Features

- **Type-safe** --- Pydantic models for all API inputs and outputs
- **Envelope management** --- Roofs, walls, floors, windows, doors, skylights, and thermal bridges
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
| [`comcheck_api.client`](api/client.md) | High-level client interface |
| [`comcheck_api.project_operations`](api/operations/building-area.md) | [Building area](api/operations/building-area.md) and [envelope](api/operations/envelope.md) operations |
