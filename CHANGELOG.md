# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Made BASE_URL configurable via COMCHECK_API_URL environment variable

### To Be Added
- Logging implementation to replace print statements
- Custom exception classes for better error handling
- Comprehensive API documentation
- Additional examples and tutorials

### To Be Fixed
- Fix import path documentation in __init__.py
- Security: Remove .env from version control

## [0.1.0] - 2025-03-XX

### Added
- Initial release of COMcheck Web API Python client
- Core API service layer with httpx HTTP client
- High-level client interface (COMcheckClient)
- Project CRUD operations (get, list, update)
- Building component management:
  - Envelope operations (walls, roofs, windows, doors, skylights)
  - Building area operations
  - Lighting, HVAC, and control systems
- Energy simulation support:
  - Start simulation
  - Check simulation status
  - Retrieve simulation results
- Compliance checking before simulation
- Type-safe Pydantic models for all data structures
- Context manager support for automatic resource cleanup
- Project template and default constants
- Data managers for building areas and envelope components
- Utility functions for project operations
- Comprehensive examples:
  - Client operations (simulation, user functions)
  - Data manager usage
  - Project operations
- Development tooling:
  - Black code formatter
  - MyPy type checking
  - Pre-commit hooks
  - pytest test framework
- Schema generation from COMcheck API
- Package management with uv

### Dependencies
- httpx >= 0.27.0 (HTTP client)
- pydantic >= 2.12.5 (data validation)
- jsonschema >= 4.23.0 (schema validation)
- python-dotenv >= 1.0.0 (environment configuration)
- types-jsonschema >= 4.23.0 (type stubs)

### Development Dependencies
- black >= 26.1.0 (code formatting)
- datamodel-code-generator >= 0.54.1 (type generation)
- mypy >= 1.19.1 (type checking)
- pre-commit >= 4.5.1 (git hooks)
- pytest >= 9.0.2 (testing)

### Requirements
- Python >= 3.12

### Known Issues
- API key must be provided manually (no OAuth flow yet)
- Some print() statements used instead of proper logging
- Limited error handling with custom exceptions

### Breaking Changes
None (initial release)

---

## Release Notes

### Version 0.1.0 - Initial Alpha Release

This is the first alpha release of the COMcheck Web API Python client. The library provides a clean, type-safe interface for interacting with the COMcheck Web API to perform building energy code compliance checks.

**Key Features:**
- Easy-to-use client interface
- Full project lifecycle management
- Building component operations
- Energy simulation and compliance checking
- Type-safe with Pydantic models
- Well-documented with examples

**Not Yet Stable:**
This is an alpha release. The API may change in future versions. Not recommended for production use without thorough testing.

**What's Next:**
- API stabilization for v1.0.0
- Enhanced documentation
- More examples and tutorials
- Performance optimizations
- Better error handling

---

## Migration Guides

### Upgrading to 0.1.0
Initial release - no migration needed.

---

## Deprecation Notices

None yet.

---

*For detailed technical improvements and roadmap, see [docs/IMPROVEMENTS.md](docs/IMPROVEMENTS.md)*
*For version control strategy, see [docs/VERSION_CONTROL.md](docs/VERSION_CONTROL.md)*
