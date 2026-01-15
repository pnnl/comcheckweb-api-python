import sys
from pathlib import Path
from typing import List
from dotenv import load_dotenv

import pytest

from comcheck_api.schemas.custom_base_model import CustomBaseModel
from comcheck_api.utilities.id_registry import reset_registry

load_dotenv()

# Add comcheck_api directory to Python path
comcheck_api_path = Path(__file__).parent.parent / "comcheck_api"
sys.path.insert(0, str(comcheck_api_path))


@pytest.fixture(autouse=True)
def reset_id_registry_before_test(request):
    if "no_reset" in request.keywords:
        # Skip resetting for tests marked with @pytest.mark.no_reset
        yield
    else:
        reset_registry()
        yield

class SampleChildModel(CustomBaseModel):
    _identifier: str = "id"
    id: str
    name: str
    value: int


class SampleParentModel(CustomBaseModel):
    _identifier: str = "id"
    id: str
    name: str
    value: int
    sampleChildModel: List[SampleChildModel]


def create_id(*, component_name: str = "Test", id_suffix: str = "1") -> str:
    return f"{component_name}:{component_name} {id_suffix}"


def create_sample_child(id_suffix: str = "1") -> SampleChildModel:
    return SampleChildModel(
        id=create_id(component_name="Child", id_suffix=id_suffix),
        name="Sample Child",
        value=42,
    )


def create_sample_parent(id_suffix: str = "1", child_list: list[SampleChildModel] = []) -> SampleParentModel:
    return SampleParentModel(
        id=create_id(component_name="Parent", id_suffix=id_suffix),
        name="Sample Parent",
        value=42,
        sampleChildModel=child_list,
    )


@pytest.fixture
def child(id_suffix: str = "1") -> SampleChildModel:
    return create_sample_child(id_suffix=id_suffix)


@pytest.fixture
def parent(id_suffix: str = "1") -> SampleParentModel:
    return create_sample_parent(id_suffix=id_suffix)