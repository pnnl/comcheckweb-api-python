import os
from copy import deepcopy
from functools import reduce
from typing import Callable

from dotenv import load_dotenv

from comcheck_api import COMcheckClient
from comcheck_api.components.envelope import ag_wall
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.constants.envelope_constants import DEFAULT_AG_WALL, DEFAULT_ROOF, DEFAULT_FLOOR
from comcheck_api.projectOperations.project_building_area_operations import add_building_area_to_project
from comcheck_api.projectOperations.project_envelope_operations import add_ag_wall_to_project, add_roof_to_project, \
    add_floor_to_project
from comcheck_api.types import OrientationOptions, ComBuilding, AssemblyTypeEnum, WallTypeOptions, AgWall, Roof, Floor, \
    WholeBldgUse, RoofTypeOptions, FloorTypeOptions

# Load environment variables
os.environ["COM_API_KEY"] = "g85IQHH0ds1qWmK68zGfOaBV0jyRcX4bP462DqTb"

api_key = os.getenv("COM_API_KEY")
#if not api_key:
#    pytest.fail("COM_API_KEY is not set in environment variables.")

client = COMcheckClient()
client.set_api_key(api_key)

#################Functional utility ####################
# project = add_building_area_to_project(project, building_area)
ProjectStep = Callable[[ComBuilding], ComBuilding]

def with_ag_wall(
    building_area_key: str,
    new_ag_wall: AgWall,
) -> ProjectStep:
    def step(project: ComBuilding) -> ComBuilding:
        return add_ag_wall_to_project(
            project,
            building_area_key,
            new_ag_wall,
        )
    return step

def with_roof(
    building_area_key: str,
    new_roof: Roof,
) -> ProjectStep:
    def step(project: ComBuilding) -> ComBuilding:
        return add_roof_to_project(
            project,
            building_area_key,
            new_roof,
        )
    return step

def with_floor(
    building_area_key: str,
    new_floor: Floor,
) -> ProjectStep:
    def step(project: ComBuilding) -> ComBuilding:
        return add_floor_to_project(
            project,
            building_area_key,
            new_floor,
        )
    return step

def with_new_building_area(
    new_building_area: WholeBldgUse,
) -> ProjectStep:
    def step(project: ComBuilding) -> ComBuilding:
        return add_building_area_to_project(
            project,
            new_building_area,
        )
    return step

def flow(*steps: ProjectStep) -> ProjectStep:
    def composed(project: ComBuilding) -> ComBuilding:
        return reduce(lambda acc, f: f(acc), steps, project)
    return composed

############### Begin code ############################

def get_project(project_name: str=None):
    project_list = client.list_projects()
    for project in project_list:
        if project["name"].lower() == project_name.lower():
            return client.get_project(project["_id"])
    return None

def create_ag_walls(cavity_r: float=0.0, cont_r:float=0.0, assembly_type: WallTypeOptions = WallTypeOptions.WOOD_FRAME_16_AG_WALL, orientation: OrientationOptions=OrientationOptions.NORTH) -> AgWall:
    ag_wall_copy = deepcopy(DEFAULT_AG_WALL)
    ag_wall_copy.description = f"Exterior Wall {str(orientation)}"
    ag_wall_copy.cavityRValue = cavity_r
    ag_wall_copy.continuousRValue = cont_r
    ag_wall_copy.wallType = assembly_type
    ag_wall_copy.orientation = orientation
    return ag_wall_copy


project = get_project("API Test Project")

building_area = deepcopy(DEFAULT_BUILDING_AREA)
building_area.areaDescription = "Default Building Area"
building_area.floorArea = 1000

ag_wall_north = create_ag_walls(20.0, 10.0, orientation=OrientationOptions.NORTH)
ag_wall_south = create_ag_walls(20.0, 10.0, orientation=OrientationOptions.SOUTH)
ag_wall_east = create_ag_walls(20.0, 10.0, orientation=OrientationOptions.EAST)
ag_wall_west = create_ag_walls(20.0, 10.0, orientation=OrientationOptions.WEST)

roof = deepcopy(DEFAULT_ROOF)
roof.description = "Default Roof"
roof.cavityRValue = 30.0
roof.continuousRValue = 10.0
roof.roofType = RoofTypeOptions.ABOVE_DECK_ROOF

floor = deepcopy(DEFAULT_FLOOR)
floor.description = "Default Floor"
floor.cavityRValue = 30.0
floor.continuousRValue = 10.0
floor.floorType = FloorTypeOptions.ALL_WOOD_JOIST_TRUSS_FLOOR

bldg_area_key = building_area.key


process_project = flow(
    with_new_building_area(building_area),
    with_roof(bldg_area_key, roof),
    with_ag_wall(bldg_area_key, ag_wall_south),
    with_ag_wall(bldg_area_key, ag_wall_north),
    with_ag_wall(bldg_area_key, ag_wall_east),
    with_ag_wall(bldg_area_key, ag_wall_west),
    with_floor(bldg_area_key, floor),
)

project = process_project(project)

client.update_project(project.id, project)
