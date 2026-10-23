"""Project Mechanical Operations.

Manages HVAC systems, fan systems, plants, and water heaters at the
project level. Mechanical data lives in ``ComBuilding.hvac`` (which can be ``MISSING``)
and ``ComBuilding.swhSystem`` (also can be ``MISSING``).

The ``hvac`` singleton contains:

- ``hvacSystem[]`` — list of HVAC systems, identified by ``description``
- ``fanSystem[]`` — list of fan systems (can be ``None``), identified by ``description``
- ``hvacPlant[]`` — list of HVAC plants, identified by ``description``

Water heaters are separate:

- ``swhSystem[]`` — list at the top level, identified by ``description``

Fan system cross-reference
---------------------------
``FanSystem.fanSystemKey`` is a UUID that links a fan system to an HVAC system.
When a fan system is assigned to an HVAC system, its UUID is copied into
``HVACSystem.fanSystemKey``. Use ``assign_fan_system_to_hvac_system`` to create
this link by description; callers never handle the UUID directly.

Energy codes
------------
Mechanical operations don't check ``control.code`` — which mechanical components
apply to the project is up to you.
"""

import logging
import warnings
from typing import Any
from uuid import uuid4
from pydantic import BaseModel
from pydantic.experimental.missing_sentinel import MISSING

from comcheck_api.types.core_types import (
    ComBuilding,
    HVAC,
    HVACSystem,
    FanSystem,
    Fan,
    FanSystemComplianceMethodOptions,
    FanSystemPressureDropCredits,
    PressureDropTypeOptions,
    HVACPlant,
    ServiceWaterHeatingSystem,
)
from comcheck_api.utilities.project_utilities import (
    _ensure_hvac,
    _require_hvac_system,
    _require_fan_system,
    _require_hvac_plant,
    _require_water_heater,
)

logger = logging.getLogger(__name__)

# Engine-calculated fields that must not be writable via update operations
_ENGINE_CALCULATED_FAN_SYSTEM_FIELDS = frozenset(
    {
        "complies",
        "complianceMessage",
    }
)

_ENGINE_CALCULATED_MECHANICAL_FIELDS = frozenset(
    {
        "requirementAnswer",
    }
)

# Identity fields that must not be changed via update
_FAN_SYSTEM_IDENTITY_FIELDS = frozenset({"fanSystemKey"})


# *********** HVAC system operations ***********


def add_hvac_system_to_project(
    project: ComBuilding,
    new_hvac_system: HVACSystem,
) -> ComBuilding:
    """Add a new HVAC system to the project.

    If ``project.hvac`` is ``MISSING``, it is created automatically.

    Args:
        project: The project to modify.
        new_hvac_system: The HVACSystem to add.

    Returns:
        Updated project with the new HVACSystem added.

    Raises:
        ValueError: If the HVAC system's fanSystemKey references a non-existent fan system.
    """
    updated_project = project.model_copy(deep=True)
    new_hvac_system = new_hvac_system.model_copy(deep=True)

    # Ensure hvac exists
    _ensure_hvac(updated_project)

    # Validate fanSystemKey if provided
    fan_system_key = getattr(new_hvac_system, "fanSystemKey", None)
    if fan_system_key:
        _validate_fan_system_key(updated_project, fan_system_key)

    updated_project.hvac.append_subcomponent(new_hvac_system, subcomponent_name="hvacSystem")
    return updated_project


def update_hvac_system_in_project(
    project: ComBuilding,
    hvac_system_description: str,
    updates: dict[str, Any] | HVACSystem,
) -> ComBuilding:
    """Update an existing HVAC system.

    Engine-calculated fields (``requirementAnswer``) are rejected.

    Args:
        project: The project to modify.
        hvac_system_description: The description of the HVAC system to update.
        updates: Partial updates (dict) or full HVACSystem to apply.

    Returns:
        Updated project with the HVAC system modified.

    Raises:
        ValueError: If the HVAC system is not found, or if updates contain
            engine-calculated fields, or if fanSystemKey references a non-existent fan system.
    """
    _require_hvac_system(project, hvac_system_description)

    current = _find_by_description(project.hvac.hvacSystem, hvac_system_description)
    updates = _updates_to_dict(updates)
    _reject_changed_fields(
        current,
        updates,
        _ENGINE_CALCULATED_MECHANICAL_FIELDS,
        "update_hvac_system_in_project",
    )

    # Validate fanSystemKey if being updated
    fan_system_key = updates.get("fanSystemKey")
    if fan_system_key is not None:
        _validate_fan_system_key(project, fan_system_key)

    updated_project = project.model_copy(deep=True)
    updated_project.hvac.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=hvac_system_description,
        subcomponent_name="hvacSystem",
    )
    return updated_project


