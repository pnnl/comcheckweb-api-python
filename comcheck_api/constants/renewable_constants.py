"""Renewable energy constants for COMcheck projects."""

from comcheck_api.types.core_types import (
    OffsiteRenewableProcurement,
    OffsiteRenewableProcurementType,
    RenewableSystem,
    RenewableSystemTypeOptions,
    RenewableSystemCapacityUnitOptions,
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
