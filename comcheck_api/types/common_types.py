"""Common utility types used throughout the comcheckweb package.

This module contains generic types, enums, and type aliases that are used
across multiple modules but aren't generated from schemas.
"""

from enum import Enum
from typing import Literal

from comcheck_api.types.core_types import ActivityUse, ExteriorUse

# Type alias for assembly types
AssemblyType = Literal[
    "Roof", "Skylight", "AgWall", "Floor", "BgWall", "Window", "Door"
]

# InteriorSpace and ExteriorArea are aliases for the schema-generated
# ActivityUse and ExteriorUse models — used to disambiguate interior lighting
# spaces from exterior lighting areas in code that isn't schema-generated.
InteriorSpace = ActivityUse
ExteriorArea = ExteriorUse


# Runtime-friendly enum (useful when you need a value at runtime)
class AssemblyTypeEnum(str, Enum):
    """Enum representation of assembly types for runtime validation and iteration."""

    ROOF = "Roof"
    SKYLIGHT = "Skylight"
    AGWALL = "AgWall"
    FLOOR = "Floor"
    BGWALL = "BgWall"
    WINDOW = "Window"
    DOOR = "Door"


__all__ = [
    "AssemblyType",
    "AssemblyTypeEnum",
    "InteriorSpace",
    "ExteriorArea",
]
