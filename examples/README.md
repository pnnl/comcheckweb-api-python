# Examples Directory

This directory contains various example scripts demonstrating the usage of the COMcheck API client and its operations for developers.

## Directory Structure

```
examples/
├── README.md                          # This file
├── client/                           # API client examples
│   ├── simulation.py                 # Simulation API workflow examples
│   ├── assemblies.py                 # Assembly u-value calculation examples
│   ├── compliance_and_report.py      # Compliance, requirements & report examples
│   ├── allowed_wattage.py            # Interior lighting allowed-wattage calculation examples
│   ├── renewable.py                  # Renewable area & capacity calculation examples
│   ├── credits.py                    # Energy credit operations & calculation examples
│   ├── mechanical.py                 # Mechanical efficiency & compliance calculation examples
│   └── user_functions.py             # User-facing function examples
└── project_operations/               # Project operations examples
    ├── building_area_operations.py       # Building area operations
    ├── envelope_operations.py            # Envelope operations
    ├── interior_lighting_operations.py   # Interior lighting (InteriorSpace) operations
    ├── exterior_lighting_operations.py   # Exterior lighting (ExteriorArea) operations
    └── renewable_operations.py           # Renewable systems & off-site procurement operations
```

## Example Categories

### 1. COMcheck Client Examples (`client/`)
Examples demonstrating COMcheck API client operations.

#### Simulation Examples (`client/simulation.py`)
Demonstrates the simulation workflow for running compliance checks.

**What it demonstrates:**
- `start_run_simulation()` - Starting a simulation
- `get_simulation_status()` - Checking simulation status
- `get_simulation_result()` - Retrieving simulation results

**Usage:**
```bash
python examples/client/simulation.py
```

#### Compliance & Report Examples (`client/compliance_and_report.py`)
Demonstrates compliance checks, requirements lookup, and PDF report generation.

**What it demonstrates:**
- `check_UA_compliance()` - Checking code compliance for a project
- `check_requirements()` - Retrieving applicable requirements
- `generate_report()` - Generating a PDF report (presigned S3 URL, optional download)
- `generate_report(use_backstop_compliance=True)` - Generating a report using backstop compliance

**Usage:**
```bash
python examples/client/compliance_and_report.py
```

#### Allowed Wattage Examples (`client/allowed_wattage.py`)
Demonstrates interior lighting allowed-wattage calculation.

**What it demonstrates:**
- `calculate_interior_space_allowed_wattage()` - Calculating allowed wattage for a single InteriorSpace
- `calculate_interior_spaces_allowed_wattage()` - Calculating allowed wattage for a list of InteriorSpace objects

**Usage:**
```bash
python examples/client/allowed_wattage.py
```

#### Renewable Examples (`client/renewable.py`)
Demonstrates server-side renewable calculations.

**What it demonstrates:**
- `area_for_renewable()` - Calculating `largestThreeFloorArea` and `roofAreaForRenewable` and writing them onto `project.renewable`
- `renewable_capacity()` - Calculating required vs. proposed renewable capacity and off-site energy and writing them onto `project.renewable`

**Usage:**
```bash
python examples/client/renewable.py
```

#### Credits Examples (`client/credits.py`)
Demonstrates energy credit operations and the server-side credit calculation.

**What it demonstrates:**
- `add_energy_credit_to_project()` / `update_energy_credit_in_project()` - Adding energy credits to a building area and updating their inputs
- `calculate_energy_credits()` - Calculating proposed vs. required credits per building area (the project is not modified)

**Usage:**
```bash
python examples/client/credits.py
```

#### Mechanical Examples (`client/mechanical.py`)
Demonstrates mechanical system efficiency and compliance calculations.

