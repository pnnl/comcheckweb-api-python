import pytest
from copy import deepcopy
from unittest.mock import patch

from comcheck_api.schemas.custom_base_model import CustomBaseModel
from comcheck_api.utilities.data_manager import DataManager, IdInfo

class SampleChildModel(CustomBaseModel):
    _identifier: id
    id: str
    name: str
    value: int

class SampleParentModel(CustomBaseModel):
    _identifier: id
    id: str
    name: str
    value: int
    child: SampleChildModel

def get_id(id_suffix: str = "1") -> str:
    return f"Test:Test {id_suffix}"

def get_sample_parent(id_suffix: str = "1") -> SampleParentModel:
    return SampleParentModel(id=f"{get_id(id_suffix)}", name="Sample", value=42, child=get_sample_child())

def get_sample_child(id_suffix: str = "1") -> SampleChildModel:
    return SampleChildModel(id=f"{get_id(id_suffix)}", name="Sample", value=42)

@pytest.fixture
def data_manager():
    with patch("comcheck_api.utilities.data_manager.get_model_info", return_value=IdInfo(identifier="id", id_prefix="Test:Test")):
        yield DataManager[SampleParentModel](model_type=SampleParentModel)

def test_initialization_with_provided_data(data_manager: DataManager):
    sp = get_sample_parent()
    manager = DataManager[SampleParentModel](initial_data=[sp], model_type=SampleParentModel)
    assert manager.get_all() == [sp]

def test_add_new_and_get_by_identifier(data_manager: DataManager):
    sp = get_sample_parent()
    result = data_manager.add_new(sp)
    assert sp in result
    fetched = data_manager.get_by_identifier(sp.id)
    assert fetched == sp

def test_add_new_with_dict(data_manager: DataManager):
    data_id = get_id(2)
    data = {"id": data_id, "name": "DictSample", "value": 10, "child": get_sample_child().model_dump(mode="json")}
    result = data_manager.add_new(data)
    fetched = data_manager.get_by_identifier(data_id)
    assert fetched.name == "DictSample"
    assert isinstance(fetched, SampleParentModel)

def test_add_duplicate_identifier_updates_identifier(data_manager: DataManager):
    sp1 = get_sample_parent()
    sp2 = deepcopy(sp1)
    data_manager.add_new(sp1)
    data_manager.add_new(sp2)
    assert sp2.id != sp1.id

def test_modify_one_updates_fields(data_manager: DataManager):
    sp = get_sample_parent()
    data_manager.add_new(sp)
    updates = {"name": "Updated Name", "value": 100}
    updated = data_manager.modify_one(sp.id, updates)
    assert updated.name == "Updated Name"
    assert updated.value == 100

def test_modify_one_invalid_field_raises(data_manager: DataManager):
    sp = get_sample_parent()
    data_manager.add_new(sp)
    with pytest.raises(ValueError):
        data_manager.modify_one(sp.id, {"nonexistent_field": "fail"})

def test_modify_one_changes_identifier_uniqueness(data_manager: DataManager):
    sp1 = get_sample_parent("1")
    sp2 = get_sample_parent("2")
    data_manager.add_new(sp1)
    data_manager.add_new(sp2)
    with pytest.raises(ValueError):
        data_manager.modify_one(sp1.id, {data_manager._identifier: sp2.id})

def test_delete_one_removes_item(data_manager: DataManager):
    sp = get_sample_parent()
    data_manager.add_new(sp)
    deleted = data_manager.delete_one(sp.id)
    assert deleted is True
    assert data_manager.get_by_identifier(sp.id) is None

def test_delete_one_nonexistent_returns_false(data_manager: DataManager):
    deleted = data_manager.delete_one("Test:Test")
    assert deleted is False