def remove_hvac_system_from_project(
    project: ComBuilding,
    hvac_system_description: str,
) -> ComBuilding:
    """Remove an HVAC system from the project.

    Args:
        project: The project to modify.
        hvac_system_description: The description of the HVAC system to remove.

    Returns:
        Updated project with the HVAC system removed.

    Raises:
        ValueError: If the HVAC system is not found.
    """
    _require_hvac_system(project, hvac_system_description)

    updated_project = project.model_copy(deep=True)
    updated_project.hvac.remove_from_subcomponent_list(
        subcomponent_id=hvac_system_description,
        subcomponent_name="hvacSystem",
    )
    return updated_project


def assign_fan_system_to_hvac_system(
    project: ComBuilding,
    hvac_system_description: str,
    fan_system_description: str | None,
) -> ComBuilding:
    """Assign a fan system to an HVAC system by copying its UUID into fanSystemKey.

    Pass ``fan_system_description=None`` to unassign the fan system.

    Args:
        project: The project to modify.
        hvac_system_description: The description of the HVAC system.
        fan_system_description: The description of the fan system to assign, or None to unassign.

    Returns:
        Updated project with the fan system assigned.

    Raises:
        ValueError: If the HVAC system or fan system is not found.
    """
    _require_hvac_system(project, hvac_system_description)

    fan_system_key = None
    if fan_system_description is not None:
        _require_fan_system(project, fan_system_description)
        # Look up the fan system's key
        fan_systems = project.hvac.fanSystem or []
        for fan_system in fan_systems:
            if getattr(fan_system, "description", None) == fan_system_description:
                fan_system_key = getattr(fan_system, "fanSystemKey", None)
                break
        if not fan_system_key or fan_system_key is MISSING:
            raise ValueError(
                f"Fan system '{fan_system_description}' has no fanSystemKey. "
                "Add fan systems with add_fan_system_to_project so a key is set."
            )

    updated_project = project.model_copy(deep=True)

    # Find and update the HVAC system directly to avoid MISSING serialization issues
    hvac_systems = updated_project.hvac.hvacSystem or []
    for hvac_system in hvac_systems:
        if getattr(hvac_system, "description", None) == hvac_system_description:
            hvac_system.fanSystemKey = fan_system_key
            break

    return updated_project


def get_hvac_system_keys_from_project(project: ComBuilding) -> list[dict]:
    """Return the description, system type, quantity, and fan system info of all HVAC systems.

    Args:
        project: The project to query.

    Returns:
        List of dicts with keys ``description``, ``systemType``, ``quantity``,
        ``fanSystemKey``, and ``fanSystemDescription`` for each HVACSystem in the project.
    """
    if project.hvac is MISSING:
        return []

    hvac_systems = getattr(project.hvac, "hvacSystem", None)
    if not isinstance(hvac_systems, list):
        return []

    # Build a map of fanSystemKey -> description for lookup
    fan_system_map = {}
    fan_systems = getattr(project.hvac, "fanSystem", None) or []
    if isinstance(fan_systems, list):
        for fan_system in fan_systems:
            key = _field_value(fan_system, "fanSystemKey")
            desc = _field_value(fan_system, "description")
            if key:
                fan_system_map[key] = desc

    result = []
    for system in hvac_systems:
        fan_system_key = _field_value(system, "fanSystemKey")
        result.append(
            {
                "description": _field_value(system, "description"),
                "systemType": _field_value(system, "systemType"),
                "quantity": _field_value(system, "quantity"),
                "fanSystemKey": fan_system_key,
                "fanSystemDescription": fan_system_map.get(fan_system_key) if fan_system_key else None,
            }
        )
    return result


# *********** Fan system operations ***********


