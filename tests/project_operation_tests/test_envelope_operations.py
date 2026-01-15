from typing import Callable, Any

import pytest
from dataclasses import dataclass

from comcheck_api.comcheck_client import COMcheckClient
from comcheck_api.project_operations import project_envelope_operations
from comcheck_api.utilities.get_project_default import (
    get_default_ag_wall_template,
    get_default_bg_wall_template,
    get_default_floor_template,
    get_default_roof_template,
    get_default_skylight_template,
    get_default_window_template,
)
from comcheck_api.types.core_types import *
from comcheck_api.utilities.project_utilities import find_component_in_component_list, get_id_from_component
from tests.project_operation_tests.assertions.components import assert_component_added, assert_component_updated, assert_component_removed
from tests.project_operation_tests.conftest import ComponentOperationConfig

def get_building_area_key(project) -> str:
    whole_bldg_use = project.get_by_path("lighting.wholeBldgUse", [])
    assert whole_bldg_use, "No wholeBldgUse found"
    return whole_bldg_use[0].key


ASSEMBLY_CONFIGS = [
    ComponentOperationConfig(
        name="roof",
        path="envelope.roof",
        default_factory=get_default_roof_template,
        add_component_to_project=project_envelope_operations.add_roof_to_project,
        update_component_in_project=project_envelope_operations.update_roof_in_project,
        remove_component_from_project=project_envelope_operations.remove_roof_from_project
    ),
    ComponentOperationConfig(
        name="floor",
        path="envelope.floor",
        default_factory=get_default_floor_template,
        add_component_to_project=project_envelope_operations.add_floor_to_project,
        update_component_in_project=project_envelope_operations.update_floor_in_project,
        remove_component_from_project=project_envelope_operations.remove_floor_from_project
    ),
    ComponentOperationConfig(
        name="agWall",
        path="envelope.agWall",
        default_factory=get_default_ag_wall_template,
        add_component_to_project=project_envelope_operations.add_ag_wall_to_project,
        update_component_in_project=project_envelope_operations.update_ag_wall_in_project,
        remove_component_from_project=project_envelope_operations.remove_ag_wall_from_project
    ),
    ComponentOperationConfig(
        name="bgWall",
        path="envelope.bgWall",
        default_factory=get_default_bg_wall_template,
        add_component_to_project=project_envelope_operations.add_bg_wall_to_project,
        update_component_in_project=project_envelope_operations.update_bg_wall_in_project,
        remove_component_from_project=project_envelope_operations.remove_bg_wall_from_project
    ),
]

NESTED_ASSEMBLY_CONFIGS = [
    ComponentOperationConfig(
        name="window",
        path="envelope.agWall[0].window",
        default_factory=get_default_window_template,
        add_component_to_project=project_envelope_operations.add_window_to_project,
        update_component_in_project=project_envelope_operations.update_window_in_project,
        remove_component_from_project=project_envelope_operations.remove_window_from_project
    ),
    ComponentOperationConfig(
        name="skylight",
        path="envelope.roof[0].skylight",
        default_factory=get_default_skylight_template,
        add_component_to_project=project_envelope_operations.add_skylight_to_project,
        update_component_in_project=project_envelope_operations.update_skylight_in_project,
        remove_component_from_project=project_envelope_operations.remove_skylight_from_project
    )
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
    subtests: pytest.Subtests,
):
    project_id = getattr(project, "id", None)
    assert project_id, f"No id found on project"

    # Run add -> update -> remove sequence for each assembly type
    with subtests.test(f"{assembly_config.name}: add"):
        building_area_key = get_building_area_key(project)
        default_assembly = assembly_config.default_factory()

        updated_project = assembly_config.add_component_to_project(
            project,
            building_area_key,
            default_assembly,
        )

        target_assembly_type = get_id_from_component(default_assembly)
        assert target_assembly_type, f"{assembly_config.name} has no assemblyType"

        client.update_project(project_id, updated_project)

        reloaded = client.get_project(project_id)

        assert_component_added(project=reloaded, path=assembly_config.path, component_id=target_assembly_type, component_name=assembly_config.name)

        project = reloaded

    with subtests.test(f"{assembly_config.name}: update"):
        new_description = f"Updated {assembly_config.name} description"
        updates = {"description": new_description}

        assemblies = project.get_by_path(assembly_config.path, [])
        assert assemblies, f"Expected {assembly_config.name} at '{assembly_config.path}'"

        target_assembly = find_component_in_component_list(assemblies, target_assembly_type)
        assert target_assembly, f"{assembly_config.name} with id {target_assembly_type} was not found"

        updated_project = assembly_config.update_component_in_project(
            project, target_assembly_type, updates
        )

        client.update_project(project_id, updated_project)

        reloaded = client.get_project(project_id)

        assert_component_updated(project=reloaded, path=assembly_config.path, updates=updates, component_id=target_assembly_type, component_name=assembly_config.name)

        project = reloaded

    with subtests.test(f"{assembly_config.name}: remove"):
        updated_project = assembly_config.remove_component_from_project(
            project, target_assembly_type
        )

        client.update_project(project_id, updated_project)

        reloaded = client.get_project(project_id)

        assert_component_removed(project=reloaded, path=assembly_config.path, component_id=target_assembly_type, component_name=assembly_config.name)

