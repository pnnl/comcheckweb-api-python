# Scripts Directory

This directory contains various scripts for testing the COMcheck API client and its operations.

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
Integration tests for project operations, organized by domain.

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
Tests for all envelope operations including assemblies and nested components.

**What it tests:**

**Envelope Assembly Operations:**
- `add_roof_to_project()` / `update_roof_in_project()` - Roof operations
- `add_floor_to_project()` / `update_floor_in_project()` - Floor operations
- `add_ag_wall_to_project()` / `update_ag_wall_in_project()` - Above-grade wall operations
- `add_bg_wall_to_project()` / `update_bg_wall_in_project()` - Below-grade wall operations

**Nested Component Operations:**
- `add_skylight_to_project()` / `update_skylight_in_project()` - Skylight operations (on roofs)
- `add_window_to_project()` / `update_window_in_project()` - Window operations (on walls)
- `add_door_to_project()` / `update_door_in_project()` - Door operations (on walls)
- `add_thermal_bridge_to_project()` - Adding thermal bridges to walls

**Usage:**
```bash
python scripts/project_operations_tests/envelope_operations_script.py
```

**Output:**
Creates multiple JSON files in `testProjectJson/` directory showing project state after each operation:
- `initialProject.json`
- `roofAddedProject.json`, `roofUpdatedProject.json`
- `floorAddedProject.json`, `floorUpdatedProject.json`
- `agWallAddedProject.json`, `agWallUpdatedProject.json`
- `bgWallAddedProject.json`, `bgWallUpdatedProject.json`
- `skylightAddedProject.json`, `skylightUpdatedProject.json`
- `windowAddedProject.json`, `windowUpdatedProject.json`
- `doorAddedProject.json`, `doorUpdatedProject.json`
- `thermalBridgeAddedProject.json`

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

## Environment Setup

Before running any scripts, ensure you have:

1. **Python Environment**: Activate the virtual environment
   ```bash
   source .venv/bin/activate
   ```

2. **API Key**: Set your COMcheck API key in `.env` file
   ```
   COM_API_KEY=your_api_key_here
   ```

3. **Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

---

## Test Data

All test scripts that make API calls export their results to the `testProjectJson/` directory. This allows you to:
- Inspect the project state after each operation
- Compare before/after states
- Debug issues by examining the JSON structure
- Use as reference data for development

---

## Best Practices

1. **Run client tests first** (`comcheck_client_tests/`) to verify your API connection and credentials
2. **Use manager unit tests** (`manager_unit_tests/`) to verify component logic without API overhead
3. **Use project operations tests** (`project_operations_tests/`) for end-to-end integration testing:
   - Run `building_area_operations_script.py` to test building area operations
   - Run `envelope_operations_script.py` to test envelope operations
4. **Check test output** in `testProjectJson/` to debug issues
5. **Keep test data updated** by re-running tests after API changes

---

## Troubleshooting

### Common Issues

**"COM_API_KEY is not set"**
- Solution: Create a `.env` file with your API key or set the environment variable

**"No projects found"**
- Solution: Ensure you have at least one project in your COMcheck account

**Import errors**
- Solution: Verify you're running scripts from the project root or that `sys.path.insert()` is working correctly

**Module not found errors**
- Solution: Make sure the virtual environment is activated and dependencies are installed
