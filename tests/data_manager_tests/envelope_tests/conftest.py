from copy import deepcopy

import pytest

from comcheck_api.constants import envelope_constants

default_objects = {
    name.lower().replace("default_", ""): getattr(envelope_constants, name)
    for name in envelope_constants.__annotations__.keys()
    if name.startswith("DEFAULT_")
}

# Dynamically create fixtures
for name, obj in default_objects.items():

    @pytest.fixture(name=name)
    def fixture_func(obj=obj):
        return deepcopy(obj)

    globals()[f"{name}_fixture"] = fixture_func
