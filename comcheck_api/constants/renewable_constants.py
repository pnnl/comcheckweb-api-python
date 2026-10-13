"""Renewable energy constants for COMcheck projects."""

from comcheck_api.types.core_types import (
    EnergyCodeOptions,
    OffsiteRenewableProcurement,
    OffsiteRenewableProcurementType,
    RenewableSystem,
    RenewableSystemTypeOptions,
    RenewableSystemCapacityUnitOptions,
)

# Supported energy codes for renewable operations (ASHRAE 90.1 2022, IECC 2024, and state codes based on them)
RENEWABLE_SUPPORTED_CODES = frozenset(
    {
        EnergyCodeOptions.CEZ_90_1_2022,
        EnergyCodeOptions.CEZ_IECC2024,
        EnergyCodeOptions.CEZ_IECC2024_APPXCF,
    }
)

DEFAULT_RENEWABLE_SYSTEM: RenewableSystem = RenewableSystem(
    description="Solar PV",
    renewableSystemType=RenewableSystemTypeOptions.RENEWABLE_SYSTEM_TYPE_SOLAR,
    renewableSystemCapacity=0.0,
    renewableSystemCapacityUnit=RenewableSystemCapacityUnitOptions.RENEWABLE_SYSTEM_UNIT_WATT,
)

DEFAULT_OFFSITE_RENEWABLE_PROCUREMENT: OffsiteRenewableProcurement = (
    OffsiteRenewableProcurement(
        description="Offsite Procurement",
        offsiteRenewableProcurementType=OffsiteRenewableProcurementType.OFFSITE_RENEWABLE_PROCUREMENT_UNSPECIFIED,
        offsiteRenewableEnergy=0.0,
    )
)
