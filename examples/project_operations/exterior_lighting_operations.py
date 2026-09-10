"""Example: exterior lighting operations.

Exterior lighting is managed at the ExteriorArea granularity.  In the COMcheck
API schema, an exterior lighting area is represented by the ``ExteriorUse``
model.  Each ExteriorArea lives directly under lighting.exteriorUse[] (no
parent building area needed) and carries exactly one ExteriorLightingSpace
whose fixture[] holds the fixtures.

Fixtures themselves can be batch added/updated/removed via
update_fixtures_in_exterior_area, matched by fixtureType (the
schema-documented uniqueness key for fixtures within a lighting space).

Zone type
---------
Before exterior compliance can be evaluated, set a real exterior lighting zone
type on the project.  Adding an ExteriorArea while the zone is still
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
from comcheck_api.defaults import (
    get_default_exterior_area_template,
    get_default_fixture_template,
)
from comcheck_api.types.core_types import (
    ExteriorLightingZoneTypeOptions,
    ExteriorUseTypeOptions,
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

# ── Step 2: Add an ExteriorArea with a fixture already populated ─────────────
fixture = get_default_fixture_template()
fixture.description = "Parking LED"
# fixtureType is the required identifier (a description string). lightingType
# is optional and marked for deprecation, so it is left unset here.
fixture.fixtureType = "Parking LED"
fixture.fixtureWattage = 150.0
fixture.quantity = 8

exterior_area = get_default_exterior_area_template()
exterior_area.areaDescription = "Main Parking Area"
exterior_area.exteriorType = ExteriorUseTypeOptions.EXTERIOR_PARKING_AREA
exterior_area.useQuantity = 5000.0
exterior_area.quantityUnits = "sq ft"
exterior_area.exteriorLightingSpace = exterior_area.exteriorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = el_ops.add_exterior_area_to_project(project, exterior_area)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print(f"ExteriorArea added: {exterior_area.areaDescription!r}")

# ── Step 3: List all exterior areas ───────────────────────────────────────────
keys = el_ops.get_exterior_area_keys_from_project(project)
print(f"Exterior areas: {keys}")

# ── Step 4: Update the ExteriorArea (change quantity) ────────────────────────
project = el_ops.update_exterior_area_in_project(
    project,
    "Main Parking Area",
    {"useQuantity": 6000.0},
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("ExteriorArea updated: useQuantity → 6000.0")

# ── Step 5: Add a second fixture via the batch fixture operation ─────────────
# update_fixtures_in_exterior_area matches fixtures by fixtureType — upserts
# either add a new fixture or replace an existing one with the same
# fixtureType, and remove_fixture_types deletes by fixtureType.  It handles
# the read-modify-write of exteriorLightingSpace.fixture[] internally, so
# there's no need to fetch and merge the existing fixture list by hand.
new_fixture = get_default_fixture_template()
new_fixture.description = "Entrance LED"
new_fixture.fixtureType = "Entrance LED"
new_fixture.fixtureWattage = 80.0
new_fixture.quantity = 2

project = el_ops.update_fixtures_in_exterior_area(
    project,
    "Main Parking Area",
    upserts=[new_fixture],
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("Second fixture added to Main Parking Area")

# ── Step 6: Update the first fixture and remove the second, in one batch ─────
updated_fixture = get_default_fixture_template()
updated_fixture.fixtureType = "Parking LED"  # matches the fixture added in Step 2
updated_fixture.fixtureWattage = 120.0
updated_fixture.quantity = 10

project = el_ops.update_fixtures_in_exterior_area(
    project,
    "Main Parking Area",
    upserts=[updated_fixture],
    remove_fixture_types=["Entrance LED"],
)

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("Parking LED updated to 120.0 W, Entrance LED removed")

# ── Step 7: Remove the ExteriorArea ──────────────────────────────────────────
project = el_ops.remove_exterior_area_from_project(project, "Main Parking Area")

project = client.update_project(project_id, project)
if not project:
    raise ValueError("Project not found after update")
print("ExteriorArea removed: 'Main Parking Area'")

keys = el_ops.get_exterior_area_keys_from_project(project)
print(f"Remaining exterior areas: {keys}")
