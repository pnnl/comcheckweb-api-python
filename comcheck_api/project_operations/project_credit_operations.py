"""Project Energy Credit Operations.

Manages energy credits (efficiency packages) at the project level. Credits live
in the flat ``ComBuilding.efficiencyPackages`` list. Each
:class:`~comcheck_api.types.core_types.EfficiencyPackage` entry is tied to a
building area by ``bldgUseKey`` (the ``WholeBldgUse.key``) and identified by
its ``type``; a building area holds at most one entry per credit type.

The extra inputs a credit needs depend on its type, e.g. ``airInfiltration`` and
``airInfiltrationMeasurementType`` for the reduced air infiltration credits or
``onSiteRenewableCapacity`` for on-site renewable credits. See the field
descriptions on ``EfficiencyPackage``.

Project-level fields that also affect credits:

- ``energyCreditMultiplierException`` — IECC 2024 Appendix C/F multiplier exception
- ``projectCoreAndShellCredit`` — credits gained from core and shell

Energy codes
------------
Energy credits apply to IECC 2021+, ASHRAE 90.1-2022, and state codes based on
them, and each code family has its own credit types (``EFF_PACKAGE_ENERGY_CREDIT_*``,
``EFF_PACKAGE_ENERGY_CREDIT_IECC2024_*``, ``ENERGY_CREDIT_VT_2024_*``, ...). These
operations don't check ``control.code`` — which credits fit the project is up to
you. Use :meth:`~comcheck_api.client.COMcheckClient.calculate_energy_credits` to
get the proposed and required credits.
"""

from typing import Any
from pydantic.experimental.missing_sentinel import MISSING

from comcheck_api.types.core_types import (
    ComBuilding,
    EfficiencyPackage,
    EnergyCreditMultiplierException,
)
from comcheck_api.utilities.project_utilities import _require_building_area

# Identity fields; change them with remove + add instead
_IDENTITY_FIELDS = frozenset({"type", "bldgUseKey"})


def _find_energy_credit_index(
    project: ComBuilding, building_area_key: str, credit_type: str
) -> int | None:
    efficiency_packages = project.efficiencyPackages
    if efficiency_packages is MISSING:
        return None
    for index, efficiency_package in enumerate(efficiency_packages):
        if efficiency_package.bldgUseKey == building_area_key and str(
            efficiency_package.type
        ) == str(credit_type):
            return index
    return None


def _require_energy_credit_index(
    project: ComBuilding, building_area_key: str, credit_type: str
) -> int:
    index = _find_energy_credit_index(project, building_area_key, credit_type)
    if index is None:
        raise ValueError(
            f"Energy credit '{credit_type}' not found for building area "
            f"'{building_area_key}' in efficiencyPackages."
        )
    return index


def add_energy_credit_to_project(
    project: ComBuilding,
    building_area_key: str,
    new_energy_credit: EfficiencyPackage,
) -> ComBuilding:
    """Add an energy credit to a building area.

    ``new_energy_credit.bldgUseKey`` is set to ``building_area_key``.

    Args:
        project: The project to modify.
        building_area_key: The key of the building area (``WholeBldgUse.key``)
            that gets the credit.
        new_energy_credit: The EfficiencyPackage to add. ``type`` selects the
            credit; set the inputs that credit needs.

    Returns:
        Updated project with the energy credit added.

    Raises:
        ValueError: If the building area is not found, or it already has a
            credit of the same type.
    """
    _require_building_area(project, building_area_key)
    if (
        _find_energy_credit_index(project, building_area_key, new_energy_credit.type)
        is not None
    ):
        raise ValueError(
            f"Building area '{building_area_key}' already has energy credit "
            f"'{new_energy_credit.type}'. Use update_energy_credit_in_project to change it."
        )

    updated_project = project.model_copy(deep=True)
    new_energy_credit = new_energy_credit.model_copy(deep=True)
    new_energy_credit.bldgUseKey = building_area_key

    if updated_project.efficiencyPackages is MISSING:
        updated_project.efficiencyPackages = []
    updated_project.efficiencyPackages.append(new_energy_credit)
    return updated_project


