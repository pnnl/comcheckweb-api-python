# Tests Directory

Automated test suite for the COMcheck API Python client using pytest.

For ad-hoc manual testing during development, see the [tools/scripts/](../tools/scripts/) directory.

## Directory Structure

```
tests/
├── README.md
├── conftest.py                                      # Root fixtures and pytest config
├── test_base_model.py                               # CustomBaseModel unit tests
├── test_comcheck_client.py                          # COMcheckClient unit tests
├── client/
│   ├── test_user_functions.py                       # Integration: list/get/update projects
│   └── test_simulation.py                           # Integration: simulation workflow
├── data_manager_tests/
│   ├── test_data_manager.py                         # DataManager unit tests
│   └── envelope_tests/
│       ├── conftest.py                              # Envelope test fixtures
│       ├── test_envelope.py                         # Envelope manager tests
│       ├── test_roof_list_manager.py                # Roof list manager tests
│       ├── test_floor_list_manager.py               # Floor list manager tests
│       ├── test_bg_wall_list_manager.py             # Below-grade wall list manager tests
│       ├── test_window_list_manager.py              # Window list manager tests
│       └── test_door_list_manager.py                # Door list manager tests
└── project_operation_tests/
    ├── conftest.py                                  # Project operation fixtures
    ├── assertions/
    │   └── components.py                            # Shared assertion helpers
    ├── test_building_area_operations.py             # Integration: building area ops
    └── test_envelope_operations.py                  # Integration: envelope ops
```

## Prerequisites

- A `.env` file with your `COM_API_KEY` set, or the environment variable exported
- At least one project in your COMcheck account (for integration tests)

## Usage

Run all unit tests (no API key needed):

```bash
pytest tests/data_manager_tests/ tests/test_base_model.py
```

Run all tests including integration tests:

```bash
pytest --integration
```

Run a specific test file:

```bash
pytest tests/project_operation_tests/test_envelope_operations.py --integration
```

Run a specific test by name:

```bash
pytest -k "test_add_roof" --integration
```

Show print output during test runs:

```bash
pytest -s --integration
```

Stop on first failure:

```bash
pytest -x -s --integration
```

## Test Categories

### Unit Tests
- `test_base_model.py` - CustomBaseModel behavior
- `test_comcheck_client.py` - Client initialization and configuration
- `data_manager_tests/` - Data manager and envelope component managers

These run without an API key and do not make network calls.

### Integration Tests
- `client/` - Client user functions and simulation workflows
- `project_operation_tests/` - Building area and envelope CRUD operations

These require `COM_API_KEY` and make live API calls. Use the `--integration` flag to enable them.
