"""COMcheckWeb API - Python client for programmatic building energy code compliance.

This package provides a type-safe, automated interface to the U.S. Department of
Energy's COMcheck Web API for building energy code compliance verification.

Quick Start:
    >>> from comcheck_api import COMcheckClient
    >>> client = COMcheckClient(api_key="your-api-key")
    >>> project = client.get_project("123")
    >>> session_id = client.start_run_simulation(project)

Basic Usage:
    from comcheck_api import (
        COMcheckClient,
        COMCheckHTTPError,
        export_to_json,
    )

    client = COMcheckClient(api_key="your-key")

    try:
        projects = client.list_projects()
        export_to_json(projects, "projects.json")
    except COMCheckHTTPError as e:
        print(f"HTTP error: {e.status_code}")

Advanced Usage:
    from comcheck_api import (
        COMcheckClient,
        project_envelope_operations,
    )
    from comcheck_api.types import AgWall, ComBuilding

    # For type imports, use the types submodule
    # from comcheck_api.types import ...

    # For advanced utilities, use the utilities submodule
    # from comcheck_api.utilities import ...
"""

# Client
from .client import COMcheckClient

# Exceptions
from .exceptions import (
    COMCheckAPIError,
    COMCheckHTTPError,
    COMCheckConnectionError,
    COMCheckValidationError,
    COMCheckSimulationError,
    COMCheckProjectNotFoundError,
)

# Project Defaults
from . import defaults

# Project Operations
from .project_operations import (
    project_building_area_operations,
    project_envelope_operations,
)

# Utilities
from . import utilities

# Types
from . import types

__all__ = [
    # Client
    "COMcheckClient",
    # Exceptions
    "COMCheckAPIError",
    "COMCheckHTTPError",
    "COMCheckConnectionError",
    "COMCheckValidationError",
    "COMCheckSimulationError",
    "COMCheckProjectNotFoundError",
    # Project Defaults
    "defaults",
    # Project Operations
    "project_building_area_operations",
    "project_envelope_operations",
    # Utilities
    "utilities",
    # Types
    "types",
]
