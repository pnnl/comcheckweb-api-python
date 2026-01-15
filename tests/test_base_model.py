from typing import List
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from comcheck_api.schemas.custom_base_model import CustomBaseModel
from comcheck_api.utilities.data_manager import DataManager, IdInfo
from tests.conftest import SampleParentModel, SampleChildModel, create_sample_child, create_sample_parent

@pytest.fixture
def child_data_manager():
    with patch("comcheck_api.utilities.data_manager.get_model_info", return_value=IdInfo(identifier="id", id_prefix="Child:Child")):
        yield DataManager[SampleChildModel](model_type=SampleChildModel)

def test_append_model_subcomponent_adds_item(parent: SampleParentModel, child: SampleChildModel, child_data_manager: DataManager):
    parent.append_subcomponent(child)

    assert len(parent.sampleChildModel) == 1

def test_append_dict_subcomponent_adds_item(parent: SampleParentModel, child: SampleChildModel, child_data_manager: DataManager):
    child = child.model_dump(mode="json")

    with patch("comcheck_api.types.core_types") as mock_core_types:
        setattr(mock_core_types, "SampleChildModel", SampleChildModel)

        parent.append_subcomponent(child, subcomponent_name="sampleChildModel")

    assert len(parent.sampleChildModel) == 1

def test_append_dict_subcomponent_validates_item(parent: SampleParentModel, child: SampleChildModel, child_data_manager: DataManager):
    child: dict = child.model_dump(mode="json")
    child.pop("id")

    with pytest.raises(ValidationError):
        SampleChildModel.model_validate_json(child)

    with patch("comcheck_api.types.core_types") as mock_core_types:
        setattr(mock_core_types, "SampleChildModel", SampleChildModel)

        with pytest.raises(ValidationError):
            parent.append_subcomponent(child, subcomponent_name="sampleChildModel")

def test_remove_from_subcomponent_list_by_instance(child_data_manager: DataManager):
    child1 = create_sample_child("1")
    child2 = create_sample_child("2")
    parent = create_sample_parent(child_list=[child1, child2])

    parent.remove_from_subcomponent_list(subcomponent=child1)

    assert [c.id for c in parent.sampleChildModel] == ["Child:Child 2"]

def test_remove_from_subcomponent_list_by_id_and_name(child_data_manager: DataManager):
    child1 = create_sample_child("1")
    child2 = create_sample_child("2")
    parent = create_sample_parent(child_list=[child1, child2])

    with patch("comcheck_api.types.core_types") as mock_core_types:
        setattr(mock_core_types, "SampleChildModel", SampleChildModel)

        parent.remove_from_subcomponent_list(
            subcomponent_id="Child:Child 2",
            subcomponent_name="sampleChildModel",
        )

    assert [c.id for c in parent.sampleChildModel] == ["Child:Child 1"]

def test_remove_from_subcomponent_list_requires_input(parent: SampleParentModel):
    with pytest.raises(ValueError):
        parent.remove_from_subcomponent_list()

def test_remove_from_subcomponent_list_not_found(child_data_manager: DataManager):
    child = create_sample_child()
    parent = create_sample_parent(child_list=[child])

    with pytest.raises(ValueError):
        parent.remove_from_subcomponent_list(
            subcomponent_id="Child:Child 2",
            subcomponent_name="sampleChildModel",
        )

def test_missing_subcomponent_list_raises():
    class BadModel(CustomBaseModel):
        pass

    model = BadModel()

    with patch("comcheck_api.types.core_types") as mock_core_types:
        setattr(mock_core_types, "SampleChildModel", SampleChildModel)

        with pytest.raises(AttributeError):
            model.remove_from_subcomponent_list(
                subcomponent_id="Child:Child 1",
                subcomponent_name="SampleChildModel",
            )