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


def generate_assembly(
    bldg_use_key: str, name: str, assembly_type: AssemblyType
) -> Dict[str, Any]:
    """Generate an assembly configuration by combining defaults with custom values.

    Args:
        bldg_use_key: The building use key identifier.
        name: The custom name for the assembly.
        assembly_type: The type of assembly (e.g., 'Window', 'AgWall', etc.).

    Returns:
        A dictionary containing the complete assembly configuration.
    """
    default_assembly = DEFAULT_ASSEMBLIES[assembly_type]
    description = type_map_description(assembly_type)

    result: Dict[str, Any] = {
        **default_assembly.model_dump(mode="json"),
        "bldgUseKey": bldg_use_key,
        "assemblyType": f"{description}:{name}",
    }
    return result
