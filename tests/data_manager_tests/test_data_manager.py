from typing import List
import pytest
from copy import deepcopy
from unittest.mock import patch

from tests.conftest import SampleParentModel, SampleChildModel, create_id, create_sample_parent
from comcheck_api.managers.data_manager import DataManager, IdInfo

@pytest.fixture
def data_manager():
    with patch("comcheck_api.managers.data_manager.get_model_info", return_value=IdInfo(identifier="id", id_prefix="Test:Test")):
        yield DataManager[SampleParentModel](model_type=SampleParentModel)

def test_initialization_with_provided_data(data_manager: DataManager, parent: SampleParentModel):
    manager = DataManager[SampleParentModel](initial_data=[parent], model_type=SampleParentModel)
    assert manager.get_all() == [parent]

def test_add_new_and_get_by_identifier(data_manager: DataManager, parent: SampleParentModel):
    result = data_manager.add_new(parent)
    assert parent in result
    fetched = data_manager.get_by_identifier(parent.id)
    assert fetched == parent

def test_add_new_with_dict(data_manager: DataManager, child: SampleChildModel):
    data_id = create_id(id_suffix=2)
    data = {"id": data_id, "name": "DictSample", "value": 10, "sampleChildModel": [child.model_dump(mode="json")]}
    data_manager.add_new(data)
    fetched = data_manager.get_by_identifier(data_id)
    assert fetched.name == "DictSample"
    assert isinstance(fetched, SampleParentModel)

def test_add_duplicate_identifier_updates_identifier(data_manager: DataManager, parent: SampleParentModel):
    parent_1 = parent
    parent_2 = deepcopy(parent_1)
    data_manager.add_new(parent_1)
    data_manager.add_new(parent_2)
    assert parent_2.id != parent_1.id

def test_modify_one_updates_fields(data_manager: DataManager, parent: SampleParentModel):
    data_manager.add_new(parent)
    updates = {"name": "Updated Name", "value": 100}
    updated = data_manager.modify_one(parent.id, updates)
    assert updated.name == "Updated Name"
    assert updated.value == 100

def test_modify_one_invalid_field_raises(data_manager: DataManager, parent: SampleParentModel):
    data_manager.add_new(parent)
    with pytest.raises(ValueError):
        data_manager.modify_one(parent.id, {"nonexistent_field": "fail"})

def test_modify_one_changes_identifier_uniqueness(data_manager: DataManager):
    parent_1 = create_sample_parent("1")
    parent_2 = create_sample_parent("2")
    data_manager.add_new(parent_1)
    data_manager.add_new(parent_2)
    with pytest.raises(ValueError):
        data_manager.modify_one(parent_1.id, {data_manager._identifier: parent_2.id})

def test_delete_one_removes_item(data_manager: DataManager, parent: SampleParentModel):
    data_manager.add_new(parent)
    deleted = data_manager.delete_one(parent.id)
    assert deleted is True
    assert data_manager.get_by_identifier(parent.id) is None

def test_delete_one_nonexistent_returns_false(data_manager: DataManager):
    deleted = data_manager.delete_one("Test:Test")
    assert deleted is False