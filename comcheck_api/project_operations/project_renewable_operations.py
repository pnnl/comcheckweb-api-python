"""Project Renewable Energy Operations.

Manages renewable energy systems and off-site procurement at the project level.
The renewable data lives in ``ComBuilding.renewable`` (a required singleton
``Renewable`` object), which carries:

- ``renewableException`` — the user's exception selection (can coexist with systems)
- Sizing scalars — ``numberOfFloors``, ``largestThreeFloorArea``, ``roofAreaForRenewable``,
  ``requiredCapacity``, ``proposedCapacity``
- ``renewableSystem[]`` — list of on-site ``RenewableSystem``
- Off-site fields — ``requiredOffsiteRenewableEnergy``, ``proposedOffsiteRenewableEnergy``,
  and ``offsiteRenewableProcurement[]``

Energy codes
------------
Renewable requirements only apply under some energy codes (and state codes
based on them). These operations don't check ``control.code`` — whether the
project needs renewable data is up to you.

Exception and systems coexistence
----------------------------------
Setting a renewable exception does **not** preclude adding on-site renewable
systems, and vice versa — the two can coexist on the same project.

Off-site procurement
--------------------
Off-site renewable procurement is **not** always present. Before adding any
``offsiteRenewableProcurement[]`` entry, confirm with the user that the project
actually uses off-site procurement.
"""

import logging
from typing import Any
from pydantic.experimental.missing_sentinel import MISSING

from comcheck_api.types.core_types import (
    ComBuilding,
    Renewable,
    RenewableExceptionOptions,
    RenewableSystem,
    OffsiteRenewableProcurement,
)
from comcheck_api.utilities.project_utilities import (
    _require_renewable_system,
    _require_offsite_renewable_procurement,
)

logger = logging.getLogger(__name__)

# Engine-calculated or API-calculated fields that must not be writable via update_renewable_in_project
_ENGINE_CALCULATED_RENEWABLE_FIELDS = frozenset(
    {
        "requiredCapacity",
        "proposedCapacity",
        "requiredOffsiteRenewableEnergy",
        "proposedOffsiteRenewableEnergy",
        "largestThreeFloorArea",
        "roofAreaForRenewable",
    }
)

# List fields that must not be writable via update_renewable_in_project (use list operations instead)
_LIST_FIELDS = frozenset(
    {
        "renewableSystem",
        "offsiteRenewableProcurement",
    }
)


def set_renewable_exception_in_project(
    project: ComBuilding,
    renewable_exception: RenewableExceptionOptions,
) -> ComBuilding:
    """Set the renewable exception on the project.

    On-site renewable systems and an exception can coexist — setting an exception
    does not preclude adding ``renewableSystem[]``, and vice versa.

    Args:
        project: The project to modify.
        renewable_exception: A :class:`~comcheck_api.types.core_types.RenewableExceptionOptions`
            value. Must not be ``NoneType_None``.

    Returns:
        Updated project with the renewable exception set.

    Raises:
        TypeError: If renewable_exception is not a RenewableExceptionOptions member.
        ValueError: If renewable_exception is NoneType_None.
    """
    if not isinstance(renewable_exception, RenewableExceptionOptions):
        raise TypeError(
            f"renewable_exception must be a RenewableExceptionOptions member, "
            f"got {type(renewable_exception).__name__!r}."
        )
    if renewable_exception == RenewableExceptionOptions.NoneType_None:
        raise ValueError(
            "NoneType_None is not a valid renewable exception. "
            "Choose a value from RenewableExceptionOptions other than NoneType_None."
        )

    updated_project = project.model_copy(deep=True)
    updated_project.renewable.renewableException = renewable_exception
    return updated_project


