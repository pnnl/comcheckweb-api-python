from typing import List
from comcheck_api.types.custom_base_model import CustomBaseModel
from comcheck_api.types.core_types import ComBuilding
from comcheck_api.managers.data_manager import DataManager, get_model_info


def _require_building_area(project: ComBuilding, building_area_key: str) -> None:
    """
    Ensure that project.lighting.wholeBldgUse exists and contains the given key.
    """
    whole_use = project.get_by_path("lighting.wholeBldgUse")

    if not isinstance(whole_use, list):
        raise ValueError("No building area (wholeBldgUse) found in project.")

    if not any(getattr(area, "key", None) == building_area_key for area in whole_use):
        raise ValueError(
            f"Building area key '{building_area_key}' not found in lighting.wholeBldgUse."
        )
    
def find_component_in_component_list(components: List[CustomBaseModel], component_id: str):
    if not components:
        return None
    
    component_type = type(components[0])
    component_manager = DataManager[component_type](initial_data=components, model_type=component_type)

    return component_manager.get_by_identifier(component_id)

def get_id_from_component(
    component: CustomBaseModel,
) -> str:
    """Retrieve the id of a component"""

    identifier, _ = get_model_info(type(component))
    return getattr(component, identifier, None)