def update_energy_credit_in_project(
    project: ComBuilding,
    building_area_key: str,
    credit_type: str,
    updates: dict[str, Any],
) -> ComBuilding:
    """Update the inputs of an existing energy credit.

    ``type`` and ``bldgUseKey`` identify the credit and cannot be updated here;
    remove the credit and add a new one instead.

    Args:
        project: The project to modify.
        building_area_key: The key of the building area that has the credit.
        credit_type: The ``type`` of the credit to update.
        updates: Partial updates (dict) to apply to the EfficiencyPackage.

    Returns:
        Updated project with the energy credit modified.

    Raises:
        ValueError: If the credit is not found, updates contains ``type`` or
            ``bldgUseKey``, or a value fails validation.
    """
    index = _require_energy_credit_index(project, building_area_key, credit_type)

    disallowed = _IDENTITY_FIELDS & updates.keys()
    if disallowed:
        raise ValueError(
            f"Cannot update {sorted(disallowed)} via update_energy_credit_in_project. "
            "Remove the energy credit and add a new one instead."
        )

    # Revalidate the merged entry — plain setattr skips Pydantic validation
    updated_project = project.model_copy(deep=True)
    current = updated_project.efficiencyPackages[index]
    merged = {**current.model_dump(mode="python"), **updates}
    updated_project.efficiencyPackages[index] = EfficiencyPackage.model_validate(merged)
    return updated_project


def remove_energy_credit_from_project(
    project: ComBuilding,
    building_area_key: str,
    credit_type: str,
) -> ComBuilding:
    """Remove an energy credit from a building area.

    Args:
        project: The project to modify.
        building_area_key: The key of the building area that has the credit.
        credit_type: The ``type`` of the credit to remove.

    Returns:
        Updated project with the energy credit removed.

    Raises:
        ValueError: If the credit is not found.
    """
    index = _require_energy_credit_index(project, building_area_key, credit_type)

    updated_project = project.model_copy(deep=True)
    del updated_project.efficiencyPackages[index]
    return updated_project


def get_energy_credit_keys_from_project(
    project: ComBuilding,
    building_area_key: str | None = None,
) -> list[dict]:
    """Return the building area key and type of the project's energy credits.

    Args:
        project: The project to query.
        building_area_key: Only return credits of this building area. Returns
            all credits when ``None``.

    Returns:
        List of dicts with keys ``bldgUseKey`` and ``type`` for each
        EfficiencyPackage in the project.
    """
    efficiency_packages = project.efficiencyPackages
    if efficiency_packages is MISSING:
        return []
    return [
        {
            "bldgUseKey": efficiency_package.bldgUseKey,
            "type": efficiency_package.type,
        }
        for efficiency_package in efficiency_packages
        if building_area_key is None
        or efficiency_package.bldgUseKey == building_area_key
    ]


def set_energy_credit_multiplier_exception_in_project(
    project: ComBuilding,
    multiplier_exception: EnergyCreditMultiplierException,
) -> ComBuilding:
    """Set the energy credit multiplier exception on the project.

    Used by IECC 2024 Appendix C/F for new construction and additions.

    Args:
        project: The project to modify.
        multiplier_exception: An
            :class:`~comcheck_api.types.core_types.EnergyCreditMultiplierException`
            value.

    Returns:
        Updated project with the multiplier exception set.

    Raises:
        TypeError: If multiplier_exception is not an EnergyCreditMultiplierException member.
    """
    if not isinstance(multiplier_exception, EnergyCreditMultiplierException):
        raise TypeError(
            f"multiplier_exception must be an EnergyCreditMultiplierException member, "
            f"got {type(multiplier_exception).__name__!r}."
        )

    updated_project = project.model_copy(deep=True)
    updated_project.energyCreditMultiplierException = multiplier_exception
    return updated_project


def set_core_and_shell_credit_in_project(
    project: ComBuilding,
    core_and_shell_credit: float | None,
) -> ComBuilding:
    """Set the credits gained from core and shell on the project.

    Applies to initial build-out projects whose mechanical type is core and shell.

    Args:
        project: The project to modify.
        core_and_shell_credit: Credits gained from core and shell, or ``None``
            to clear them.

    Returns:
        Updated project with ``projectCoreAndShellCredit`` set.

    Raises:
        ValueError: If core_and_shell_credit is negative.
    """
    if core_and_shell_credit is not None and core_and_shell_credit < 0:
        raise ValueError("core_and_shell_credit must not be negative.")

    updated_project = project.model_copy(deep=True)
    updated_project.projectCoreAndShellCredit = core_and_shell_credit
    return updated_project
