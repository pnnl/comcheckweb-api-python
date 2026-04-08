import pytest

from comcheck_api.client import COMcheckClient
from comcheck_api.project_operations import project_envelope_operations
from comcheck_api.utilities.get_project_default import (
    get_default_ag_wall_template,
    get_default_bg_wall_template,
    get_default_door_template,
    get_default_floor_template,
    get_default_roof_template,
    get_default_skylight_template,
    get_default_window_template,
)
from comcheck_api.types.core_types import *
from tests.project_operation_tests.conftest import (
    ComponentOperationConfig,
    run_flat_assembly_lifecycle,
    run_nested_assembly_lifecycle,
)

ASSEMBLY_CONFIGS = [
    ComponentOperationConfig(
        name="roof",
        path="envelope.roof",
        default_factory=get_default_roof_template,
        add_component_to_project=project_envelope_operations.add_roof_to_project,
        update_component_in_project=project_envelope_operations.update_roof_in_project,
        remove_component_from_project=project_envelope_operations.remove_roof_from_project,
    ),
    ComponentOperationConfig(
        name="floor",
        path="envelope.floor",
        default_factory=get_default_floor_template,
        add_component_to_project=project_envelope_operations.add_floor_to_project,
        update_component_in_project=project_envelope_operations.update_floor_in_project,
        remove_component_from_project=project_envelope_operations.remove_floor_from_project,
    ),
    ComponentOperationConfig(
        name="agWall",
        path="envelope.agWall",
        default_factory=get_default_ag_wall_template,
        add_component_to_project=project_envelope_operations.add_ag_wall_to_project,
        update_component_in_project=project_envelope_operations.update_ag_wall_in_project,
        remove_component_from_project=project_envelope_operations.remove_ag_wall_from_project,
    ),
    ComponentOperationConfig(
        name="bgWall",
        path="envelope.bgWall",
        default_factory=get_default_bg_wall_template,
        add_component_to_project=project_envelope_operations.add_bg_wall_to_project,
        update_component_in_project=project_envelope_operations.update_bg_wall_in_project,
        remove_component_from_project=project_envelope_operations.remove_bg_wall_from_project,
    ),
    ComponentOperationConfig(
        name="window",
        path="envelope.window",
        default_factory=get_default_window_template,
        add_component_to_project=project_envelope_operations.add_window_to_project,
        update_component_in_project=project_envelope_operations.update_window_in_project,
        remove_component_from_project=project_envelope_operations.remove_window_from_project,
    ),
    ComponentOperationConfig(
        name="skylight",
        path="envelope.skylight",
        default_factory=get_default_skylight_template,
        add_component_to_project=project_envelope_operations.add_skylight_to_project,
        update_component_in_project=project_envelope_operations.update_skylight_in_project,
        remove_component_from_project=project_envelope_operations.remove_skylight_from_project,
    ),
    ComponentOperationConfig(
        name="door",
        path="envelope.door",
        default_factory=get_default_door_template,
        add_component_to_project=project_envelope_operations.add_door_to_project,
        update_component_in_project=project_envelope_operations.update_door_in_project,
        remove_component_from_project=project_envelope_operations.remove_door_from_project,
    ),
]

NESTED_ASSEMBLY_CONFIGS = [
    ComponentOperationConfig(
        name="window",
        path="envelope.agWall[0].window",
        default_factory=get_default_window_template,
        add_component_to_project=project_envelope_operations.add_window_to_project,
        update_component_in_project=project_envelope_operations.update_window_in_project,
        remove_component_from_project=project_envelope_operations.remove_window_from_project,
    ),
    ComponentOperationConfig(
        name="skylight",
        path="envelope.roof[0].skylight",
        default_factory=get_default_skylight_template,
        add_component_to_project=project_envelope_operations.add_skylight_to_project,
        update_component_in_project=project_envelope_operations.update_skylight_in_project,
        remove_component_from_project=project_envelope_operations.remove_skylight_from_project,
    ),
    ComponentOperationConfig(
        name="door",
        path="envelope.agWall[0].door",
        default_factory=get_default_door_template,
        add_component_to_project=project_envelope_operations.add_door_to_project,
        update_component_in_project=project_envelope_operations.update_door_in_project,
        remove_component_from_project=project_envelope_operations.remove_door_from_project,
    ),
]


@pytest.mark.parametrize(
    "assembly_config",
    ASSEMBLY_CONFIGS,
    ids=lambda c: c.name,
)
def test_assembly_operations(
    client: COMcheckClient,
    project: ComBuilding,
    assembly_config: ComponentOperationConfig,
    building_area_key: str,
    maybe_apply_and_reload,
):
    project.projectType = ProjectTypeOptions.ALTERATION
    run_flat_assembly_lifecycle(
        client=client,
        project=project,
        config=assembly_config,
        building_area_key=building_area_key,
    )


@pytest.mark.parametrize(
    "nested_assembly_config",
    NESTED_ASSEMBLY_CONFIGS,
    ids=lambda c: c.name,
)
def test_nested_assembly_operations(
    client: COMcheckClient,
    project: ComBuilding,
    nested_assembly_config: ComponentOperationConfig,
    building_area_key: str,
    maybe_apply_and_reload,
):
    project.projectType = ProjectTypeOptions.NEW_CONSTRUCTION
    run_nested_assembly_lifecycle(
        client=client,
        project=project,
        config=nested_assembly_config,
        building_area_key=building_area_key,
    )
