"""Example of using envelope component managers."""

from comcheck_api.managers.components.envelope.ag_wall import AgWallListManager
from comcheck_api.managers.components.envelope.roof import RoofListManager
from pytest_fixtures.components import SAMPEL_SKYLIGHT, SAMPLE_AG_WALL, SAMPLE_ROOF

# Example 1: Working with above-grade walls
ag_wall_manager = AgWallListManager([])

# Add a new wall
wall = ag_wall_manager.add_new(SAMPLE_AG_WALL)
print("Added wall:", wall)

# Add a thermal bridge to the wall
ag_wall_manager.add_new_thermal_bridge(wall[0])
print("\nWall with thermal bridge:", wall)

# Example 2: Working with roofs
roof_manager = RoofListManager([])

# Add a new roof
roof = roof_manager.add_new(SAMPLE_ROOF)
print("\nAdded roof:", roof)

roof_manager.add_new_skylight(roof, SAMPEL_SKYLIGHT)

print("\nAdded skylight:", roof_manager.get_all())
