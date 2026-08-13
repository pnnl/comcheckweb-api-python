"""Example: exterior lighting operations.

Exterior lighting is managed at the ExteriorUse granularity.  Each ExteriorUse
lives directly under lighting.exteriorUse[] (no parent building area needed)
and carries exactly one ExteriorLightingSpace whose fixture[] holds the
fixtures.

Zone type
---------
Before exterior compliance can be evaluated, set a real exterior lighting zone
type on the project.  Adding an ExteriorUse while the zone is still
EXT_ZONE_UNSPECIFIED emits a warning — call
set_exterior_lighting_zone_type_in_project to fix it.
"""

import logging
import os
from dotenv import load_dotenv

from comcheck_api import (
    COMcheckClient,
    project_exterior_lighting_operations as el_ops,
)

# The library logs API failures via logging.getLogger(__name__) but never
# configures a handler (as a library shouldn't). Configure logging here so
# those error logs — including the server's response body — are visible.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
from comcheck_api.defaults import (
    get_default_exterior_lighting_area_template,
    get_default_fixture_template,
)
from comcheck_api.types.core_types import (
    ExteriorLightingZoneTypeOptions,
    ExteriorUseTypeOptions,
    LightingTypeOptions,
)

load_dotenv(override=True)
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY") or "your-api-key-here")

# Fetch an existing project so changes can be saved back to the account.
# (update_project persists to the server; it requires a project that already
# exists there, so we start from a fetched project rather than a local
# template.)
project = client.get_project("your-project-id")
if not project:
    raise ValueError("Project not found")
project_id = str(project.id)


# ── Step 1: Set the exterior lighting zone type ───────────────────────────────
# Must be set to a real zone before exterior compliance can be evaluated.
project = el_ops.set_exterior_lighting_zone_type_in_project(
    project, ExteriorLightingZoneTypeOptions.EXT_ZONE_NEIGHBORHOOD_BUS_DISTRICT
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"Zone type set: {project.lighting.exteriorLightingZoneType}")

# ── Step 2: Add an ExteriorUse with a fixture already populated ───────────────
fixture = get_default_fixture_template()
fixture.description = "Parking LED"
fixture.fixtureType = LightingTypeOptions.LED
fixture.fixtureWattage = 150.0
fixture.quantity = 8

exterior_use = get_default_exterior_lighting_area_template()
exterior_use.areaDescription = "Main Parking Area"
exterior_use.exteriorType = ExteriorUseTypeOptions.EXTERIOR_PARKING_AREA
exterior_use.useQuantity = 5000.0
exterior_use.quantityUnits = "sq ft"
exterior_use.exteriorLightingSpace = exterior_use.exteriorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = el_ops.add_exterior_lighting_area_to_project(project, exterior_use)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"ExteriorUse added: {exterior_use.areaDescription!r}")

# ── Step 3: List all exterior uses ────────────────────────────────────────────
keys = el_ops.get_exterior_lighting_area_keys_from_project(project)
print(f"Exterior uses: {keys}")

# ── Step 4: Update the ExteriorUse (change quantity) ─────────────────────────
project = el_ops.update_exterior_lighting_area_in_project(
    project,
    "Main Parking Area",
    {"useQuantity": 6000.0},
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("ExteriorUse updated: useQuantity → 6000.0")

# ── Step 5: Add a second fixture by updating the lighting space ───────────────
# Use direct attribute access (not get_by_path, which returns Any) so
# `exterior_use` keeps its real type for editor autocomplete and type checking.
if not project.lighting or not project.lighting.exteriorUse:
    raise ValueError("Project has no exterior uses (exteriorUse)")
exterior_use = next(
    exterior_use
    for exterior_use in project.lighting.exteriorUse
    if exterior_use.areaDescription == "Main Parking Area"
)
existing_fixtures = list(exterior_use.exteriorLightingSpace.fixture or [])

new_fixture = get_default_fixture_template()
new_fixture.description = "Entrance LED"
new_fixture.fixtureWattage = 80.0
new_fixture.quantity = 2

updated_space = exterior_use.exteriorLightingSpace.model_copy(
    deep=True,
    update={"fixture": existing_fixtures + [new_fixture]},
)
project = el_ops.update_exterior_lighting_area_in_project(
    project,
    "Main Parking Area",
    {
        "exteriorLightingSpace": updated_space.model_dump(
            mode="python", exclude_unset=True
        )
    },
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("Second fixture added to Main Parking Area")

# ── Step 6: Remove the ExteriorUse ───────────────────────────────────────────
project = el_ops.remove_exterior_lighting_area_from_project(
    project, "Main Parking Area"
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("ExteriorUse removed: 'Main Parking Area'")

keys = el_ops.get_exterior_lighting_area_keys_from_project(project)
print(f"Remaining exterior uses: {keys}")
