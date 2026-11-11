# COMcheckClient

The primary interface for interacting with the COMcheck Web API.

Use the client to load and save projects and to call COMcheck calculations.
To build or edit a project locally, use the
[project operations](operations/building-area.md) modules, then save the
result with `update_project`.

Methods that end with "update the project in place" write the calculated
values back onto the `project` you pass in and return that same instance.

Exterior lighting has no client calculation methods — use
[`project_exterior_lighting_operations`](operations/exterior-lighting.md).

::: comcheck_api.client.comcheck_client.COMcheckClient
    options:
      members: false
      show_root_heading: false

## Projects

::: comcheck_api.client.comcheck_client.COMcheckClient.set_api_key
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.get_project
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.list_projects
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.update_project
    options:
      heading_level: 3

## Envelope

See also: [Envelope operations](operations/envelope.md).

::: comcheck_api.client.comcheck_client.COMcheckClient.update_uvalues
    options:
      heading_level: 3

## Interior Lighting

See also: [Interior Lighting operations](operations/interior-lighting.md).

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_interior_space_allowed_wattage
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_interior_spaces_allowed_wattage
    options:
      heading_level: 3

## Mechanical

See also: [Mechanical operations](operations/mechanical.md).

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_hvac_system_efficiency
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.validate_hvac_system_economizer
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_fan_pressure_drop_credit
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.check_fan_system_compliance
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_fan_maximum_allowable_hp
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.update_fan_system_compliance
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.update_fan_pressure_drop_credits
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.update_fan_maximum_allowable_hp
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_plant_efficiency
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_water_heater_efficiency
    options:
      heading_level: 3

## Credits

See also: [Credits operations](operations/credits.md).

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_energy_credits
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.calculate_single_energy_credit
    options:
      heading_level: 3

## Renewable Energy

See also: [Renewable Energy operations](operations/renewable-energy.md).

::: comcheck_api.client.comcheck_client.COMcheckClient.area_for_renewable
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.renewable_capacity
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.set_renewable_exception
    options:
      heading_level: 3

## Simulation

See also: [Simulation](simulation.md).

::: comcheck_api.client.comcheck_client.COMcheckClient.start_run_simulation
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.get_simulation_status
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.get_simulation_result
    options:
      heading_level: 3

## Compliance & Reports

See also: [Compliance & Reports](compliance.md).

::: comcheck_api.client.comcheck_client.COMcheckClient.check_UA_compliance
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.check_requirements
    options:
      heading_level: 3

::: comcheck_api.client.comcheck_client.COMcheckClient.generate_report
    options:
      heading_level: 3