def add_fan_system_to_project(
    project: ComBuilding,
    new_fan_system: FanSystem,
) -> ComBuilding:
    """Add a new fan system to the project.

    If ``project.hvac`` is ``MISSING``, it is created automatically. The library sets
    ``fanSystemKey`` to a new UUID if it is empty or already used by another fan system.

    Args:
        project: The project to modify.
        new_fan_system: The FanSystem to add.

    Returns:
        Updated project with the new FanSystem added.
    """
    updated_project = project.model_copy(deep=True)
    new_fan_system = new_fan_system.model_copy(deep=True)

    # Ensure hvac exists
    _ensure_hvac(updated_project)

    # Generate or validate fanSystemKey
    current_keys = set()
    fan_systems = updated_project.hvac.fanSystem or []
    for fs in fan_systems:
        key = getattr(fs, "fanSystemKey", None)
        if key and key is not MISSING:
            current_keys.add(key)

    new_key = getattr(new_fan_system, "fanSystemKey", None)
    # Check if key is missing, None, or already exists
    if new_key is MISSING or new_key is None or not new_key or new_key in current_keys:
        new_key = str(uuid4())
        new_fan_system.fanSystemKey = new_key

    updated_project.hvac.append_subcomponent(new_fan_system, subcomponent_name="fanSystem")
    return updated_project


def update_fan_system_in_project(
    project: ComBuilding,
    fan_system_description: str,
    updates: dict[str, Any] | FanSystem,
) -> ComBuilding:
    """Update an existing fan system.

    Engine-calculated fields (``complies``, ``complianceMessage``, ``requirementAnswer``)
    and identity fields (``fanSystemKey``) are rejected.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system to update.
        updates: Partial updates (dict) or full FanSystem to apply.

    Returns:
        Updated project with the fan system modified.

    Raises:
        ValueError: If the fan system is not found, or if updates contain
            disallowed fields.
    """
    _require_fan_system(project, fan_system_description)

    current = _find_by_description(project.hvac.fanSystem, fan_system_description)
    updates = _updates_to_dict(updates)
    _reject_changed_fields(
        current,
        updates,
        _ENGINE_CALCULATED_FAN_SYSTEM_FIELDS
        | _ENGINE_CALCULATED_MECHANICAL_FIELDS
        | _FAN_SYSTEM_IDENTITY_FIELDS,
        "update_fan_system_in_project",
        hint="Use assign_fan_system_to_hvac_system for linking.",
    )

    updated_project = project.model_copy(deep=True)
    updated_project.hvac.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=fan_system_description,
        subcomponent_name="fanSystem",
    )
    return updated_project


def remove_fan_system_from_project(
    project: ComBuilding,
    fan_system_description: str,
) -> ComBuilding:
    """Remove a fan system from the project.

    Also clears ``fanSystemKey`` on any HVAC systems that reference it.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system to remove.

    Returns:
        Updated project with the fan system removed.

    Raises:
        ValueError: If the fan system is not found.
    """
    _require_fan_system(project, fan_system_description)

    # Get the fan system's key before removing it
    fan_systems = project.hvac.fanSystem or []
    removed_key = None
    for fan_system in fan_systems:
        if getattr(fan_system, "description", None) == fan_system_description:
            removed_key = getattr(fan_system, "fanSystemKey", None)
            break

    updated_project = project.model_copy(deep=True)
    updated_project.hvac.remove_from_subcomponent_list(
        subcomponent_id=fan_system_description,
        subcomponent_name="fanSystem",
    )

    # Clear fanSystemKey on HVAC systems that reference the removed fan system
    if removed_key:
        hvac_systems = getattr(updated_project.hvac, "hvacSystem", None) or []
        for hvac_system in hvac_systems:
            if getattr(hvac_system, "fanSystemKey", None) == removed_key:
                hvac_system.fanSystemKey = None

    return updated_project


def get_fan_system_keys_from_project(project: ComBuilding) -> list[dict]:
    """Return the description, fan system key, and comply method of all fan systems.

    Args:
        project: The project to query.

    Returns:
        List of dicts with keys ``description``, ``fanSystemKey``, and ``complyMethod``
        for each FanSystem in the project.
    """
    if project.hvac is MISSING:
        return []

    fan_systems = getattr(project.hvac, "fanSystem", None) or []
    if not isinstance(fan_systems, list):
        return []

    return [
        {
            "description": _field_value(system, "description"),
            "fanSystemKey": _field_value(system, "fanSystemKey"),
            "complyMethod": _field_value(system, "complyMethod"),
        }
        for system in fan_systems
    ]


