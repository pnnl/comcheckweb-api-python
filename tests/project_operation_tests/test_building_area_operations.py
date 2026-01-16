import pytest

from comcheck_api.client import COMcheckClient
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.utilities.get_project_default import (
    get_default_building_area_template,
)
from comcheck_api.types.core_types import *
from tests.project_operation_tests.conftest import (
    ComponentOperationConfig,
    run_flat_assembly_lifecycle,
)


building_area_config = ComponentOperationConfig(
    name="wholeBldgUse",
    path="lighting.wholeBldgUse",
    default_factory=get_default_building_area_template,
    add_component_to_project=project_building_area_operations.add_building_area_to_project,
    update_component_in_project=project_building_area_operations.update_building_area_in_project,
    remove_component_from_project=project_building_area_operations.remove_building_area_from_project,
    updates={
        "wholeBldgType": WholeBuildingTypeOptions.WHOLE_BUILDING_COURT_HOUSE,
        "areaDescription": "Updated building area description",
        "floorArea": 2500,
    },
)


def test_building_area_operations(
    client: COMcheckClient, project: ComBuilding, maybe_apply_and_reload
):
    project.projectType = ProjectTypeOptions.ALTERATION
    run_flat_assembly_lifecycle(
        client=client,
        project=project,
        config=building_area_config,
    )
