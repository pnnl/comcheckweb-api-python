"""COMcheckWeb API package.

Example:
    from comcheckweb.comcheck_client import COMcheckClient
    from comcheckweb.project_operations import (
        project_building_area_operations,
        project_envelope_operations,
    )
    from comcheckweb.utilities import export_to_json
    from comcheckweb.get_project_default import (
        get_default_ag_wall_template,
        get_default_building_area_template,
    )
    from comcheckweb.types import AssemblyType, AgWall
"""

# COMcheck API Client
from .comcheck_client import COMcheckClient

# Project Defaults
from . import get_project_default

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