def update_renewable_in_project(
    project: ComBuilding,
    updates: dict[str, Any],
) -> ComBuilding:
    """Update scalar fields on the renewable singleton.

    Only user-writable scalar fields (``numberOfFloors``) may be updated here.
    Engine-calculated fields (``requiredCapacity``, ``proposedCapacity``,
    ``requiredOffsiteRenewableEnergy``, ``proposedOffsiteRenewableEnergy``),
    API-calculated fields (``largestThreeFloorArea``, ``roofAreaForRenewable``),
    and list fields (``renewableSystem``, ``offsiteRenewableProcurement``) are
    rejected.

    Args:
        project: The project to modify.
        updates: Partial updates (dict) to apply to the renewable singleton.

    Returns:
        Updated project with the renewable singleton modified.

    Raises:
        ValueError: If updates contains renewableException, engine-calculated,
            API-calculated, or list fields; if a value fails validation (e.g.
            negative numberOfFloors).
    """
    if "renewableException" in updates:
        raise ValueError(
            "Use set_renewable_exception_in_project to change renewableException."
        )

    disallowed = (_ENGINE_CALCULATED_RENEWABLE_FIELDS | _LIST_FIELDS) & updates.keys()
    if disallowed:
        raise ValueError(
            f"Cannot update engine-calculated, API-calculated, or list fields via update_renewable_in_project: "
            f"{sorted(disallowed)}. Use list operations for renewableSystem and offsiteRenewableProcurement."
        )

    # Revalidate the merged singleton — plain setattr skips Pydantic validation,
    # so e.g. a negative or non-integer numberOfFloors would slip through.
    updated_project = project.model_copy(deep=True)
    merged = {**updated_project.renewable.model_dump(mode="python"), **updates}
    updated_project.renewable = Renewable.model_validate(merged)
    return updated_project


def add_renewable_system_to_project(
    project: ComBuilding,
    new_renewable_system: RenewableSystem,
) -> ComBuilding:
    """Add a new on-site renewable system to the project.

    On-site renewable systems can coexist with a renewable exception.

    Args:
        project: The project to modify.
        new_renewable_system: The RenewableSystem to add.

    Returns:
        Updated project with the new RenewableSystem added.
    """
    updated_project = project.model_copy(deep=True)
    new_renewable_system = new_renewable_system.model_copy(deep=True)
    updated_project.renewable.append_subcomponent(new_renewable_system)
    return updated_project


def update_renewable_system_in_project(
    project: ComBuilding,
    renewable_system_description: str,
    updates: dict[str, Any] | RenewableSystem,
) -> ComBuilding:
    """Update an existing on-site renewable system.

    Args:
        project: The project to modify.
        renewable_system_description: The description of the RenewableSystem to update.
        updates: Partial updates (dict) or full RenewableSystem to apply.

    Returns:
        Updated project with the RenewableSystem modified.

    Raises:
        ValueError: If the renewable system is not found.
    """
    _require_renewable_system(project, renewable_system_description)

    updated_project = project.model_copy(deep=True)
    updated_project.renewable.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=renewable_system_description,
        subcomponent_name="renewableSystem",
    )
    return updated_project


def remove_renewable_system_from_project(
    project: ComBuilding,
    renewable_system_description: str,
) -> ComBuilding:
    """Remove an on-site renewable system from the project.

    Args:
        project: The project to modify.
        renewable_system_description: The description of the RenewableSystem to remove.

    Returns:
        Updated project with the RenewableSystem removed.

    Raises:
        ValueError: If the renewable system is not found.
    """
    _require_renewable_system(project, renewable_system_description)

    updated_project = project.model_copy(deep=True)
    updated_project.renewable.remove_from_subcomponent_list(
        subcomponent_id=renewable_system_description,
        subcomponent_name="renewableSystem",
    )
    return updated_project


