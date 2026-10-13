# Renewable Energy Operations

Renewable energy is managed at the **project level** through the
`ComBuilding.renewable` singleton. The `Renewable` object carries:

- `renewableException` — the user's exception selection
- Sizing scalars — `numberOfFloors`, `largestThreeFloorArea`, `roofAreaForRenewable`,
  `requiredCapacity`, `proposedCapacity`
- `renewableSystem[]` — list of on-site renewable systems
- Off-site fields — `requiredOffsiteRenewableEnergy`, `proposedOffsiteRenewableEnergy`,
  and `offsiteRenewableProcurement[]`

## Supported energy codes

Renewable operations require one of the supported energy codes:

- ASHRAE 90.1 2022 (`CEZ_90_1_2022`)
- IECC 2024 (`CEZ_IECC2024`)
- IECC 2024 Appendix C/F (`CEZ_IECC2024_APPXCF`)
- State codes based on the above

All mutating operations raise `ValueError` for unsupported codes.

## Key concepts

- **Exception and systems coexist.** Setting a renewable exception does **not**
  preclude adding on-site renewable systems, and vice versa — the two can
  coexist on the same project.

- **Off-site procurement confirmation.** Off-site renewable procurement is
  **not** always present. Before adding any `offsiteRenewableProcurement[]`
  entry, confirm with the user that the project actually uses off-site
  procurement.

- **Read-only operations work for any code.** The `get_*_keys` functions work
  for any energy code, not just the supported set.

## description uniqueness

`description` must be unique within `renewable.renewableSystem[]` and
`renewable.offsiteRenewableProcurement[]`. It is the identifier used by update
and remove operations. If missing, a unique value is auto-generated with the
prefix `"Renewable System"` or `"Offsite Procurement"`.

## Operations

```python
from comcheck_api import project_renewable_operations as rn_ops
```

| Function | Description |
|---|---|
| `set_renewable_exception_in_project(project, renewable_exception)` | Set the renewable exception (rejects `NoneType_None`) |
| `update_renewable_in_project(project, updates)` | Update scalar fields on the renewable singleton |
| `add_renewable_system_to_project(project, new_renewable_system)` | Add a new on-site renewable system |
| `update_renewable_system_in_project(project, renewable_system_description, updates)` | Update an existing renewable system |
| `remove_renewable_system_from_project(project, renewable_system_description)` | Remove a renewable system |
| `get_renewable_system_keys_from_project(project)` | List all renewable systems in the project |
| `add_offsite_renewable_procurement_to_project(project, new_procurement)` | Add a new offsite renewable procurement |
| `update_offsite_renewable_procurement_in_project(project, procurement_description, updates)` | Update an existing offsite renewable procurement |
| `remove_offsite_renewable_procurement_from_project(project, procurement_description)` | Remove an offsite renewable procurement |
| `get_offsite_renewable_procurement_keys_from_project(project)` | List all offsite renewable procurements |

## Setting the renewable exception

```python
from comcheck_api import project_renewable_operations as rn_ops
from comcheck_api.types.core_types import RenewableExceptionOptions

project = rn_ops.set_renewable_exception_in_project(
    project, RenewableExceptionOptions.RENEWABLE_ONSITE_EXCEPTION_LOW_SOLAR_RAD
)
```

`NoneType_None` is rejected with a `ValueError`. A raw string raises a
`TypeError` — always use the enum.

## Adding an on-site renewable system

```python
from comcheck_api.defaults import get_default_renewable_system_template
from comcheck_api.types.core_types import (
    RenewableSystemTypeOptions,
    RenewableSystemCapacityUnitOptions,
)

renewable_system = get_default_renewable_system_template()
renewable_system.description = "Rooftop Solar"
renewable_system.renewableSystemType = RenewableSystemTypeOptions.RENEWABLE_SYSTEM_TYPE_SOLAR
renewable_system.renewableSystemCapacity = 50000.0
renewable_system.renewableSystemCapacityUnit = RenewableSystemCapacityUnitOptions.RENEWABLE_SYSTEM_UNIT_WATT

project = rn_ops.add_renewable_system_to_project(project, renewable_system)
```

## Updating a renewable system

Pass only the fields you want to change — unchanged fields are preserved:

```python
project = rn_ops.update_renewable_system_in_project(
    project,
    "Rooftop Solar",
    {"renewableSystemCapacity": 75000.0},
)
```

## Adding offsite renewable procurement

!!! note
    Off-site renewable procurement is **not** always present. Confirm with the
    user that the project actually uses off-site procurement before calling
    this function.

```python
from comcheck_api.defaults import get_default_offsite_renewable_procurement_template
from comcheck_api.types.core_types import OffsiteRenewableProcurementType

offsite_procurement = get_default_offsite_renewable_procurement_template()
offsite_procurement.description = "Wind PPA"
offsite_procurement.offsiteRenewableProcurementType = OffsiteRenewableProcurementType.OFFSITE_RENEWABLE_PROCUREMENT_PHYSICAL_AGREEMENT
offsite_procurement.offsiteRenewableEnergy = 100000.0  # kWh

project = rn_ops.add_offsite_renewable_procurement_to_project(project, offsite_procurement)
```

## Updating scalar fields

Only user-writable scalar fields (currently just `numberOfFloors`) may be
updated via `update_renewable_in_project`. Engine-calculated fields
(`requiredCapacity`, `proposedCapacity`, `requiredOffsiteRenewableEnergy`,
`proposedOffsiteRenewableEnergy`), API-calculated fields
(`largestThreeFloorArea`, `roofAreaForRenewable`), and list fields
(`renewableSystem`, `offsiteRenewableProcurement`) are rejected with a
`ValueError`:

```python
project = rn_ops.update_renewable_in_project(project, {"numberOfFloors": 5})
```

## Renewable area calculation (placeholder)

!!! warning "Pending Implementation"
    The `COMcheckClient.update_renewable_area` method is a placeholder. The
    `area-for-renewable` endpoint is pending implementation in the external
    `comcheck-cdk` repository.

The `update_renewable_area` method will calculate `largestThreeFloorArea` and
`roofAreaForRenewable` from the project envelope/geometry once the endpoint is
available. It follows the same pattern as `update_uvalues`:

```python
# This will raise NotImplementedError until the endpoint is available
# project = client.update_renewable_area(project)
```

## Removing renewable systems

```python
project = rn_ops.remove_renewable_system_from_project(project, "Rooftop Solar")
```

## Removing offsite renewable procurement

```python
project = rn_ops.remove_offsite_renewable_procurement_from_project(project, "Wind PPA")
```

## Listing renewable systems and procurements

```python
renewable_systems = rn_ops.get_renewable_system_keys_from_project(project)
# [{"description": "Rooftop Solar", "renewableSystemType": "RENEWABLE_SYSTEM_TYPE_SOLAR", ...}]

offsite_procurements = rn_ops.get_offsite_renewable_procurement_keys_from_project(project)
# [{"description": "Wind PPA", "offsiteRenewableProcurementType": "...", ...}]
```

## Related

- [Types Guide](types-guide.md) — `Renewable`, `RenewableSystem`, `OffsiteRenewableProcurement`
- [Interior Lighting](interior-lighting.md) — Similar pattern for lighting spaces
- [Exterior Lighting](exterior-lighting.md) — Similar pattern for exterior lighting areas