# *********** Fans and pressure drop credits in a fan system ***********


def add_fan_to_fan_system(
    project: ComBuilding,
    fan_system_description: str,
    new_fan: Fan,
) -> ComBuilding:
    """Add a new fan to a fan system.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system.
        new_fan: The Fan to add.

    Returns:
        Updated project with the new fan added.

    Raises:
        ValueError: If the fan system is not found.
    """
    _require_fan_system(project, fan_system_description)

    updated_project = project.model_copy(deep=True)
    new_fan = new_fan.model_copy(deep=True)

    # Find the fan system and update it
    fan_systems = updated_project.hvac.fanSystem or []
    for fan_system in fan_systems:
        if getattr(fan_system, "description", None) == fan_system_description:
            fan_system.append_subcomponent(new_fan, subcomponent_name="fan")
            break

    return updated_project


def update_fan_in_fan_system(
    project: ComBuilding,
    fan_system_description: str,
    fan_description: str,
    updates: dict[str, Any] | Fan,
) -> ComBuilding:
    """Update an existing fan in a fan system.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system.
        fan_description: The description of the fan to update.
        updates: Partial updates (dict) or full Fan to apply.

    Returns:
        Updated project with the fan modified.

    Raises:
        ValueError: If the fan system or fan is not found.
    """
    _require_fan_system(project, fan_system_description)

    updated_project = project.model_copy(deep=True)

    # Find the fan system and update the fan
    fan_systems = updated_project.hvac.fanSystem or []
    for fan_system in fan_systems:
        if getattr(fan_system, "description", None) == fan_system_description:
            fan_system.update_subcomponent_list(
                subcomponent_updates=updates,
                subcomponent_id=fan_description,
                subcomponent_name="fan",
            )
            break

    return updated_project


def remove_fan_from_fan_system(
    project: ComBuilding,
    fan_system_description: str,
    fan_description: str,
) -> ComBuilding:
    """Remove a fan from a fan system.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system.
        fan_description: The description of the fan to remove.

    Returns:
        Updated project with the fan removed.

    Raises:
        ValueError: If the fan system or fan is not found.
    """
    _require_fan_system(project, fan_system_description)

    updated_project = project.model_copy(deep=True)

    # Find the fan system and remove the fan
    fan_systems = updated_project.hvac.fanSystem or []
    for fan_system in fan_systems:
        if getattr(fan_system, "description", None) == fan_system_description:
            fan_system.remove_from_subcomponent_list(
                subcomponent_id=fan_description,
                subcomponent_name="fan",
            )
            break

    return updated_project


def add_pressure_drop_credit_to_fan_system(
    project: ComBuilding,
    fan_system_description: str,
    new_credit: FanSystemPressureDropCredits,
) -> ComBuilding:
    """Add a pressure drop credit to a fan system.

    Credits are identified by ``type``, which is unique within a fan system.
    ``pressureDropCredit`` is calculated by the engine — use
    :meth:`~comcheck_api.client.COMcheckClient.update_fan_pressure_drop_credits`
    to fill it in.

    Emits a :class:`UserWarning` if the fan system's ``complyMethod`` is not
    ``FAN_SYSTEM_MOTOR_BRAKE_HP``; the UI only offers pressure drop credits for
    the brake horsepower method.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system.
        new_credit: The FanSystemPressureDropCredits to add.

    Returns:
        Updated project with the credit added.

    Raises:
        ValueError: If the fan system is not found, the credit type is
            ``PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED``, or the fan system already
            has a credit of that type.
    """
    _require_fan_system(project, fan_system_description)

    if new_credit.type == PressureDropTypeOptions.PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED:
        raise ValueError(
            "PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED is not a valid credit type. "
            "Choose a value from PressureDropTypeOptions."
        )

    updated_project = project.model_copy(deep=True)
    fan_system = _find_by_description(updated_project.hvac.fanSystem, fan_system_description)
    credits = fan_system.pressureDropCredits
    if credits is MISSING or credits is None:
        credits = []

    if any(credit.type == new_credit.type for credit in credits):
        raise ValueError(
            f"Fan system '{fan_system_description}' already has a "
            f"{new_credit.type} pressure drop credit."
        )

    if fan_system.complyMethod != FanSystemComplianceMethodOptions.FAN_SYSTEM_MOTOR_BRAKE_HP:
        warnings.warn(
            f"Fan system '{fan_system_description}' does not use the "
            "FAN_SYSTEM_MOTOR_BRAKE_HP compliance method, so pressure drop "
            "credits don't apply to it.",
            UserWarning,
            stacklevel=2,
        )

    fan_system.pressureDropCredits = [*credits, new_credit.model_copy(deep=True)]
    return updated_project


