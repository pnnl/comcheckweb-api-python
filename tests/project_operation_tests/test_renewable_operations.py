"""Tests for project_renewable_operations."""

import pytest
from pydantic.experimental.missing_sentinel import MISSING

from comcheck_api.defaults import (
    get_default_renewable_system_template,
    get_default_offsite_renewable_procurement_template,
)
from comcheck_api.project_operations import (
    project_renewable_operations as rn_ops,
)
from comcheck_api.types.core_types import (
    ComBuilding,
    EnergyCodeOptions,
    RenewableExceptionOptions,
    RenewableSystemTypeOptions,
    RenewableSystemCapacityUnitOptions,
    OffsiteRenewableProcurementType,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh(project: ComBuilding) -> ComBuilding:
    return project.model_copy(deep=True)


# ---------------------------------------------------------------------------
# set_renewable_exception_in_project
# ---------------------------------------------------------------------------


def test_set_renewable_exception(project: ComBuilding):
    proj = _fresh(project)
    result = rn_ops.set_renewable_exception_in_project(
        proj, RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD
    )
    assert (
        result.renewable.renewableException
        == RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD
    )


def test_set_renewable_exception_rejects_nonetype(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="NoneType_None"):
        rn_ops.set_renewable_exception_in_project(
            proj, RenewableExceptionOptions.NoneType_None
        )


def test_set_renewable_exception_rejects_non_enum(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(TypeError):
        rn_ops.set_renewable_exception_in_project(
            proj, "RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD"
        )


def test_set_renewable_exception_does_not_mutate_original(project: ComBuilding):
    proj = _fresh(project)
    original_exception = proj.renewable.renewableException
    rn_ops.set_renewable_exception_in_project(
        proj, RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD
    )
    assert proj.renewable.renewableException == original_exception


# ---------------------------------------------------------------------------
# update_renewable_in_project
# ---------------------------------------------------------------------------


def test_update_renewable_scalar_fields(project: ComBuilding):
    proj = _fresh(project)
    result = rn_ops.update_renewable_in_project(proj, {"numberOfFloors": 5})
    assert result.renewable.numberOfFloors == 5


def test_update_renewable_validates_values(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError):
        rn_ops.update_renewable_in_project(proj, {"numberOfFloors": -3})
    with pytest.raises(ValueError):
        rn_ops.update_renewable_in_project(proj, {"numberOfFloors": "abc"})


def test_update_renewable_rejects_exception_field(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="set_renewable_exception_in_project"):
        rn_ops.update_renewable_in_project(proj, {"renewableException": "junk"})


def test_update_renewable_preserves_other_fields(project: ComBuilding):
    proj = _fresh(project)
    proj = rn_ops.add_renewable_system_to_project(
        proj, get_default_renewable_system_template()
    )
    result = rn_ops.update_renewable_in_project(proj, {"numberOfFloors": 4})
    assert result.renewable.id == proj.renewable.id
    assert result.renewable.renewableSystem == proj.renewable.renewableSystem
    assert (
        result.renewable.offsiteRenewableProcurement
        == proj.renewable.offsiteRenewableProcurement
    )


def test_update_renewable_rejects_engine_fields(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="engine-calculated"):
        rn_ops.update_renewable_in_project(proj, {"requiredCapacity": 100.0})
    with pytest.raises(ValueError, match="engine-calculated"):
        rn_ops.update_renewable_in_project(proj, {"proposedCapacity": 100.0})
    with pytest.raises(ValueError, match="engine-calculated"):
        rn_ops.update_renewable_in_project(
            proj, {"requiredOffsiteRenewableEnergy": 100.0}
        )
    with pytest.raises(ValueError, match="engine-calculated"):
        rn_ops.update_renewable_in_project(
            proj, {"proposedOffsiteRenewableEnergy": 100.0}
        )


def test_update_renewable_rejects_api_fields(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="API-calculated"):
        rn_ops.update_renewable_in_project(proj, {"largestThreeFloorArea": 1000.0})
    with pytest.raises(ValueError, match="API-calculated"):
        rn_ops.update_renewable_in_project(proj, {"roofAreaForRenewable": 500.0})


def test_update_renewable_rejects_list_fields(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="list fields"):
        rn_ops.update_renewable_in_project(proj, {"renewableSystem": []})
    with pytest.raises(ValueError, match="list fields"):
        rn_ops.update_renewable_in_project(proj, {"offsiteRenewableProcurement": []})


# ---------------------------------------------------------------------------
# add_renewable_system_to_project
# ---------------------------------------------------------------------------


def test_add_renewable_system(project: ComBuilding):
    proj = _fresh(project)
    rs = get_default_renewable_system_template()
    rs.description = "Solar panels"
    rs.renewableSystemCapacity = 50000.0

    result = rn_ops.add_renewable_system_to_project(proj, rs)

    keys = rn_ops.get_renewable_system_keys_from_project(result)
    assert any(k["description"] == "Solar panels" for k in keys)


def test_add_renewable_system_does_not_mutate_original(project: ComBuilding):
    proj = _fresh(project)
    original_count = len(proj.renewable.renewableSystem)
    rs = get_default_renewable_system_template()
    rs.description = "Wind turbine"
    rn_ops.add_renewable_system_to_project(proj, rs)
    assert len(proj.renewable.renewableSystem) == original_count


def test_add_renewable_system_auto_generates_description(project: ComBuilding):
    proj = _fresh(project)
    rs1 = get_default_renewable_system_template()
    rs1.description = None  # Missing description
    result = rn_ops.add_renewable_system_to_project(proj, rs1)

    # The description should be auto-generated with the prefix "Renewable System"
    keys = rn_ops.get_renewable_system_keys_from_project(result)
    assert any("Renewable System" in k.get("description", "") for k in keys)


# ---------------------------------------------------------------------------
# update_renewable_system_in_project
# ---------------------------------------------------------------------------


def test_update_renewable_system(project: ComBuilding):
    proj = _fresh(project)
    rs = get_default_renewable_system_template()
    rs.description = "Solar array"
    proj = rn_ops.add_renewable_system_to_project(proj, rs)

    result = rn_ops.update_renewable_system_in_project(
        proj,
        "Solar array",
        {
            "renewableSystemCapacity": 75000.0,
            "renewableSystemType": RenewableSystemTypeOptions.RENEWABLE_SYSTEM_TYPE_WIND,
        },
    )

    systems = result.renewable.renewableSystem
    updated = next(s for s in systems if s.description == "Solar array")
    assert updated.renewableSystemCapacity == 75000.0
    assert (
        updated.renewableSystemType
        == RenewableSystemTypeOptions.RENEWABLE_SYSTEM_TYPE_WIND
    )


def test_update_renewable_system_not_found(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="not found"):
        rn_ops.update_renewable_system_in_project(
            proj, "Nonexistent", {"renewableSystemCapacity": 100.0}
        )


# ---------------------------------------------------------------------------
# remove_renewable_system_from_project
# ---------------------------------------------------------------------------


def test_remove_renewable_system(project: ComBuilding):
    proj = _fresh(project)
    rs = get_default_renewable_system_template()
    rs.description = "Geothermal"
    proj = rn_ops.add_renewable_system_to_project(proj, rs)

    result = rn_ops.remove_renewable_system_from_project(proj, "Geothermal")

    keys = rn_ops.get_renewable_system_keys_from_project(result)
    assert not any(k["description"] == "Geothermal" for k in keys)


def test_remove_renewable_system_not_found(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="not found"):
        rn_ops.remove_renewable_system_from_project(proj, "Nonexistent")


# ---------------------------------------------------------------------------
# get_renewable_system_keys_from_project
# ---------------------------------------------------------------------------


def test_get_renewable_system_keys(project: ComBuilding):
    proj = _fresh(project)
    keys = rn_ops.get_renewable_system_keys_from_project(proj)
    assert isinstance(keys, list)


def test_mutating_ops_do_not_check_energy_code(project: ComBuilding):
    # Whether a project needs renewable data is the caller's call, so ops
    # must not reject codes (e.g. state codes) outside a fixed list.
    proj = _fresh(project)
    proj.control.code = EnergyCodeOptions.CEZ_IECC2009
    proj = rn_ops.set_renewable_exception_in_project(
        proj, RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD
    )
    proj = rn_ops.add_renewable_system_to_project(
        proj, get_default_renewable_system_template()
    )
    proj = rn_ops.add_offsite_renewable_procurement_to_project(
        proj, get_default_offsite_renewable_procurement_template()
    )
    assert len(proj.renewable.renewableSystem) == 1
    assert len(proj.renewable.offsiteRenewableProcurement) == 1


def test_get_renewable_system_keys_works_for_any_code(project: ComBuilding):
    # Read-only operations work for any code
    proj = _fresh(project)
    proj.control.code = EnergyCodeOptions.CEZ_IECC2009
    keys = rn_ops.get_renewable_system_keys_from_project(proj)
    assert isinstance(keys, list)


# ---------------------------------------------------------------------------
# add_offsite_renewable_procurement_to_project
# ---------------------------------------------------------------------------


def test_add_offsite_renewable_procurement(project: ComBuilding):
    proj = _fresh(project)
    op = get_default_offsite_renewable_procurement_template()
    op.description = "PPA agreement"
    op.offsiteRenewableEnergy = 100000.0

    result = rn_ops.add_offsite_renewable_procurement_to_project(proj, op)

    keys = rn_ops.get_offsite_renewable_procurement_keys_from_project(result)
    assert any(k["description"] == "PPA agreement" for k in keys)


def test_add_offsite_renewable_procurement_initializes_missing_list(
    project: ComBuilding,
):
    proj = _fresh(project)
    # Force offsiteRenewableProcurement to MISSING
    proj.renewable.offsiteRenewableProcurement = MISSING

    op = get_default_offsite_renewable_procurement_template()
    op.description = "Community solar"
    result = rn_ops.add_offsite_renewable_procurement_to_project(proj, op)

    # The list should be initialized
    assert result.renewable.offsiteRenewableProcurement is not MISSING
    assert isinstance(result.renewable.offsiteRenewableProcurement, list)
    assert len(result.renewable.offsiteRenewableProcurement) >= 1


def test_add_offsite_renewable_procurement_does_not_mutate_original(
    project: ComBuilding,
):
    proj = _fresh(project)
    # Ensure list is initialized
    if proj.renewable.offsiteRenewableProcurement is MISSING:
        proj.renewable.offsiteRenewableProcurement = []
    original_count = len(proj.renewable.offsiteRenewableProcurement)

    op = get_default_offsite_renewable_procurement_template()
    op.description = "Green tariff"
    rn_ops.add_offsite_renewable_procurement_to_project(proj, op)

    assert len(proj.renewable.offsiteRenewableProcurement) == original_count


# ---------------------------------------------------------------------------
# update_offsite_renewable_procurement_in_project
# ---------------------------------------------------------------------------


def test_update_offsite_renewable_procurement(project: ComBuilding):
    proj = _fresh(project)
    op = get_default_offsite_renewable_procurement_template()
    op.description = "Wind PPA"
    proj = rn_ops.add_offsite_renewable_procurement_to_project(proj, op)

    result = rn_ops.update_offsite_renewable_procurement_in_project(
        proj,
        "Wind PPA",
        {
            "offsiteRenewableEnergy": 200000.0,
            "offsiteRenewableProcurementType": OffsiteRenewableProcurementType.OFFSITE_RENEWABLE_PROCUREMENT_PHYSICAL_AGREEMENT,
        },
    )

    procurements = result.renewable.offsiteRenewableProcurement
    updated = next(p for p in procurements if p.description == "Wind PPA")
    assert updated.offsiteRenewableEnergy == 200000.0
    assert (
        updated.offsiteRenewableProcurementType
        == OffsiteRenewableProcurementType.OFFSITE_RENEWABLE_PROCUREMENT_PHYSICAL_AGREEMENT
    )


def test_update_offsite_renewable_procurement_not_found(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="not found"):
        rn_ops.update_offsite_renewable_procurement_in_project(
            proj, "Nonexistent", {"offsiteRenewableEnergy": 100.0}
        )


# ---------------------------------------------------------------------------
# remove_offsite_renewable_procurement_from_project
# ---------------------------------------------------------------------------


def test_remove_offsite_renewable_procurement(project: ComBuilding):
    proj = _fresh(project)
    op = get_default_offsite_renewable_procurement_template()
    op.description = "REC purchase"
    proj = rn_ops.add_offsite_renewable_procurement_to_project(proj, op)

    result = rn_ops.remove_offsite_renewable_procurement_from_project(
        proj, "REC purchase"
    )

    keys = rn_ops.get_offsite_renewable_procurement_keys_from_project(result)
    assert not any(k["description"] == "REC purchase" for k in keys)


def test_remove_offsite_renewable_procurement_not_found(project: ComBuilding):
    proj = _fresh(project)
    with pytest.raises(ValueError, match="not found"):
        rn_ops.remove_offsite_renewable_procurement_from_project(proj, "Nonexistent")


# ---------------------------------------------------------------------------
# get_offsite_renewable_procurement_keys_from_project
# ---------------------------------------------------------------------------


def test_get_offsite_renewable_procurement_keys(project: ComBuilding):
    proj = _fresh(project)
    keys = rn_ops.get_offsite_renewable_procurement_keys_from_project(proj)
    assert isinstance(keys, list)


def test_get_offsite_renewable_procurement_keys_works_for_any_code(
    project: ComBuilding,
):
    # Read-only operations work for any code
    proj = _fresh(project)
    proj.control.code = EnergyCodeOptions.CEZ_IECC2009
    keys = rn_ops.get_offsite_renewable_procurement_keys_from_project(proj)
    assert isinstance(keys, list)


def test_get_offsite_renewable_procurement_keys_handles_missing(project: ComBuilding):
    proj = _fresh(project)
    proj.renewable.offsiteRenewableProcurement = MISSING
    keys = rn_ops.get_offsite_renewable_procurement_keys_from_project(proj)
    assert keys == []


# ---------------------------------------------------------------------------
# Exception and systems coexistence
# ---------------------------------------------------------------------------


def test_exception_and_systems_coexist(project: ComBuilding):
    proj = _fresh(project)

    # Set an exception
    proj = rn_ops.set_renewable_exception_in_project(
        proj, RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD
    )

    # Add a renewable system
    rs = get_default_renewable_system_template()
    rs.description = "Backup solar"
    proj = rn_ops.add_renewable_system_to_project(proj, rs)

    # Both should be present
    assert (
        proj.renewable.renewableException
        == RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD
    )
    systems = rn_ops.get_renewable_system_keys_from_project(proj)
    assert any(k["description"] == "Backup solar" for k in systems)