# @pytest.mark.parametrize(
#     "nested_assembly_config",
#     NESTED_ASSEMBLY_CONFIGS,
#     ids=lambda c: c.name,
# )
# def test_nested_assembly_operations(
#     client: COMcheckClient,
#     project: ComBuilding,
#     nested_assembly_config: AssemblyConfig,
#     subtests: pytest.Subtests,
# ):
#     # Run add -> update -> remove sequence for each assembly type

#     with subtests.test(f"{nested_assembly_config.name}: add"):
#         building_area_key = get_building_area_key(project)
#         default_assembly = nested_assembly_config.default_factory()

#         parent_assembly_path = nested_assembly_config.path.rsplit(".", 1)[0]
#         parent_assembly = project.get_by_path(parent_assembly_path)

#         updated_project = nested_assembly_config.add_component_to_project(
#             project,
#             building_area_key,
#             default_assembly,
#             parent_assembly
#         )

#         print(parent_assembly)
#         print(default_assembly)
#         print(updated_project.envelope.agWall[0])
#         print(project.envelope.agWall[0])

#         project_id = getattr(updated_project, "id", None)
#         assert project_id, f"No id found on updated project for {nested_assembly_config.name} (add)"

#         client.update_project(project_id, updated_project)

#         reloaded = client.get_project(project_id)
#         assemblies: List[Any] = reloaded.get_by_path(nested_assembly_config.path, [])
#         assert assemblies, (
#             f"Expected at least one {nested_assembly_config.name} at path "
#             f"'{nested_assembly_config.path}' after add"
#         )

#         project = reloaded

#     with subtests.test(f"{nested_assembly_config.name}: update"):
#         new_description = f"Updated {nested_assembly_config.name} description"
#         updates = {"description": new_description}

#         assemblies = project.get_by_path(nested_assembly_config.path, [])
#         if not assemblies:
#             pytest.skip(
#                 f"No {nested_assembly_config.name} assemblies found at '{nested_assembly_config.path}'"
#             )

#         target_assembly = assemblies[0]
#         target_assembly_type = getattr(target_assembly, "assemblyType", None)
#         assert target_assembly_type, f"{nested_assembly_config.name} has no assemblyType"

#         updated_project = nested_assembly_config.update_component_in_project(
#             project, target_assembly_type, updates
#         )
#         project_id = getattr(updated_project, "id", None)
#         assert project_id, f"No id found on updated project for {nested_assembly_config.name} (update)"

#         client.update_project(project_id, updated_project)

#         reloaded = client.get_project(project_id)

#         assemblies_after: List[Any] = reloaded.get_by_path(nested_assembly_config.path, [])
#         assert assemblies_after, (
#             f"No assemblies found at '{nested_assembly_config.path}' after update"
#         )

#         assert any(
#             getattr(a, "assemblyType", None) == target_assembly_type
#             and getattr(a, "description", None) == new_description
#             for a in assemblies_after
#         ), f"{nested_assembly_config.name} description was not updated as expected"

#         project = reloaded

#     with subtests.test(f"{nested_assembly_config.name}: remove"):
#         updated_project = nested_assembly_config.remove_component_from_project(
#             project, target_assembly_type
#         )
#         project_id = getattr(updated_project, "id", None)
#         assert project_id, f"No id found on updated project for {nested_assembly_config.name} (remove)"

#         client.update_project(project_id, updated_project)

#         reloaded = client.get_project(project_id)
#         assemblies: List[Any] = reloaded.get_by_path(nested_assembly_config.path)
#         assembly_manager = DataManager[type(target_assembly)](initial_data=assemblies, model_type=type(target_assembly))
#         assert assembly_manager.get_by_identifier(target_assembly_type) is None, f"Expected assembly {nested_assembly_config.name} with assemblytype '{target_assembly_type}' at path '{nested_assembly_config.path}' to be removed"