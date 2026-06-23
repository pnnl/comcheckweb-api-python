# Scripts Directory

Manual testing scripts for ad-hoc development and debugging of the COMcheck API client. Use these for quick, interactive testing when adding new features or investigating API behavior.

For automated tests with assertions, see the [tests/](../../tests/) directory.

## Directory Structure

```
tools/scripts/
├── README.md
├── main.py                                          # Script runner (runs all *_script.py files)
├── script_test_data.py                              # Shared test data (envelope, building area)
├── comcheck_client_tests/
│   ├── user_function_script.py                      # Test client user functions
│   └── simulation_script.py                         # Test simulation workflow
└── project_operations_tests/
    ├── building_area_operations_script.py            # Test building area operations
    └── envelope_operations_script.py                 # Test envelope operations
```

## Prerequisites

- A `.env` file with your `COM_API_KEY` set, or the environment variable exported
- At least one project in your COMcheck account

## Usage

Run all scripts:

```bash
python tools/scripts/main.py
```

Run a single script:

```bash
python tools/scripts/comcheck_client_tests/user_function_script.py
python tools/scripts/comcheck_client_tests/simulation_script.py
python tools/scripts/project_operations_tests/building_area_operations_script.py
python tools/scripts/project_operations_tests/envelope_operations_script.py
```

Some scripts support running individual tests by number:

```bash
python tools/scripts/project_operations_tests/envelope_operations_script.py 3
```

## Output

Scripts export JSON results to a `testProjectJson/` directory for manual inspection of API responses.

## Scripts vs Tests

| | `tools/scripts/` | `tests/` |
|---|---|---|
| **Purpose** | Ad-hoc manual testing during development | Automated tests with assertions |
| **When to use** | Exploring API behavior, debugging, adding new features | Validating correctness, CI, regression testing |
| **Output** | Prints and JSON files for manual inspection | Pass/fail via pytest |
| **Runner** | `python tools/scripts/main.py` or run individually | `pytest` |
