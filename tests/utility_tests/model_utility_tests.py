from comcheck_api.constants.envelope_constants import DEFAULT_BG_WALL, DEFAULT_DOOR
from comcheck_api.utilities.model_utilities import find_objects_by_ids

def test_model_search():
    bg_wall = DEFAULT_BG_WALL.model_copy(deep=True)
    door = DEFAULT_DOOR.model_copy(deep=True)
    bg_wall.add_subcomponent(door)

    found_objects = find_objects_by_ids(bg_wall, [door.assemblyType], id_field="assemblyType")
    assert len(found_objects) == 1
    assert found_objects[0] == door