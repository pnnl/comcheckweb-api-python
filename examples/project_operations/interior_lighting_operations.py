"""Example: interior lighting operations.

Interior lighting is managed at the ActivityUse granularity.  Each ActivityUse
belongs to a WholeBldgUse (building area) and carries exactly one
InteriorLightingSpace whose fixture[] holds the fixtures.

There are no fixture-level operations — to add, change, or remove a fixture,
edit the activityUse's interiorLightingSpace.fixture[] list and pass the whole
ActivityUse through update_interior_lighting_space_in_project.
"""

import os
from dotenv import load_dotenv

from comcheck_api import (
    COMcheckClient,
    project_building_area_operations as ba_ops,
    project_interior_lighting_operations as il_ops,
)
from comcheck_api.defaults import (
    get_default_interior_lighting_space_template,
    get_default_building_area_template,
    get_default_fixture_template,
)
from comcheck_api.types.core_types import ActivityTypeOptions, LightingTypeOptions

load_dotenv()
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY") or "your-api-key-here")

# Start from the default project template
from comcheck_api.defaults import get_default_project_template

project = get_default_project_template()

# ── Step 1: A building area must exist before adding activity uses ────────────
area = get_default_building_area_template()
area.areaDescription = "Main Office"
project = ba_ops.add_building_area_to_project(project, area)
area_key = area.key
print(f"Building area added: {area.areaDescription!r} (key={area_key})")

# ── Step 2: Add an ActivityUse with a fixture already populated ───────────────
fixture = get_default_fixture_template()
fixture.description = "Recessed LED"
fixture.lightingType = LightingTypeOptions.LED
fixture.fixtureWattage = 20.0
fixture.quantity = 10

activity_use = get_default_interior_lighting_space_template()
activity_use.areaDescription = "Open Office"
activity_use.activityType = ActivityTypeOptions.ACTIVITY_COMMON_OFFICE
activity_use.floorArea = 2000.0
activity_use.interiorLightingSpace = activity_use.interiorLightingSpace.model_copy(
    deep=True, update={"fixture": [fixture]}
)

project = il_ops.add_interior_lighting_space_to_project(project, area_key, activity_use)
print(f"ActivityUse added: {activity_use.areaDescription!r}")

# ── Step 3: List all activity uses in the building area ───────────────────────
keys = il_ops.get_interior_lighting_space_keys_from_project(project, area_key)
print(f"Activity uses in {area.areaDescription!r}: {keys}")

# ── Step 4: Update the ActivityUse (change floor area) ───────────────────────
project = il_ops.update_interior_lighting_space_in_project(
    project,
    area_key,
    "Open Office",
    {"floorArea": 2500.0},
)
print("ActivityUse updated: floorArea → 2500.0")

# ── Step 5: Add a second fixture by updating the lighting space ───────────────
# Retrieve current activityUse to get the existing fixtures
whole_use = project.get_by_path("lighting.wholeBldgUse")
ba = next(a for a in whole_use if a.key == area_key)
au = next(au for au in ba.activityUse if au.areaDescription == "Open Office")
existing_fixtures = list(au.interiorLightingSpace.fixture or [])

new_fixture = get_default_fixture_template()
new_fixture.description = "Pendant LED"
new_fixture.fixtureWattage = 35.0
new_fixture.quantity = 4

updated_space = au.interiorLightingSpace.model_copy(
    deep=True,
    update={"fixture": existing_fixtures + [new_fixture]},
)
project = il_ops.update_interior_lighting_space_in_project(
    project,
    area_key,
    "Open Office",
    {
        "interiorLightingSpace": updated_space.model_dump(
            mode="python", exclude_unset=True
        )
    },
)
print("Second fixture added to Open Office")

# ── Step 6: Remove the ActivityUse ───────────────────────────────────────────
project = il_ops.remove_interior_lighting_space_from_project(
    project, area_key, "Open Office"
)
print("ActivityUse removed: 'Open Office'")

keys = il_ops.get_interior_lighting_space_keys_from_project(project, area_key)
print(f"Remaining activity uses: {keys}")
