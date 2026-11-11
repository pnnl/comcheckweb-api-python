# Project Defaults

Functions that return deep copies of pre-configured default templates for
projects and building components. Each call returns a new copy, so customize
it freely and pass it to the matching `add_*` operation.

```python
from comcheck_api.defaults import get_default_roof_template

roof = get_default_roof_template()
roof.grossArea = 8000.0
project = project_envelope_operations.add_roof_to_project(
    project, building_area_key=area_key, new_roof=roof
)
```

## Project

::: comcheck_api.defaults.get_default_project_template
    options:
      heading_level: 3

## Building Area

Pass to `add_building_area_to_project`. Each call gets a fresh `key` and a unique `areaDescription`.

See [Building Area operations](operations/building-area.md).

::: comcheck_api.defaults.get_default_building_area_template
    options:
      heading_level: 3

## Envelope

Pass to the matching `add_*_to_project` function in `project_envelope_operations`. `add_thermal_bridge_to_project` is the exception: it takes the thermal bridge values as arguments (`psi_factor`, `thermal_bridge_length`, ...) rather than a `ThermalBridge`, so use the template as a reference for those values.

See [Envelope operations](operations/envelope.md).

::: comcheck_api.defaults.get_default_roof_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_ag_wall_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_bg_wall_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_floor_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_window_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_door_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_skylight_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_thermal_bridge_template
    options:
      heading_level: 3

## Interior Lighting

Pass the interior space to `add_interior_space_to_project`. Fixtures go in `interiorLightingSpace.fixture[]` or through `update_fixtures_in_interior_space`; the same fixture template is used for [exterior lighting](#exterior-lighting).

See [Interior Lighting operations](operations/interior-lighting.md).

::: comcheck_api.defaults.get_default_interior_space_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_fixture_template
    options:
      heading_level: 3

## Exterior Lighting

Pass to `add_exterior_area_to_project`. Use `get_default_fixture_template` (above) for its fixtures.

See [Exterior Lighting operations](operations/exterior-lighting.md).

::: comcheck_api.defaults.get_default_exterior_area_template
    options:
      heading_level: 3

## Mechanical

Pass to `add_hvac_system_to_project`, `add_fan_system_to_project`, `add_fan_to_fan_system`, `add_hvac_plant_to_project`, and `add_water_heater_to_project`. Give each one a unique `description` — mechanical components are identified by it.

See [Mechanical operations](operations/mechanical.md).

::: comcheck_api.defaults.get_default_hvac_system_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_fan_system_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_fan_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_hvac_plant_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_water_heater_template
    options:
      heading_level: 3

## Credits

There is no credit template — build an `EfficiencyPackage` with the credit `type` directly and pass it to `add_energy_credit_to_project`.

See [Credits operations](operations/credits.md).

## Renewable Energy

Pass to `add_renewable_system_to_project` and `add_offsite_renewable_procurement_to_project`.

See [Renewable Energy operations](operations/renewable-energy.md).

::: comcheck_api.defaults.get_default_renewable_system_template
    options:
      heading_level: 3

::: comcheck_api.defaults.get_default_offsite_renewable_procurement_template
    options:
      heading_level: 3
