from typing import List
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from comcheck_api.types.custom_base_model import CustomBaseModel
from comcheck_api.managers.data_manager import DataManager, IdInfo
from tests.conftest import SampleParentModel, SampleChildModel, create_sample_child, create_sample_parent

@pytest.fixture
def child_data_manager():
    with patch("comcheck_api.managers.data_manager.get_model_info", return_value=IdInfo(identifier="id", id_prefix="Child:Child")):
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


def test_get_normalized_subcomponent_info_from_annotation():
    """Test that _get_normalized_subcomponent_info extracts type from list annotation."""
    from comcheck_api.types.core_types import HVAC, HVACSystem, ServiceWaterHeatingSystem
    from comcheck_api.defaults import get_default_project_template

    project = get_default_project_template()

    # Initialize hvac so we can test on it
    hvac = HVAC(hvacSystem=[], hvacPlant=[], fanSystem=[])

    # Test hvacSystem -> HVACSystem (list[HVACSystem] annotation)
    cls, name = hvac._get_normalized_subcomponent_info(None, "hvacSystem")
    assert cls == HVACSystem
    assert name == "hvacSystem"

    # Test swhSystem -> ServiceWaterHeatingSystem (list[ServiceWaterHeatingSystem] | MISSING annotation)
    cls, name = project._get_normalized_subcomponent_info(None, "swhSystem")
    assert cls == ServiceWaterHeatingSystem
    assert name == "swhSystem"


def test_get_normalized_subcomponent_info_from_annotation_hvac():
    """Test annotation extraction for hvac subcomponents."""
    from comcheck_api.types.core_types import HVAC, HVACSystem, FanSystem, HVACPlant

    # Initialize hvac
    hvac = HVAC(hvacSystem=[], hvacPlant=[], fanSystem=[])

    # Test fanSystem -> FanSystem (list[FanSystem] | None annotation)
    cls, name = hvac._get_normalized_subcomponent_info(None, "fanSystem")
    assert cls == FanSystem
    assert name == "fanSystem"

    # Test hvacPlant -> HVACPlant
    cls, name = hvac._get_normalized_subcomponent_info(None, "hvacPlant")
    assert cls == HVACPlant
    assert name == "hvacPlant"


def test_get_subcomponent_list_normalizes_none():
    """Test that _get_subcomponent_list normalizes None to []."""
    from comcheck_api.types.core_types import HVAC

    hvac = HVAC(hvacSystem=[], hvacPlant=[], fanSystem=None)

    # Should normalize None to []
    fan_list = hvac._get_subcomponent_list("fanSystem")
    assert fan_list == []
    assert isinstance(fan_list, list)