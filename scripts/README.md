# Scripts Directory

This directory contains various scripts for testing the COMcheck API client and its operations for developers.

## Directory Structure

```
scripts/
├── README.md                          # This file
├── main.py                            # Main entry point (legacy)
├── script_test_data.py               # Test data utilities
├── comcheck_client_tests/             # API client tests
│   ├── simulation_script.py           # Simulation API workflow tests
│   └── user_function_script.py        # User-facing function tests
├── project_operations_tests/          # Project operations integration tests
│   ├── building_area_operations_script.py   # Building area operations
│   └── envelope_operations_script.py        # Envelope operations
└── manager_unit_tests/                # Manager unit tests
    ├── building_area/                 # Building area manager tests
    │   └── building_area_script.py
    └── envelope/                      # Envelope component manager tests
        ├── ag_wall_script.py
        ├── bg_wall_script.py
        ├── door_script.py
        ├── floor_script.py
        ├── roof_script.py
        └── window_script.py
```

## Test Categories

### 1. COMcheck Client Tests (`comcheck_client_tests/`)
Tests for COMcheck API client operations.

#### Simulation Tests (`comcheck_client_tests/simulation_script.py`)
Tests the simulation workflow for running compliance checks.

**What it tests:**
- `start_run_simulation()` - Starting a simulation
- `get_simulation_status()` - Checking simulation status
- `get_simulation_result()` - Retrieving simulation results

**Usage:**
```bash
python scripts/comcheck_client_tests/simulation_script.py
```

#### User Function Tests (`comcheck_client_tests/user_function_script.py`)
Tests user-facing API client functions.

**What it tests:**
- `list_projects()` - Retrieving project lists
- `get_project()` - Getting individual projects
- Other user-facing client methods

**Usage:**
```bash
python scripts/comcheck_client_tests/user_function_script.py
```

---

### 2. Project Operations Tests (`project_operations_tests/`)
Integration tests for project operations.

#### Building Area Operations (`project_operations_tests/building_area_operations_script.py`)
Tests for building area operations.

**What it tests:**
- `add_building_area_to_project()` - Adding new building areas
- `update_building_area_in_project()` - Updating existing building areas

**Usage:**
```bash
python scripts/project_operations_tests/building_area_operations_script.py
```

**Output:**
- `testProjectJson/initialProject.json`
- `testProjectJson/buildingAreaAddedProject.json`
- `testProjectJson/buildingAreaUpdatedProject.json`

#### Envelope Operations (`project_operations_tests/envelope_operations_script.py`)
Comprehensive integration tests for all envelope operations including assemblies and nested components. This script tests the complete workflow of adding and updating envelope components in a COMcheck project.

**Test Coverage:**

**Envelope Assembly Operations (Tests 1-8):**
1. `add_roof_to_project()` - Add roof assemblies
2. `update_roof_in_project()` - Update existing roofs
3. `add_floor_to_project()` - Add floor assemblies  
4. `update_floor_in_project()` - Update existing floors
5. `add_ag_wall_to_project()` - Add above-grade wall assemblies
6. `update_ag_wall_in_project()` - Update existing above-grade walls
7. `add_bg_wall_to_project()` - Add below-grade wall assemblies
8. `update_bg_wall_in_project()` - Update existing below-grade walls

**Nested Component Operations (Tests 9-15):**
9. `add_skylight_to_project()` - Add nested skylights to roofs
10. `update_skylight_in_project()` - Update nested skylights in roofs
11. `add_skylight_to_project()` - Add orphaned skylights (ALTERATION projects)
12. `update_skylight_in_project()` - Update orphaned skylights (converts project to ALTERATION)
13. `add_window_to_project()` - Add nested windows to walls
14. `update_window_in_project()` - Update nested windows in walls
15. `add_thermal_bridge_to_project()` - Add thermal bridges to above-grade walls

**Key Features:**

- **Location-Aware Updates**: Update operations automatically detect whether components are orphaned (ALTERATION projects) or nested in parent assemblies
- **Orphaned vs Nested Components**: 
  - Orphaned: Components stored directly in `envelope.component[]` (ALTERATION projects only)
  - Nested: Components stored in parent assemblies (e.g., `roof.skylight[]`, `agWall.window[]`)
