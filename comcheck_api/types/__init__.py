"""Type definitions for the comcheckweb-api-python package.

This module re-exports all generated types from api_types and core_types
so package users can import them directly.
"""

from types import ModuleType
from typing import List

# Import modules to access their __all__ if defined
from . import api_types as _api_types
from . import common_types as _common_types
from . import core_types as _core_types
from .api_types import *  # noqa: F401, F403
from .common_types import *  # noqa: F401, F403
from .core_types import *  # noqa: F401, F403


def _collect_exports(mod: ModuleType) -> List[str]:
    """Collect exportable names from a module."""
    if hasattr(mod, "__all__"):
        return list(mod.__all__)
    return [name for name in dir(mod) if not name.startswith("_")]


# Build __all__ from all modules
__all__ = []

for name in _collect_exports(_common_types):
    if name not in __all__:
        __all__.append(name)

for name in _collect_exports(_api_types):
    if name not in __all__:
        __all__.append(name)

for name in _collect_exports(_core_types):
    if name not in __all__:
        __all__.append(name)