def update_pressure_drop_credit_in_fan_system(
    project: ComBuilding,
    fan_system_description: str,
    credit_type: PressureDropTypeOptions,
    updates: dict[str, Any] | FanSystemPressureDropCredits,
) -> ComBuilding:
    """Update the inputs of a pressure drop credit in a fan system.

    ``type`` can't be changed (remove the credit and add a new one), and the
    engine-calculated ``pressureDropCredit`` can't be set. Changing an input
    clears ``pressureDropCredit`` so a stale value isn't kept; recalculate it
    with :meth:`~comcheck_api.client.COMcheckClient.update_fan_pressure_drop_credits`.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system.
        credit_type: The ``type`` of the credit to update.
        updates: Partial updates (dict) or full FanSystemPressureDropCredits to apply.

    Returns:
        Updated project with the credit modified.

    Raises:
        ValueError: If the fan system or credit is not found, updates change
            ``type`` or ``pressureDropCredit``, or a value fails validation.
    """
    _require_fan_system(project, fan_system_description)

    updated_project = project.model_copy(deep=True)
    fan_system = _find_by_description(updated_project.hvac.fanSystem, fan_system_description)
    credits = fan_system.pressureDropCredits
    if credits is MISSING or credits is None:
        credits = []
    index = next(
        (i for i, credit in enumerate(credits) if credit.type == credit_type), None
    )
    if index is None:
        raise ValueError(
            f"Pressure drop credit '{credit_type}' not found in fan system "
            f"'{fan_system_description}'."
        )

    current = credits[index]
    updates = _updates_to_dict(updates)
    _reject_changed_fields(
        current,
        updates,
        frozenset({"type", "pressureDropCredit"}),
        "update_pressure_drop_credit_in_fan_system",
        hint="Remove the credit and add a new one to change its type.",
    )

    merged = {**current.model_dump(mode="python"), **updates}
    if merged != current.model_dump(mode="python"):
        merged.pop("pressureDropCredit", None)
    credits[index] = FanSystemPressureDropCredits.model_validate(merged)
    fan_system.pressureDropCredits = credits
    return updated_project


def remove_pressure_drop_credit_from_fan_system(
    project: ComBuilding,
    fan_system_description: str,
    credit_type: PressureDropTypeOptions,
) -> ComBuilding:
    """Remove a pressure drop credit from a fan system.

    Args:
        project: The project to modify.
        fan_system_description: The description of the fan system.
        credit_type: The ``type`` of the credit to remove.

    Returns:
        Updated project with the credit removed.

    Raises:
        ValueError: If the fan system or credit is not found.
    """
    _require_fan_system(project, fan_system_description)

    updated_project = project.model_copy(deep=True)
    fan_system = _find_by_description(updated_project.hvac.fanSystem, fan_system_description)
    credits = fan_system.pressureDropCredits
    if credits is MISSING or credits is None:
        credits = []
    remaining = [credit for credit in credits if credit.type != credit_type]
    if len(remaining) == len(credits):
        raise ValueError(
            f"Pressure drop credit '{credit_type}' not found in fan system "
            f"'{fan_system_description}'."
        )

    fan_system.pressureDropCredits = remaining
    return updated_project


# *********** Plant operations ***********


def add_hvac_plant_to_project(
    project: ComBuilding,
    new_hvac_plant: HVACPlant,
) -> ComBuilding:
    """Add a new HVAC plant to the project.

    If ``project.hvac`` is ``MISSING``, it is created automatically.

    Args:
        project: The project to modify.
        new_hvac_plant: The HVACPlant to add.

    Returns:
        Updated project with the new HVACPlant added.
    """
    updated_project = project.model_copy(deep=True)
    new_hvac_plant = new_hvac_plant.model_copy(deep=True)

    # Ensure hvac exists
    _ensure_hvac(updated_project)

    updated_project.hvac.append_subcomponent(new_hvac_plant, subcomponent_name="hvacPlant")
    return updated_project


