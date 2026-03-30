"""COMcheckWeb API package.

Example:
    from comcheck_api.client import COMcheckClient
    from comcheck_api.project_operations import (
        project_building_area_operations,
        project_envelope_operations,
    )
    from comcheck_api.utilities import export_to_json
    from comcheck_api.utilities.get_project_default import (
        get_default_ag_wall_template,
        get_default_building_area_template,
    )
    from comcheck_api.types import AssemblyType, AgWall
"""

# COMcheck API Client
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
from .utilities import get_project_default

# Project Operations
from .project_operations import (
    project_building_area_operations,
    project_envelope_operations,
)

# Utility Functions
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
    # Defaults
    "get_project_default",
    # Project Operations
    "project_building_area_operations",
    "project_envelope_operations",
    # Utilities
    "utilities",
    # Types
    "types",
]
