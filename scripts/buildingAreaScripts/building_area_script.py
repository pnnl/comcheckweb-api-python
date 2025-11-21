"""Script to test building area manager."""

import os
import sys

# Add compcheck_api to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from comcheck_api.components.building_area import BuildingAreaListManager
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA

manager = BuildingAreaListManager([])

manager.add_new(DEFAULT_BUILDING_AREA)

print("Building area list:", manager.get_all())
