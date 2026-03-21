# Code Improvements & Action Plan

This document outlines recommended improvements before publishing this library to GitHub/PyPI.

## Project Status

**🔓 Open Source** - Publicly available on GitHub
**🔒 Internal Development** - External contributions not accepted

This library will be:
- ✅ Publicly available on GitHub (anyone can view and use it)
- ✅ Issue reports welcome from users
- ❌ External contributions/pull requests not accepted
- ❌ Development is internal only

## Table of Contents
- [Critical Issues](#critical-issues)
- [Code Quality Improvements](#code-quality-improvements)
- [Documentation Needs](#documentation-needs)
- [Version Control Strategy](#version-control-strategy)
- [Publishing Checklist](#publishing-checklist)

---

## Critical Issues

### 1. Security - API Key Exposure
**Priority:** 🔴 CRITICAL

**Issue:** `.env` file containing API key is committed to git repository.

**Impact:** API credentials exposed in version control history.

**Fix:**
```bash
# Remove from git
git rm --cached .env

# Ensure it's in .gitignore (already present)
git commit -m "Remove sensitive .env file from version control"
```

**Action:** Create `.env.example` template file without real credentials.

### 2. Hardcoded API URL
**Priority:** 🟡 MEDIUM

**Location:** `comcheck_api/api/api_services.py:21`

```python
BASE_URL: str = "https://becp-dev.pnl.gov/ahj/COM"
```

**Issue:** URL is hardcoded, making it difficult to switch environments (dev/staging/prod).

**Fix:**
```python
def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
    if not api_key:
        raise ValueError("API key is required")
    self.api_key = api_key
    self.base_url = base_url or os.getenv(
        "COMCHECK_API_URL",
        "https://becp-dev.pnl.gov/ahj/COM"
    )
    self._client: Optional[httpx.Client] = None
```

### 3. Incomplete LICENSE
**Priority:** 🟡 MEDIUM

**Issue:** LICENSE file has placeholders `[year] [fullname]`.

**Fix:** Update with actual copyright information:
```
Copyright (c) 2025 [Your Organization Name]
```

---

## Code Quality Improvements

### 1. Replace print() with logging

**Issue:** Using `print()` statements in production code.

**Locations:**
- `comcheck_api/client/comcheck_client.py:233`
- `comcheck_api/api/api_services.py:73-81`

**Fix:**
```python
import logging

logger = logging.getLogger(__name__)

# Replace print() calls
logger.info("Updating project: %s", project_id)
logger.error("HTTP error occurred: %s", error, exc_info=True)
```

### 2. Inconsistent Type Annotations

**Issue:** Mixed union syntax in type hints.

**Location:** `comcheck_client.py:102`
```python
# Current (inconsistent)
def update_project(...) -> ComBuilding | dict[str, Any] | None:

# Should be (consistent with Python 3.12+)
def update_project(...) -> ComBuilding | dict[str, Any] | None:
```

**Recommendation:** Use `|` syntax consistently throughout (Python 3.12+ standard).

### 3. Import Path Issues

**Location:** `comcheck_api/__init__.py:4`

**Issue:** Documentation references incorrect package name:
```python
# Current
from comcheckweb.client import COMcheckClient

# Should be
from comcheck_api.client import COMcheckClient
```

**Fix:** Update all import examples in docstrings.

### 4. Unresolved TODO Comments

**Location:** `comcheck_client.py:148`

```python
# TODO: need to verify if other components also need to remove None IDs
```

**Action:** Either implement or document why it's deferred with issue tracking.

### 5. Better Error Handling

**Current:** Errors are caught, logged with print(), then re-raised without context.

**Improvement:** Create custom exceptions and add context:

```python
# comcheck_api/exceptions.py
class COMCheckAPIError(Exception):
    """Base exception for COMcheck API errors."""
    pass

class COMCheckHTTPError(COMCheckAPIError):
    """HTTP request failed."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")

class COMCheckValidationError(COMCheckAPIError):
    """Validation failed."""
    pass
```

Usage:
```python
except httpx.HTTPStatusError as error:
    logger.error("HTTP error: %s", error, exc_info=True)
    raise COMCheckHTTPError(
        error.response.status_code,
        error.response.text
    ) from error
```

---

## Documentation Needs

### Missing Files

#### 1. CHANGELOG.md
**Purpose:** Track version history and changes.

**Format:** Keep a Changelog standard (https://keepachangelog.com/)

#### 2. API Documentation
**Needed:**
- `docs/api-reference.md` - Complete API documentation
- `docs/quickstart.md` - Getting started guide
- `docs/types-reference.md` - Type system documentation

#### 3. .env.example
**Purpose:** Template for environment variables without secrets.

```bash
# .env.example
COM_API_KEY=your-api-key-here
COMCHECK_API_URL=https://becp-dev.pnl.gov/ahj/COM
```

### Documentation Improvements

#### Update README.md
Current README is basic. Needs:
- Clear installation instructions
- Quick start code examples
- Feature highlights
- Links to full documentation
- Badges (license, Python version, build status)
- Usage examples
- Configuration options

#### Add Docstrings
Many functions lack comprehensive docstrings. Need:
- Parameter descriptions
- Return value documentation
- Exception documentation
- Usage examples

**Example:**
```python
def start_run_simulation(
    self,
    project: ComBuilding,
    project_id: Optional[int] = None
) -> str:
    """Start a simulation run for a given project.

    This method performs compliance validation before starting the simulation.
    If the project fails any compliance checks, a ValueError is raised with
    all validation error messages.

    Args:
        project: The project data to run the simulation on. Must be a valid
                ComBuilding instance with all required fields populated.
        project_id: Optional project ID. If provided, the project will be
                   updated in the database before simulation starts. If None,
                   the simulation runs without saving to database.

    Returns:
        str: The simulation session ID that can be used to query status
             and results using get_simulation_status() and
             get_simulation_result().

    Raises:
        ValueError: If the project fails compliance validation. The error
                   message contains all validation issues that need to be
                   resolved before simulation can proceed.
        RuntimeError: If the API fails to start the simulation or returns
                     no session data.

    Example:
        >>> from comcheck_api import COMcheckClient
        >>> client = COMcheckClient(api_key="your-key")
        >>> project = client.get_project("123")
        >>> session_id = client.start_run_simulation(project)
        >>> print(f"Simulation started: {session_id}")
    """
```

---

## Version Control Strategy

### Semantic Versioning

Follow SemVer (https://semver.org/):

```
MAJOR.MINOR.PATCH

- MAJOR: Breaking changes (e.g., 1.0.0 → 2.0.0)
- MINOR: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
- PATCH: Bug fixes, backward compatible (e.g., 1.0.0 → 1.0.1)
```

**Current:** `0.1.0` (pre-release/alpha)

**Recommended Progression:**
- `0.1.0` - Initial alpha release
- `0.2.0` - Beta with additional features
- `0.9.0` - Release candidate
- `1.0.0` - First stable release

### Git Tagging

```bash
# Create annotated tags for releases
git tag -a v0.1.0 -m "Initial alpha release"
git push origin v0.1.0

# List all tags
git tag -l
```

### Branch Strategy

**Recommended:**
- `main` - Stable releases only
- `develop` - Integration branch
- `feature/*` - Feature branches
- `release/*` - Release preparation

**Current:** Using feature branches merged to `main`.

### Release Workflow

```bash
# 1. Create release branch
git checkout -b release/0.1.0 develop

# 2. Update version in pyproject.toml
# 3. Update CHANGELOG.md
# 4. Commit changes
git commit -m "Prepare release v0.1.0"

# 5. Merge to main
git checkout main
git merge release/0.1.0

# 6. Tag the release
git tag -a v0.1.0 -m "Release version 0.1.0"

# 7. Push
git push origin main --tags

# 8. Build and publish
uv build
uv publish
```

---

## Publishing Checklist

### Pre-Release Tasks

- [ ] **Security**
  - [ ] Remove `.env` from git history
  - [ ] Create `.env.example`
  - [ ] Audit code for other secrets
  - [ ] Review dependencies for vulnerabilities

- [ ] **Code Quality**
  - [ ] Replace all `print()` with `logging`
  - [ ] Make `BASE_URL` configurable
  - [ ] Fix import paths in `__init__.py`
  - [ ] Resolve all TODO comments
  - [ ] Add custom exception classes
  - [ ] Consistent type annotation style

- [ ] **Documentation**
  - [ ] Complete `CHANGELOG.md`
  - [ ] Update `README.md` with full guide
  - [ ] Add missing docstrings
  - [ ] Create API reference documentation
  - [ ] Update LICENSE with real info

- [ ] **Testing**
  - [ ] Run all tests: `uv run pytest`
  - [ ] Type check: `uv run mypy comcheck_api`
  - [ ] Format check: `uv run black --check comcheck_api`
  - [ ] Verify examples work
  - [ ] Test package installation

- [ ] **Metadata**
  - [ ] Update `pyproject.toml` with proper metadata
  - [ ] Add project URLs (homepage, issues, docs)
  - [ ] Add keywords and classifiers
  - [ ] Add author information
  - [ ] Verify license field

- [ ] **Version Control**
  - [ ] Create version tag
  - [ ] Push to remote
  - [ ] Create GitHub release
  - [ ] Attach release notes

- [ ] **Package Building**
  - [ ] Build: `uv build`
  - [ ] Verify package contents
  - [ ] Test install from wheel
  - [ ] Check package metadata

### Publishing to PyPI

- [ ] **Test PyPI First**
  ```bash
  uv publish --repository testpypi
  pip install --index-url https://test.pypi.org/simple/ comcheck-api
  ```

- [ ] **Production PyPI**
  ```bash
  uv publish
  pip install comcheck-api
  ```

### Post-Release Tasks

- [ ] Verify installation from PyPI
- [ ] Update documentation links
- [ ] Announce release
- [ ] Monitor for issues
- [ ] Create next milestone

---

## Priority Matrix

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 🔴 P0 | Remove `.env` from git | 5 min | High |
| 🔴 P0 | Fix LICENSE | 2 min | High |
| 🔴 P0 | Fix import paths | 10 min | High |
| 🟡 P1 | Replace print() with logging | 30 min | Medium |
| 🟡 P1 | Make BASE_URL configurable | 15 min | Medium |
| 🟡 P1 | Create CHANGELOG.md | 20 min | Medium |
| 🟡 P1 | Update README.md | 45 min | High |
| 🟢 P2 | Add custom exceptions | 60 min | Medium |
| 🟢 P2 | API documentation | 2-4 hrs | High |
| 🟢 P2 | Add comprehensive docstrings | 2-3 hrs | Medium |
| 🟢 P3 | Resolve TODO comments | 1 hr | Low |

---

## Next Steps

1. **Immediate (This session)**
   - Switch to main branch ✅
   - Create docs directory ✅
   - Create documentation files (this file) ✅

2. **Critical Fixes (Before any release)**
   - Remove `.env` from git
   - Fix LICENSE
   - Fix import paths
   - Create `.env.example`

3. **Essential Documentation (Before v0.1.0)**
   - CHANGELOG.md
   - Enhanced README.md

4. **Code Improvements (Before v1.0.0)**
   - Logging implementation
   - Custom exceptions
   - Comprehensive docstrings
   - API documentation

5. **Release Preparation**
   - Version tagging
   - Package building
   - PyPI publishing

---

*Document created: March 20, 2026*
*Last updated: March 20, 2026*
