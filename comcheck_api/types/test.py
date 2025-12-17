from pydantic import BaseModel

from comcheck_api.types.core_types import *
from comcheck_api.types.api_types import *

def assertions():
    assert is_subset(AgWallAssembliesUValuesArgs, AgWall)

def is_subset(model_small: BaseModel, model_large: BaseModel) -> bool:
    fields_small = set(model_small.model_fields.keys())
    fields_large = set(model_large.model_fields.keys())
    return fields_small.issubset(fields_large)

assertions()