- **Failed Test Tracking**: Displays summary of any failed tests at the end
- **Selective Test Execution**: Run individual tests or all tests at once

**Usage:**
```bash
# Run all tests (1-15)
python scripts/project_operations_tests/envelope_operations_script.py

# Run a specific test by number
python scripts/project_operations_tests/envelope_operations_script.py 5   # Run test #5 (Adding agWall)
python scripts/project_operations_tests/envelope_operations_script.py 14  # Run test #14 (Updating nested window)
```

**Example Output:**
```
================================================================================
Envelope Operations Integration Tests
================================================================================

✓ Using project ID: 507f1f77bcf86cd799439011
  Exported initial state to: testProjectJson/initialProject.json

Running single test: #14

14. Updating nested window...
  Found nested window in agWall: METAL_BUILDING_WALL
   ✓ Nested window updated

================================================================================
Envelope Tests Complete

✓ All tests passed!
================================================================================
```

**Output Files:**
Creates JSON snapshots in `testProjectJson/` directory showing project state after each operation:

**Assembly Operations:**
- `initialProject.json` - Starting project state
- `roofAddedProject.json`, `roofUpdatedProject.json`
- `floorAddedProject.json`, `floorUpdatedProject.json`
- `agWallAddedProject.json`, `agWallUpdatedProject.json`
- `bgWallAddedProject.json`, `bgWallUpdatedProject.json`

**Nested Component Operations:**
- `nestedSkylightAddedProject.json`, `nestedSkylightUpdatedProject.json`
- `orphanedSkylightAddedProject.json`, `orphanedSkylightUpdatedProject.json`
- `windowAddedProject.json`, `windowUpdatedProject.json`
- `thermalBridgeAddedProject.json`

**Important Notes:**

- **Test Order Matters**: Tests build on each other. Running test #14 requires components added in previous tests (e.g., walls and windows must exist)
- **ALTERATION Projects**: Tests 11-12 demonstrate orphaned component handling by temporarily converting the project to ALTERATION type
- **Location Detection**: Update operations use the `_find_component_location()` helper to automatically locate components whether they're orphaned or nested

---

### 3. Manager Unit Tests (`manager_unit_tests/`)
Unit tests for Manager classes that handle list operations on components.

**Purpose:**
These scripts test the Manager classes directly without making API calls. They verify the core logic for adding, modifying, and removing components from lists.

#### Building Area Manager Tests:
- `manager_unit_tests/building_area/building_area_script.py`
  - Tests: `BuildingAreaListManager`

#### Envelope Manager Tests:
- `manager_unit_tests/envelope/ag_wall_script.py` - Tests: `AgWallListManager`
- `manager_unit_tests/envelope/bg_wall_script.py` - Tests: `BgWallListManager`
- `manager_unit_tests/envelope/door_script.py` - Tests: `DoorListManager`
- `manager_unit_tests/envelope/floor_script.py` - Tests: `FloorListManager`
- `manager_unit_tests/envelope/roof_script.py` - Tests: `RoofListManager`
- `manager_unit_tests/envelope/window_script.py` - Tests: `WindowListManager`

**Usage:**
```bash
# Run individual manager tests
python scripts/manager_unit_tests/building_area/building_area_script.py
python scripts/manager_unit_tests/envelope/roof_script.py
# etc.
```

---

## Test Output

All test scripts that make API calls export their results to the `testProjectJson/` directory. This allows you to:
- Inspect the project state after each operation
- Compare before/after states
- Debug issues by examining the JSON structure
- Use as reference data for development

---

## Best Practices

1. **Run client tests first** (`comcheck_client_tests/`) to verify your API connection and credentials
2. **Use project operations tests** (`project_operations_tests/`) for end-to-end integration testing:
   - Run `building_area_operations_script.py` to test building area operations
   - Run `envelope_operations_script.py` to test envelope operations
3. **Check test output** in `testProjectJson/` to debug issues
4. **Keep test data updated** by re-running tests after API changes

---

## Troubleshooting

### Common Issues

**"COM_API_KEY is not set"**
- Solution: Create a `.env` file with your API key or set the environment variable

**"No projects found"**
- Solution: Ensure you have at least one project in your COMcheck account
