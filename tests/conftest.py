"""Pytest configuration file."""

import sys
from pathlib import Path

import pytest

from comcheck_api.utilities.id_registry import reset_registry
from comcheck_api.constants.envelope_constants import *

# Add compcheck_api directory to Python path
compcheck_api_path = Path(__file__).parent.parent / "comcheck_api"
sys.path.insert(0, str(compcheck_api_path))

@pytest.fixture(autouse=True)
def reset_id_registry_before_test(request):
    if "no_reset" in request.keywords:
        # Skip resetting for tests marked with @pytest.mark.no_reset
        yield
    else:
        reset_registry()
        yield