def get_renewable_system_keys_from_project(project: ComBuilding) -> list[dict]:
    """Return the description, type, capacity, and unit of all renewable systems.

    Args:
        project: The project to query.

    Returns:
        List of dicts with keys ``description``, ``renewableSystemType``,
        ``renewableSystemCapacity``, and ``renewableSystemCapacityUnit``
        for each RenewableSystem in the project.
    """
    renewable_systems = project.get_by_path("renewable.renewableSystem")
    if not isinstance(renewable_systems, list):
        return []
    return [
        {
            "description": getattr(system, "description", None),
            "renewableSystemType": getattr(system, "renewableSystemType", None),
            "renewableSystemCapacity": getattr(system, "renewableSystemCapacity", None),
            "renewableSystemCapacityUnit": getattr(
                system, "renewableSystemCapacityUnit", None
            ),
        }
        for system in renewable_systems
    ]


def add_offsite_renewable_procurement_to_project(
    project: ComBuilding,
    new_procurement: OffsiteRenewableProcurement,
) -> ComBuilding:
    """Add a new offsite renewable procurement to the project.

    .. note::
        Off-site renewable procurement is **not** always present. Confirm with
        the user that the project actually uses off-site procurement before
        calling this function.

    Args:
        project: The project to modify.
        new_procurement: The OffsiteRenewableProcurement to add.

    Returns:
        Updated project with the new OffsiteRenewableProcurement added.
    """
    updated_project = project.model_copy(deep=True)
    new_procurement = new_procurement.model_copy(deep=True)

    # Initialize offsiteRenewableProcurement to [] if it's MISSING
    if updated_project.renewable.offsiteRenewableProcurement is MISSING:
        updated_project.renewable.offsiteRenewableProcurement = []

    updated_project.renewable.append_subcomponent(new_procurement)
    return updated_project


def update_offsite_renewable_procurement_in_project(
    project: ComBuilding,
    procurement_description: str,
    updates: dict[str, Any] | OffsiteRenewableProcurement,
) -> ComBuilding:
    """Update an existing offsite renewable procurement.

    Args:
        project: The project to modify.
        procurement_description: The description of the OffsiteRenewableProcurement to update.
        updates: Partial updates (dict) or full OffsiteRenewableProcurement to apply.

    Returns:
        Updated project with the OffsiteRenewableProcurement modified.

    Raises:
        ValueError: If the offsite renewable procurement is not found.
    """
    _require_offsite_renewable_procurement(project, procurement_description)

    updated_project = project.model_copy(deep=True)
    updated_project.renewable.update_subcomponent_list(
        subcomponent_updates=updates,
        subcomponent_id=procurement_description,
        subcomponent_name="offsiteRenewableProcurement",
    )
    return updated_project


def remove_offsite_renewable_procurement_from_project(
    project: ComBuilding,
    procurement_description: str,
) -> ComBuilding:
    """Remove an offsite renewable procurement from the project.

    Args:
        project: The project to modify.
        procurement_description: The description of the OffsiteRenewableProcurement to remove.

    Returns:
        Updated project with the OffsiteRenewableProcurement removed.

    Raises:
        ValueError: If the offsite renewable procurement is not found.
    """
    _require_offsite_renewable_procurement(project, procurement_description)

    updated_project = project.model_copy(deep=True)
    updated_project.renewable.remove_from_subcomponent_list(
        subcomponent_id=procurement_description,
        subcomponent_name="offsiteRenewableProcurement",
    )
    return updated_project


def get_offsite_renewable_procurement_keys_from_project(
    project: ComBuilding,
) -> list[dict]:
    """Return the description, type, and energy of all offsite renewable procurements.

    Args:
        project: The project to query.

    Returns:
        List of dicts with keys ``description``, ``offsiteRenewableProcurementType``,
        and ``offsiteRenewableEnergy`` for each OffsiteRenewableProcurement in the project.
    """
    offsite_procurements = project.get_by_path("renewable.offsiteRenewableProcurement")
    if offsite_procurements is MISSING or not isinstance(offsite_procurements, list):
        return []
    return [
        {
            "description": getattr(procurement, "description", None),
            "offsiteRenewableProcurementType": getattr(
                procurement, "offsiteRenewableProcurementType", None
            ),
            "offsiteRenewableEnergy": getattr(
                procurement, "offsiteRenewableEnergy", None
            ),
        }
        for procurement in offsite_procurements
    ]
