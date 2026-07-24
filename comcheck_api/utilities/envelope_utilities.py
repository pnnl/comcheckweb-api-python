"""Envelope-related utility functions for COMcheck projects."""

from typing import Any, Dict

from comcheck_api.constants.envelope_constants import DEFAULT_ASSEMBLIES
from comcheck_api.types.common_types import AssemblyType


def type_map_description(type_name: str) -> str:
    """Map assembly type to a human-readable description.

    Args:
        type_name: The assembly type identifier.

    Returns:
        A formatted description string.
    """
    mapping = {
        "AgWall": "Ext Wall",
        "BgWall": "Basement",
    }
    return mapping.get(type_name, type_name)