**What it demonstrates:**
- `calculate_water_heater_efficiency()` - Calculating efficiency requirements for water heater systems
- `calculate_hvac_system_efficiency()` - Calculating efficiency requirements for HVAC systems
- `validate_hvac_system_economizer()` - Validating economizer requirements for an HVAC system
- `calculate_plant_efficiency()` - Calculating efficiency requirements for HVAC plants
- `calculate_fan_pressure_drop_credit()` - Calculating pressure drop credit for a fan system
- `check_fan_system_compliance()` - Checking fan system compliance
- `calculate_fan_maximum_allowable_hp()` - Calculating maximum allowable horsepower for a fan
- `update_fan_system_compliance()` - Updating fan system compliance fields in a project
- `update_fan_pressure_drop_credits()` - Updating pressure drop credit values in a project

**Usage:**
```bash
python examples/client/mechanical.py
```

#### User Function Examples (`client/user_functions.py`)
Demonstrates user-facing API client functions.

**What it demonstrates:**
- `list_projects()` - Retrieving project lists
- `get_project()` - Getting individual projects
- Other user-facing client methods

**Usage:**
```bash
python examples/client/user_functions.py
```

---

### 2. Project Operations Examples (`project_operations/`)
Examples demonstrating project operations.

#### Building Area Operations (`project_operations/building_area_operations.py`)
Examples for building area operations.

**What it demonstrates:**
- `add_building_area_to_project()` - Adding new building areas
- `update_building_area_in_project()` - Updating existing building areas

**Usage:**
```bash
python examples/project_operations/building_area_operations.py
```

**Output:**
- `testProjectJson/initialProject.json`
- `testProjectJson/buildingAreaAddedProject.json`
- `testProjectJson/buildingAreaUpdatedProject.json`

#### Interior Lighting Operations (`project_operations/interior_lighting_operations.py`)
Demonstrates adding and managing interior lighting (InteriorSpace) in a project.

**What it demonstrates:**
- `add_interior_space_to_project()` - Adding an InteriorSpace with fixtures pre-populated
- `update_interior_space_in_project()` - Updating InteriorSpace fields
- `update_fixtures_in_interior_space()` - Batch adding/updating/removing fixtures, matched by fixtureType
- `remove_interior_space_from_project()` - Removing an InteriorSpace and its fixtures
- `get_interior_space_keys_from_project()` - Listing interior spaces in a building area

**Usage:**
```bash
python examples/project_operations/interior_lighting_operations.py
```

#### Exterior Lighting Operations (`project_operations/exterior_lighting_operations.py`)
Demonstrates setting the exterior lighting zone type and managing ExteriorArea items with fixtures.

**What it demonstrates:**
- `set_exterior_lighting_zone_type_in_project()` - Setting the project-level zone type
- `add_exterior_area_to_project()` - Adding an ExteriorArea with fixtures pre-populated
- `update_exterior_area_in_project()` - Updating ExteriorArea fields
- `update_fixtures_in_exterior_area()` - Batch adding/updating/removing fixtures, matched by fixtureType
- `remove_exterior_area_from_project()` - Removing an ExteriorArea and its fixtures

**Usage:**
```bash
python examples/project_operations/exterior_lighting_operations.py
```

#### Envelope Operations (`project_operations/envelope_operations.py`)
Comprehensive examples for all envelope operations including assemblies and nested components. This script demonstrates the complete workflow of adding and updating envelope components in a COMcheck project.

**Key Features:**

- **Location-Aware Updates**: Update operations automatically detect whether components are orphaned (ALTERATION projects) or nested in parent assemblies
- **Orphaned vs Nested Components**: 
  - Orphaned: Components stored directly in `envelope.component[]` (ALTERATION projects only)
  - Nested: Components stored in parent assemblies (e.g., `roof.skylight[]`, `agWall.window[]`)

**Usage:**
```bash
python examples/project_operations/envelope_operations.py
```

**Output Files:**
Creates JSON snapshots in `testProjectJson/` directory showing project state after each operation.

---

## Best Practices

1. **Start with client examples** (`client/`) to understand basic API operations
2. **Use project operations examples** (`project_operations/`) for end-to-end workflows
3. **Check example output** in `testProjectJson/` to understand the results

---

## Troubleshooting

### Common Issues

**"COM_API_KEY is not set"**
- Solution: Create a `.env` file with your API key or set the environment variable

**"No projects found"**
- Solution: Ensure you have at least one project in your COMcheck account
