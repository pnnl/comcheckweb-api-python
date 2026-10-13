"""Tests for renewable area placeholder methods."""

import pytest

from comcheck_api import COMcheckClient
from comcheck_api.api.api_services import COMCheckApiService
from comcheck_api.types.core_types import ComBuilding, EnergyCodeOptions


def test_area_for_renewable_service_raises_not_implemented():
    """Test that COMCheckApiService.area_for_renewable raises NotImplementedError."""
    service = COMCheckApiService(api_key="test")
    with pytest.raises(
        NotImplementedError, match="area-for-renewable endpoint is pending"
    ):
        service.area_for_renewable({}, "CEZ_90_1_2022")


def test_update_renewable_area_client_raises_not_implemented():
    """Test that COMcheckClient.update_renewable_area raises NotImplementedError."""
    from comcheck_api.defaults import get_default_project_template

    client = COMcheckClient(api_key="test")
    project = get_default_project_template()
    project.control.code = EnergyCodeOptions.CEZ_90_1_2022
    with pytest.raises(
        NotImplementedError, match="area-for-renewable endpoint is pending"
    ):
        client.update_renewable_area(project)
