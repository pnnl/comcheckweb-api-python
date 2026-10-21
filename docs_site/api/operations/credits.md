# Credits Operations

Energy credits are stored in the flat `ComBuilding.efficiencyPackages` list.
Each `EfficiencyPackage` entry:

- belongs to one building area — `bldgUseKey` is the `WholeBldgUse.key`
- is identified by its `type` — a building area holds at most one entry per credit type
- carries the inputs its credit type needs, e.g. `airInfiltration` for the
  reduced air infiltration credits or `onSiteRenewableCapacity` for on-site
  renewable credits (see the field descriptions on `EfficiencyPackage`)

Two project-level fields also affect credits:

- `energyCreditMultiplierException` — the IECC 2024 Appendix C/F energy credit
  multiplier exception (new construction and additions)
- `projectCoreAndShellCredit` — credits gained from core and shell (initial
  build-out with a core and shell mechanical type)

## Energy codes

Energy credits apply to IECC 2021 and newer, ASHRAE 90.1-2022, and state codes
based on them. Each code family has its own credit types:

| Code family | Credit type enum | Prefix |
|---|---|---|
| IECC 2021, ASHRAE 90.1-2022 | `EfficiencyPackageTypeOptions` | `EFF_PACKAGE_ENERGY_CREDIT_` |
| IECC 2024 (incl. Appendix C/F, NYS 2024, NYC 2025) | `IECC2024EnergyCreditTypeOptions` | `EFF_PACKAGE_ENERGY_CREDIT_IECC2024_` |
| Massachusetts Stretch | `MAS2022EnergyCreditTypeOptions` | `EFF_PACKAGE_ENERGY_CREDIT_MAS_` |
| Denver | `Denver2022EnergyCreditTypeOptions` | `EFF_PACKAGE_ENERGY_CREDIT_DENVER_` |
| Vermont 2024 | `VT2024EnergyCreditTypeOptions` | `ENERGY_CREDIT_VT_2024_` |

These operations don't check `control.code` — which credits fit the project is
up to you. Older codes that use additional efficiency packages instead
(IECC 2015/2018) get `0` proposed and required credits from the calculation.

## Operations

```python
from comcheck_api import project_credit_operations as cr_ops
```

| Function | Description |
|---|---|
| `add_energy_credit_to_project(project, building_area_key, new_energy_credit)` | Add an energy credit to a building area |
| `update_energy_credit_in_project(project, building_area_key, credit_type, updates)` | Update the inputs of an existing energy credit |
| `remove_energy_credit_from_project(project, building_area_key, credit_type)` | Remove an energy credit from a building area |
| `get_energy_credit_keys_from_project(project, building_area_key=None)` | List the `bldgUseKey` and `type` of the energy credits |
| `set_energy_credit_multiplier_exception_in_project(project, multiplier_exception)` | Set `energyCreditMultiplierException` |
| `set_core_and_shell_credit_in_project(project, core_and_shell_credit)` | Set `projectCoreAndShellCredit` |

Removing a building area with
`project_building_area_operations.remove_building_area_from_project` also
removes its energy credits.

## Adding and updating credits

```python
from comcheck_api import project_credit_operations as cr_ops
from comcheck_api.types.core_types import (
    EfficiencyPackage,
    IECC2024EnergyCreditTypeOptions as Credit,
)

area_key = project.lighting.wholeBldgUse[0].key

project = cr_ops.add_energy_credit_to_project(
    project,
    area_key,
    EfficiencyPackage(type=Credit.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_ENHANCED_ROOF_R10),
)

project = cr_ops.add_energy_credit_to_project(
    project,
    area_key,
    EfficiencyPackage(
        type=Credit.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_REDUCE_AIR_INFILTRATION,
        airInfiltration=0.25,
        airInfiltrationMeasurementType="AIR_INFILTRATION_MEASUREMENT_75PA",
    ),
)

project = cr_ops.update_energy_credit_in_project(
    project,
    area_key,
    Credit.EFF_PACKAGE_ENERGY_CREDIT_IECC2024_REDUCE_AIR_INFILTRATION,
    {"airInfiltration": 0.2},
)
```

`type` and `bldgUseKey` can't be updated — remove the credit and add a new one.

## Calculating credits

`COMcheckClient.calculate_energy_credits` sends the project to
`POST /update-energy-credits` and returns an `EnergyCreditResult`. The project
is not modified.

```python
from comcheck_api import COMcheckClient

with COMcheckClient(api_key="your-key") as client:
    result = client.calculate_energy_credits(project)

print(f"Credits - Required: {result.required} Proposed: {result.proposed}")
for credit in result.energyCredits:
    print(credit.bldgUseKey, credit.creditType, credit.value)
for alert in result.userAlerts:
    print(alert.level, alert.message)
print("Meets required credits:", result.passes)
```

| Field | Description |
|---|---|
| `energyCredits` | Credits achieved per building area (`bldgUseKey`) and credit type (`creditType`). `category` is `regular`, or `renewable_load` for renewable and load management credits, and may be `None` from older backends. `value` is weighted by the building area's share of the gross floor area. |
| `proposed` / `required` | Total proposed and required credits |
| `proposedRenewableAndLoadMgmt` / `requiredRenewableAndLoadMgmt` | Renewable and load management credits, reported separately by codes with the renewable trade-off (IECC 2024, Vermont 2024); `0` otherwise |
| `warnings` | Calculation warnings, e.g. a credit missing an input |
| `userAlerts` | Alerts for the user, e.g. insufficient credits |
| `passes` | `True` when proposed credits (and renewable and load management credits) meet the required credits; `None` when the totals are missing |

`passes` is derived from the totals. The compliance check
(`COMcheckClient.check_UA_compliance`) reports the official energy credit status.