def update_hvac_plant_in_project(
    project: ComBuilding,
    hvac_plant_description: str,
    updates: dict[str, Any] | HVACPlant,
) -> ComBuilding:
    """Update an existing HVAC plant.

    Engine-calculated fields (``requirementAnswer``) are rejected.

    Args:
        project: The project to modify.
        hvac_plant_description: The description of the HVAC plant to update.
        updates: Partial updates (dict) or full HVACPlant to apply.

    Returns:
        Updated project with the HVAC plant modified.

    Raises:
        ValueError: If the HVAC plant is not found, or if updates contain
            engine-calculated fields.
    """
    _require_hvac_plant(project, hvac_plant_description)

    current = _find_by_description(project.hvac.hvacPlant, hvac_plant_description)
    updates = _updates_to_dict(updates)
    _reject_changed_fields(
        current,
        updates,
        _ENGINE_CALCULATED_MECHANICAL_FIELDS,
        "update_hvac_plant_in_project",
    )

    updated_project = project.model_copy(deep=True)
    updated_project.hvac.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=hvac_plant_description,
        subcomponent_name="hvacPlant",
    )
    return updated_project


def remove_hvac_plant_from_project(
    project: ComBuilding,
    hvac_plant_description: str,
) -> ComBuilding:
    """Remove an HVAC plant from the project.

    Args:
        project: The project to modify.
        hvac_plant_description: The description of the HVAC plant to remove.

    Returns:
        Updated project with the HVAC plant removed.

    Raises:
        ValueError: If the HVAC plant is not found.
    """
    _require_hvac_plant(project, hvac_plant_description)

    updated_project = project.model_copy(deep=True)
    updated_project.hvac.remove_from_subcomponent_list(
        subcomponent_id=hvac_plant_description,
        subcomponent_name="hvacPlant",
    )
    return updated_project


def get_hvac_plant_keys_from_project(project: ComBuilding) -> list[dict]:
    """Return the description, plant type, system type, and quantity of all HVAC plants.

    Args:
        project: The project to query.

    Returns:
        List of dicts with keys ``description``, ``plantType``, ``systemType``,
        and ``quantity`` for each HVACPlant in the project.
    """
    if project.hvac is MISSING:
        return []

    hvac_plants = getattr(project.hvac, "hvacPlant", None)
    if not isinstance(hvac_plants, list):
        return []

    return [
        {
            "description": _field_value(plant, "description"),
            "plantType": _field_value(plant, "plantType"),
            "systemType": _field_value(plant, "systemType"),
            "quantity": _field_value(plant, "quantity"),
        }
        for plant in hvac_plants
    ]


# *********** Water heater operations ***********


def add_water_heater_to_project(
    project: ComBuilding,
    new_water_heater: ServiceWaterHeatingSystem,
) -> ComBuilding:
    """Add a new water heater to the project.

    If ``project.swhSystem`` is ``MISSING``, it is initialized to an empty list.

    Args:
        project: The project to modify.
        new_water_heater: The ServiceWaterHeatingSystem to add.

    Returns:
        Updated project with the new ServiceWaterHeatingSystem added.
    """
    updated_project = project.model_copy(deep=True)
    new_water_heater = new_water_heater.model_copy(deep=True)

    # Initialize swhSystem to [] if it's MISSING
    if updated_project.swhSystem is MISSING:
        updated_project.swhSystem = []

    updated_project.append_subcomponent(new_water_heater, subcomponent_name="swhSystem")
    return updated_project


def update_water_heater_in_project(
    project: ComBuilding,
    water_heater_description: str,
    updates: dict[str, Any] | ServiceWaterHeatingSystem,
) -> ComBuilding:
    """Update an existing water heater.

    Engine-calculated fields (``requirementAnswer``) are rejected.

    Args:
        project: The project to modify.
        water_heater_description: The description of the water heater to update.
        updates: Partial updates (dict) or full ServiceWaterHeatingSystem to apply.

    Returns:
        Updated project with the water heater modified.

    Raises:
        ValueError: If the water heater is not found, or if updates
            contain engine-calculated fields.
    """
    _require_water_heater(project, water_heater_description)

    current = _find_by_description(project.swhSystem, water_heater_description)
    updates = _updates_to_dict(updates)
    _reject_changed_fields(
        current,
        updates,
        _ENGINE_CALCULATED_MECHANICAL_FIELDS,
        "update_water_heater_in_project",
    )

    updated_project = project.model_copy(deep=True)
    updated_project.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=water_heater_description,
        subcomponent_name="swhSystem",
    )
    return updated_project


