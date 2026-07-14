# Examples Directory

This directory contains various example scripts demonstrating the usage of the COMcheck API client and its operations for developers.

## Directory Structure

```
examples/
├── README.md                          # This file
├── client/                           # API client examples
│   ├── simulation.py                 # Simulation API workflow examples
│   ├── compliance_and_report.py      # Compliance, requirements & report examples
│   └── user_functions.py             # User-facing function examples
└── project_operations/               # Project operations examples
    ├── building_area_operations.py  # Building area operations
    └── envelope_operations.py       # Envelope operations
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

**Usage:**
```bash
python examples/client/compliance_and_report.py
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
