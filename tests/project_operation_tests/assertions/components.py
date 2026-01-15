from comcheck_api.schemas.custom_base_model import CustomBaseModel
from comcheck_api.types.core_types import ComBuilding
from comcheck_api.utilities.data_manager import get_model_info
from comcheck_api.utilities.project_utilities import find_component_in_component_list, get_id_from_component


def assert_component_added(
    project: ComBuilding,
    path: str,
    component_id: str,
    component_name: str,
) -> None:
    """Assert that a component with the given key exists in the collection."""
    components = project.get_by_path(path, [])
    assert isinstance(components, list) and components, (
        f"Expected at least one {component_name} at path "
        f"'{path}' after add"
    )

    added_component = find_component_in_component_list(components=components, component_id=component_id)
    if not added_component:
        raise AssertionError(
            f"{component_name} with id '{component_id}' not found after add"
        )


def assert_component_updated(
    project: ComBuilding,
    path: str,
    updates: dict,
    component_id: str,
    component_name: str,
) -> None:
    """Assert that a component with the given key has the updated fields."""
    components = project.get_by_path(path, [])
    assert isinstance(components, list) and components, (
        f"Expected at least one {component_name} at path "
        f"'{path}' after update"
    )

    updated_component = find_component_in_component_list(components=components, component_id=component_id)
    if not updated_component:
        raise AssertionError(
            f"{component_name} with id '{component_id}' not found after update"
        )

    for field, expected in updates.items():
        actual = getattr(updated_component, field, None)
        assert actual == expected, (
            f"{component_name}.{field} not updated as expected "
            f"(expected={expected}, actual={actual})"
        )


def assert_component_removed(
    project: ComBuilding,
    path: str,
    component_id: str,
    component_name: str,
) -> None:
    """Assert that a component with the given key does not exist in the collection."""
    components = project.get_by_path(path, [])

    added_component = find_component_in_component_list(components=components, component_id=component_id)
    if added_component:
        raise AssertionError(
            f"Expected {component_name} with id '{component_id}' to be removed"
        )
    
def assert_component_has_id(
    component: CustomBaseModel,
) -> None:
    """Assert that a component has a value for its identifier"""

    id = get_id_from_component(component)
    return id