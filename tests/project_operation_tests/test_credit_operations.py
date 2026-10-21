"""Tests for project_credit_operations."""

import pytest
from pydantic import ValidationError
from pydantic.experimental.missing_sentinel import MISSING

from comcheck_api.defaults import (
    get_default_building_area_template,
    get_default_project_template,
)
from comcheck_api.project_operations import (
    project_building_area_operations as ba_ops,
    project_credit_operations as cr_ops,
)
from comcheck_api.types.core_types import (
    AirInfiltrationMeasurementTypeOptions,
    ComBuilding,
    EfficiencyPackage,
    EnergyCreditMultiplierException,
    IECC2024EnergyCreditTypeOptions,
)

ROOF_R10 = (
    IECC2024EnergyCreditTypeOptions.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ENHANCED_ROOF_R10
)
AIR_INFILTRATION = (
    IECC2024EnergyCreditTypeOptions.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_REDUCE_AIR_INFILTRATION
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def credit_project() -> ComBuilding:
    """Default project with two building areas."""
    project = get_default_project_template()
    first_area = get_default_building_area_template()
    first_area.areaDescription = "Office"
    second_area = get_default_building_area_template()
    second_area.areaDescription = "Retail"
    project = ba_ops.add_building_area_to_project(project, first_area)
    return ba_ops.add_building_area_to_project(project, second_area)


def _area_keys(project: ComBuilding) -> list[str]:
    return [area.key for area in project.lighting.wholeBldgUse]


def _with_roof_credit(project: ComBuilding) -> tuple[ComBuilding, str]:
    key = _area_keys(project)[0]
    return (
        cr_ops.add_energy_credit_to_project(
            project, key, EfficiencyPackage(type=ROOF_R10)
        ),
        key,
    )


# ---------------------------------------------------------------------------
# add_energy_credit_to_project
# ---------------------------------------------------------------------------


def test_add_energy_credit_sets_building_area_key(credit_project: ComBuilding):
    result, key = _with_roof_credit(credit_project)

    (credit,) = result.efficiencyPackages
    assert credit.type == ROOF_R10
    assert credit.bldgUseKey == key


def test_add_energy_credit_initializes_missing_list(credit_project: ComBuilding):
    credit_project.efficiencyPackages = MISSING

    result, _ = _with_roof_credit(credit_project)

    assert len(result.efficiencyPackages) == 1


def test_add_energy_credit_does_not_mutate_inputs(credit_project: ComBuilding):
    key = _area_keys(credit_project)[0]
    new_credit = EfficiencyPackage(type=ROOF_R10)

    cr_ops.add_energy_credit_to_project(credit_project, key, new_credit)

    assert credit_project.efficiencyPackages == []
    assert new_credit.bldgUseKey is MISSING


def test_add_same_credit_type_to_other_area(credit_project: ComBuilding):
    result, _ = _with_roof_credit(credit_project)
    other_key = _area_keys(credit_project)[1]

    result = cr_ops.add_energy_credit_to_project(
        result, other_key, EfficiencyPackage(type=ROOF_R10)
    )

    assert len(result.efficiencyPackages) == 2


def test_add_duplicate_credit_raises(credit_project: ComBuilding):
    result, key = _with_roof_credit(credit_project)

    with pytest.raises(ValueError, match="already has energy credit"):
        cr_ops.add_energy_credit_to_project(
            result, key, EfficiencyPackage(type=ROOF_R10)
        )


def test_add_energy_credit_unknown_area_raises(credit_project: ComBuilding):
    with pytest.raises(ValueError, match="not found"):
        cr_ops.add_energy_credit_to_project(
            credit_project, "no-such-key", EfficiencyPackage(type=ROOF_R10)
        )


def test_efficiency_package_rejects_unknown_type():
    with pytest.raises(ValidationError):
        EfficiencyPackage(type="NOT_A_CREDIT")


# ---------------------------------------------------------------------------
# update_energy_credit_in_project
# ---------------------------------------------------------------------------


def test_update_energy_credit_inputs(credit_project: ComBuilding):
    key = _area_keys(credit_project)[0]
    project = cr_ops.add_energy_credit_to_project(
        credit_project, key, EfficiencyPackage(type=AIR_INFILTRATION)
    )

    result = cr_ops.update_energy_credit_in_project(
        project,
        key,
        AIR_INFILTRATION,
        {
            "airInfiltration": 0.25,
            "airInfiltrationMeasurementType": "AIR_INFILTRATION_MEASUREMENT_50PA",
        },
    )

    (credit,) = result.efficiencyPackages
    assert credit.airInfiltration == 0.25
    assert (
        credit.airInfiltrationMeasurementType
        == AirInfiltrationMeasurementTypeOptions.AIR_INFILTRATION_MEASUREMENT_50PA
    )
    assert credit.bldgUseKey == key
    assert project.efficiencyPackages[0].airInfiltration is MISSING


def test_update_energy_credit_validates_values(credit_project: ComBuilding):
    project, key = _with_roof_credit(credit_project)

    with pytest.raises(ValidationError):
        cr_ops.update_energy_credit_in_project(
            project, key, ROOF_R10, {"fractionGrossFloorAreaServedByCAV": 2.0}
        )


@pytest.mark.parametrize("field", ["type", "bldgUseKey"])
def test_update_energy_credit_rejects_identity_fields(
    credit_project: ComBuilding, field: str
):
    project, key = _with_roof_credit(credit_project)

    with pytest.raises(ValueError, match="Remove the energy credit"):
        cr_ops.update_energy_credit_in_project(project, key, ROOF_R10, {field: "x"})


def test_update_missing_energy_credit_raises(credit_project: ComBuilding):
    project, key = _with_roof_credit(credit_project)

    with pytest.raises(ValueError, match="not found"):
        cr_ops.update_energy_credit_in_project(
            project, key, AIR_INFILTRATION, {"airInfiltration": 0.25}
        )


# ---------------------------------------------------------------------------
# remove_energy_credit_from_project
# ---------------------------------------------------------------------------


def test_remove_energy_credit(credit_project: ComBuilding):
    project, key = _with_roof_credit(credit_project)

    result = cr_ops.remove_energy_credit_from_project(project, key, ROOF_R10)

    assert result.efficiencyPackages == []
    assert len(project.efficiencyPackages) == 1


def test_remove_energy_credit_only_from_given_area(credit_project: ComBuilding):
    project, key = _with_roof_credit(credit_project)
    other_key = _area_keys(credit_project)[1]
    project = cr_ops.add_energy_credit_to_project(
        project, other_key, EfficiencyPackage(type=ROOF_R10)
    )

    result = cr_ops.remove_energy_credit_from_project(project, key, ROOF_R10)

    assert [credit.bldgUseKey for credit in result.efficiencyPackages] == [other_key]


def test_remove_missing_energy_credit_raises(credit_project: ComBuilding):
    with pytest.raises(ValueError, match="not found"):
        cr_ops.remove_energy_credit_from_project(
            credit_project, _area_keys(credit_project)[0], ROOF_R10
        )


def test_remove_building_area_removes_its_credits(credit_project: ComBuilding):
    project, key = _with_roof_credit(credit_project)
    other_key = _area_keys(credit_project)[1]
    project = cr_ops.add_energy_credit_to_project(
        project, other_key, EfficiencyPackage(type=AIR_INFILTRATION)
    )

    result = ba_ops.remove_building_area_from_project(project, key)

    assert [credit.bldgUseKey for credit in result.efficiencyPackages] == [other_key]


# ---------------------------------------------------------------------------
# get_energy_credit_keys_from_project
# ---------------------------------------------------------------------------


def test_get_energy_credit_keys(credit_project: ComBuilding):
    project, key = _with_roof_credit(credit_project)
    other_key = _area_keys(credit_project)[1]
    project = cr_ops.add_energy_credit_to_project(
        project, other_key, EfficiencyPackage(type=AIR_INFILTRATION)
    )

    assert cr_ops.get_energy_credit_keys_from_project(project) == [
        {"bldgUseKey": key, "type": ROOF_R10},
        {"bldgUseKey": other_key, "type": AIR_INFILTRATION},
    ]
    assert cr_ops.get_energy_credit_keys_from_project(project, other_key) == [
        {"bldgUseKey": other_key, "type": AIR_INFILTRATION},
    ]


def test_get_energy_credit_keys_missing_list(credit_project: ComBuilding):
    credit_project.efficiencyPackages = MISSING

    assert cr_ops.get_energy_credit_keys_from_project(credit_project) == []


# ---------------------------------------------------------------------------
# Project-level credit fields
# ---------------------------------------------------------------------------


def test_set_energy_credit_multiplier_exception(credit_project: ComBuilding):
    result = cr_ops.set_energy_credit_multiplier_exception_in_project(
        credit_project,
        EnergyCreditMultiplierException.ENERGY_CREDIT_MULTIPLIER_EXCEPTION_INDUSTRIAL_USE,
    )

    assert (
        result.energyCreditMultiplierException
        == EnergyCreditMultiplierException.ENERGY_CREDIT_MULTIPLIER_EXCEPTION_INDUSTRIAL_USE
    )
    assert credit_project.energyCreditMultiplierException is MISSING


def test_set_energy_credit_multiplier_exception_rejects_non_enum(
    credit_project: ComBuilding,
):
    with pytest.raises(TypeError):
        cr_ops.set_energy_credit_multiplier_exception_in_project(
            credit_project, "ENERGY_CREDIT_MULTIPLIER_EXCEPTION_INDUSTRIAL_USE"
        )


def test_set_core_and_shell_credit(credit_project: ComBuilding):
    result = cr_ops.set_core_and_shell_credit_in_project(credit_project, 2.5)
    assert result.projectCoreAndShellCredit == 2.5

    result = cr_ops.set_core_and_shell_credit_in_project(result, None)
    assert result.projectCoreAndShellCredit is None


def test_set_core_and_shell_credit_rejects_negative(credit_project: ComBuilding):
    with pytest.raises(ValueError):
        cr_ops.set_core_and_shell_credit_in_project(credit_project, -1)
