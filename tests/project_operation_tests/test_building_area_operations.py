import pytest

from comcheck_api.comcheck_client import COMcheckClient
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.get_project_default import get_default_building_area_template
from comcheck_api.types.core_types import *
from comcheck_api.utilities.project_utilities import find_component_in_component_list, get_id_from_component
from tests.project_operation_tests.assertions.components import assert_component_added, assert_component_updated, assert_component_removed
from tests.project_operation_tests.conftest import ComponentOperationConfig


building_area_config = ComponentOperationConfig(
    name="wholeBldgUse",
    path="lighting.wholeBldgUse",
    default_factory=get_default_building_area_template,
    add_component_to_project=project_building_area_operations.add_building_area_to_project,
    update_component_in_project=project_building_area_operations.update_building_area_in_project,
    remove_component_from_project=project_building_area_operations.remove_building_area_from_project
)

def test_building_area_operations(client: COMcheckClient, project: ComBuilding, subtests: pytest.Subtests):
    project_id = getattr(project, "id", None)
    assert project_id, f"No id found on project"

    # Run add -> update -> remove sequence to avoid loading same project twice (one for confirming changes and one for the next test)
    with subtests.test(f"{building_area_config.name}: add"):
        default_building_area = get_default_building_area_template()

        updated_project = building_area_config.add_component_to_project(
            project, default_building_area
        )

        target_key = get_id_from_component(default_building_area)
        assert target_key, f"{building_area_config.name} has no key"

        client.update_project(project_id, updated_project)

        reloaded = client.get_project(project_id)

        assert_component_added(project=reloaded, path=building_area_config.path, component_id=target_key, component_name=building_area_config.name)

        project = reloaded

    with subtests.test(f"{building_area_config.name}: update"):
        updates = {
            "wholeBldgType": WholeBuildingTypeOptions.WHOLE_BUILDING_COURT_HOUSE,
            "areaDescription": "Updated building area description",
            "floorArea": 2500,
        }

        whole_bldg_use = project.get_by_path(building_area_config.path, [])
        assert whole_bldg_use, f"Expected {building_area_config.name} at '{building_area_config.path}'"

        target_building_area = find_component_in_component_list(whole_bldg_use, target_key)
        assert target_building_area, f"{building_area_config.name} with id {target_key} was not found"

        updated_project = building_area_config.update_component_in_project(
            project, target_key, updates
        )

        client.update_project(project_id, updated_project)

        reloaded = client.get_project(project_id)

        assert_component_updated(project=reloaded, path=building_area_config.path, updates=updates, component_id=target_key, component_name=building_area_config.name)

        project = reloaded

    with subtests.test(f"{building_area_config.name}: remove"):
        updated_project = building_area_config.remove_component_from_project(
            project, target_key
        )
        client.update_project(project_id, updated_project)

        reloaded = client.get_project(project_id)

        assert_component_removed(project=reloaded, path=building_area_config.path, component_id=target_key, component_name=building_area_config.name)
