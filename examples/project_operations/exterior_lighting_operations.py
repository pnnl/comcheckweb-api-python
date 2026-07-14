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

import os
from dotenv import load_dotenv

from comcheck_api import (
    COMcheckClient,
    project_exterior_lighting_operations as el_ops,
)
from comcheck_api.defaults import (
    get_default_exterior_lighting_area_template,
    get_default_fixture_template,
    get_default_project_template,
)
from comcheck_api.types.core_types import (
    ExteriorLightingZoneTypeOptions,
    ExteriorUseTypeOptions,
    LightingTypeOptions,
)

load_dotenv()
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY") or "your-api-key-here")

project = get_default_project_template()

# ── Step 1: Set the exterior lighting zone type ───────────────────────────────
# Must be set to a real zone before exterior compliance can be evaluated.
project = el_ops.set_exterior_lighting_zone_type_in_project(
    project, ExteriorLightingZoneTypeOptions.EXT_ZONE_NEIGHBORHOOD_BUS_DISTRICT
)
print(f"Zone type set: {project.lighting.exteriorLightingZoneType}")

# ── Step 2: Add an ExteriorUse with a fixture already populated ───────────────
fixture = get_default_fixture_template()
fixture.description = "Parking LED"
fixture.lightingType = LightingTypeOptions.LED
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
print("ExteriorUse updated: useQuantity → 6000.0")

# ── Step 5: Add a second fixture by updating the lighting space ───────────────
exterior_uses = project.get_by_path("lighting.exteriorUse")
eu = next(e for e in exterior_uses if e.areaDescription == "Main Parking Area")
existing_fixtures = list(eu.exteriorLightingSpace.fixture or [])

new_fixture = get_default_fixture_template()
new_fixture.description = "Entrance LED"
new_fixture.fixtureWattage = 80.0
new_fixture.quantity = 2

updated_space = eu.exteriorLightingSpace.model_copy(
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
print("Second fixture added to Main Parking Area")

# ── Step 6: Remove the ExteriorUse ───────────────────────────────────────────
project = el_ops.remove_exterior_lighting_area_from_project(
    project, "Main Parking Area"
)
print("ExteriorUse removed: 'Main Parking Area'")

keys = el_ops.get_exterior_lighting_area_keys_from_project(project)
print(f"Remaining exterior uses: {keys}")
