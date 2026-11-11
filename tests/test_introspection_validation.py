"""Tests for the introspection and validation helpers."""

import comcheck_api as cc
from comcheck_api.defaults import get_default_project_template


def test_list_operations_groups_in_documented_order():
    groups = list(dict.fromkeys(op.group for op in cc.list_operations()))

    assert groups == [
        "building_area",
        "envelope",
        "interior_lighting",
        "exterior_lighting",
        "mechanical",
        "credits",
        "renewable",
    ]


def test_list_operations_lists_public_functions_only():
    ops = cc.list_operations()
    names = {op.name for op in ops}

    assert "add_roof_to_project" in names
    assert "update_fan_in_fan_system" in names
    assert not any(name.startswith("_") for name in names)
    # Client methods are API calls, not project operations.
    assert "update_fan_maximum_allowable_hp" not in names
    roof = next(op for op in ops if op.name == "add_roof_to_project")
    assert roof.group == "envelope"
    assert roof.signature.startswith("add_roof_to_project(")


def test_lookup_type_model():
    schema = cc.lookup_type("Fan")

    assert schema.kind == "model"
    fields = {f.name: f for f in schema.fields}
    assert "designBrakeHp" in fields


def test_lookup_type_enums():
    str_enum = cc.lookup_type("FanSystemComplianceMethodOptions")
    plain_enum = cc.lookup_type("RenewableExceptionOptions")

    assert str_enum.kind == "enum"
    assert "FAN_SYSTEM_MOTOR_BRAKE_HP" in {m.name for m in str_enum.members}
    assert plain_enum.kind == "enum"
    assert plain_enum.members


def test_lookup_type_alias_case_insensitive_and_missing():
    assert cc.lookup_type("InteriorSpace").kind == "model"
    assert cc.lookup_type("combuilding").name == "ComBuilding"
    assert cc.lookup_type("NotAType") is None


def test_validate_project_accepts_model_and_dict():
    project = get_default_project_template()

    assert cc.validate_project(project).ok
    assert cc.validate_project(project.model_dump(mode="json")).ok


def test_validate_project_reports_errors_with_dotted_location():
    data = get_default_project_template().model_dump(mode="json")
    data["envelope"] = 5
    del data["control"]

    result = cc.validate_project(data)

    assert not result.ok
    locs = {err.loc for err in result.errors}
    assert {"control", "envelope"} <= locs
