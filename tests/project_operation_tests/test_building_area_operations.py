import pytest
from copy import deepcopy

from comcheck_api.client import COMcheckClient
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.project_operations import project_building_area_operations
from comcheck_api.defaults import (
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


def test_add_building_area_duplicate_description_raises(project: ComBuilding):
    existing = project.get_by_path("lighting.wholeBldgUse", [])
    assert existing, "fixture project must have at least one building area"
    duplicate_desc = getattr(existing[0], "areaDescription")

    duplicate = get_default_building_area_template()
    duplicate.areaDescription = duplicate_desc

    with pytest.raises(ValueError, match="areaDescription"):
        project_building_area_operations.add_building_area_to_project(
            project, duplicate
        )


def test_update_building_area_duplicate_description_raises(project: ComBuilding):
    local = project.model_copy(deep=True)

    area_a = get_default_building_area_template()
    area_b = get_default_building_area_template()
    local = project_building_area_operations.add_building_area_to_project(local, area_a)
    local = project_building_area_operations.add_building_area_to_project(local, area_b)

    with pytest.raises(ValueError, match="areaDescription"):
        project_building_area_operations.update_building_area_in_project(
            local, area_b.key, {"areaDescription": area_a.areaDescription}
        )


def test_get_building_area_keys(project: ComBuilding):
    local_project = project.model_copy(deep=True)
    local_project.lighting.wholeBldgUse = [
        deepcopy(DEFAULT_BUILDING_AREA),
        deepcopy(DEFAULT_BUILDING_AREA),
    ]

    result = project_building_area_operations.get_building_area_keys_from_project(
        local_project
    )

    assert result == [
        {
            "key": DEFAULT_BUILDING_AREA.key,
            "areaDescription": DEFAULT_BUILDING_AREA.areaDescription,
        },
        {
            "key": DEFAULT_BUILDING_AREA.key,
            "areaDescription": DEFAULT_BUILDING_AREA.areaDescription,
        },
    ]


def test_get_building_area_keys_empty(project: ComBuilding):
    local_project = project.model_copy(deep=True)
    local_project.lighting.wholeBldgUse = []

    result = project_building_area_operations.get_building_area_keys_from_project(
        local_project
    )

    assert result == []


def test_get_building_area_keys_no_lighting(project: ComBuilding):
    local_project = project.model_copy(deep=True, update={"lighting": None})

    result = project_building_area_operations.get_building_area_keys_from_project(
        local_project
    )

    assert result == []