def remove_water_heater_from_project(
    project: ComBuilding,
    water_heater_description: str,
) -> ComBuilding:
    """Remove a water heater from the project.

    Args:
        project: The project to modify.
        water_heater_description: The description of the water heater to remove.

    Returns:
        Updated project with the water heater removed.

    Raises:
        ValueError: If the water heater is not found.
    """
    _require_water_heater(project, water_heater_description)

    updated_project = project.model_copy(deep=True)
    updated_project.remove_from_subcomponent_list(
        subcomponent_id=water_heater_description,
        subcomponent_name="swhSystem",
    )
    return updated_project


def get_water_heater_keys_from_project(project: ComBuilding) -> list[dict]:
    """Return the description, system type, fuel type, and quantity of all water heaters.

    Args:
        project: The project to query.

    Returns:
        List of dicts with keys ``description``, ``swhSystemType``, ``fuelType``,
        and ``quantity`` for each ServiceWaterHeatingSystem in the project.
    """
    water_heaters = project.swhSystem
    if water_heaters is MISSING or not isinstance(water_heaters, list):
        return []

    return [
        {
            "description": _field_value(system, "description"),
            "swhSystemType": _field_value(system, "swhSystemType"),
            "fuelType": _field_value(system, "fuelType"),
            "quantity": _field_value(system, "quantity"),
        }
        for system in water_heaters
    ]


# *********** Helper Functions ***********


def _field_value(item, field: str) -> Any:
    """Return item.field, with an unset (MISSING) field as None."""
    value = getattr(item, field, None)
    return None if value is MISSING else value


def _find_by_description(items, description: str):
    """Return the item in items with the given description (None if not found)."""
    return next(
        (item for item in items or [] if getattr(item, "description", None) == description),
        None,
    )


def _updates_to_dict(updates: dict[str, Any] | BaseModel) -> dict[str, Any]:
    """Convert model updates to a dict the same way DataManager.modify_one does."""
    if isinstance(updates, BaseModel):
        return updates.model_dump(mode="json", exclude_unset=True)
    return updates


def _reject_changed_fields(
    current: BaseModel | None,
    updates: dict[str, Any],
    fields: frozenset[str],
    function_name: str,
    hint: str = "",
) -> None:
    """Raise if updates change any of the given engine-calculated or identity fields.

    A field whose value is unchanged is allowed, so an edited copy of an existing
    item can be passed back as the update.

    Raises:
        ValueError: If any of the fields is set to a different value.
    """
    current_values = current.model_dump(mode="json") if current is not None else {}
    changed = sorted(
        field
        for field in fields & updates.keys()
        if updates[field] != current_values.get(field)
    )
    if changed:
        raise ValueError(
            f"Cannot update engine-calculated or identity fields via {function_name}: "
            f"{changed}. {hint}".rstrip()
        )


def _validate_fan_system_key(project: ComBuilding, fan_system_key: str) -> None:
    """Validate that a fanSystemKey references an existing fan system.

    Args:
        project: The project to check.
        fan_system_key: The fanSystemKey to validate.

    Raises:
        ValueError: If the fanSystemKey does not reference an existing fan system.
    """
    if project.hvac is MISSING:
        raise ValueError(
            f"fanSystemKey '{fan_system_key}' references a non-existent fan system. "
            "No HVAC data found in project."
        )

    fan_systems = getattr(project.hvac, "fanSystem", None) or []
    if not isinstance(fan_systems, list):
        raise ValueError(
            f"fanSystemKey '{fan_system_key}' references a non-existent fan system. "
            "No fan systems found in project."
        )

    if not any(
        getattr(fs, "fanSystemKey", None) == fan_system_key for fs in fan_systems
    ):
        raise ValueError(
            f"fanSystemKey '{fan_system_key}' does not match any existing fan system."
        )
