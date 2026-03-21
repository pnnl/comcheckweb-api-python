# Version Control Strategy

This document outlines the version control and release management strategy for the COMcheck API Python client library.

## Table of Contents
- [Semantic Versioning](#semantic-versioning)
- [Branch Strategy](#branch-strategy)
- [Git Workflow](#git-workflow)
- [Release Process](#release-process)
- [Version Numbering](#version-numbering)

---

## Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/).

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

**Components:**
- `MAJOR`: Incompatible API changes
- `MINOR`: Add functionality (backward-compatible)
- `PATCH`: Bug fixes (backward-compatible)
- `PRERELEASE`: Optional (alpha, beta, rc)
- `BUILD`: Optional build metadata

### Version Increments

#### MAJOR (X.0.0)
Increment when making incompatible API changes:
- Removing public methods/functions
- Changing method signatures
- Removing or renaming parameters
- Changing return types in breaking ways
- Major architectural changes

**Example:** `1.5.3` → `2.0.0`

#### MINOR (0.X.0)
Increment when adding functionality in a backward-compatible manner:
- Adding new public methods/functions
- Adding optional parameters with defaults
- Adding new features
- Deprecating functionality (without removing)

**Example:** `1.5.3` → `1.6.0`

#### PATCH (0.0.X)
Increment when making backward-compatible bug fixes:
- Fixing bugs
- Performance improvements
- Documentation updates
- Internal refactoring

**Example:** `1.5.3` → `1.5.4`

### Pre-release Versions

Use suffixes for pre-release versions:

- `0.1.0-alpha` - Early preview, unstable
- `0.1.0-beta` - Feature complete, testing phase
- `0.1.0-rc.1` - Release candidate, near final
- `1.0.0` - Stable release

### Version 0.x.y (Initial Development)

During initial development (major version 0):
- API may change without notice
- `0.y.0` indicates breaking changes
- `0.0.z` for fixes and additions
- No stability guarantees until `1.0.0`

**Current Phase:** `0.1.0` (initial alpha)

---

## Branch Strategy

### Main Branches

#### `main`
- **Purpose:** Production-ready code
- **Protection:** Protected, requires PR reviews
- **Contains:** Released versions only
- **Tags:** All release tags (`v1.0.0`, `v1.1.0`, etc.)

#### `develop` (optional for larger teams)
- **Purpose:** Integration branch for features
- **Protection:** Requires CI to pass
- **Contains:** Next release preparation
- **Merges from:** Feature branches
- **Merges to:** `main` via release branches

### Supporting Branches

#### Feature Branches (`feature/*`)
- **Naming:** `feature/TICKET-description`
- **Example:** `feature/CCSTRAT-1316-simulation-updates`
- **Branch from:** `main` (or `develop`)
- **Merge to:** `main` (or `develop`)
- **Lifetime:** Until feature is merged
- **Delete:** After successful merge

#### Release Branches (`release/*`)
- **Naming:** `release/X.Y.Z`
- **Example:** `release/1.0.0`
- **Branch from:** `develop` or `main`
- **Merge to:** `main` and back to `develop`
- **Purpose:** Prepare release, version bump, final testing
- **Delete:** After release is tagged

#### Hotfix Branches (`hotfix/*`)
- **Naming:** `hotfix/X.Y.Z-description`
- **Example:** `hotfix/1.0.1-api-timeout`
- **Branch from:** `main`
- **Merge to:** `main` and `develop`
- **Purpose:** Critical bug fixes in production
- **Delete:** After merge

---

## Git Workflow

### Current Workflow

The project currently uses a **simplified workflow** with feature branches merging directly to `main`:

```
main ← feature/CCSTRAT-1316
     ← feature/CCSTRAT-1317
     ← hotfix/0.1.1-fix
```

### Recommended Workflow (for larger teams)

**GitFlow** workflow for more structured releases:

```
         ┌─────────┐
         │  main   │  (production)
         └────┬────┘
              │
         ┌────▼────┐
         │ develop │  (integration)
         └────┬────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼──┐  ┌──▼──┐  ┌──▼───┐
│feature│  │feature│ │hotfix│
└───┬──┘  └──┬──┘  └──┬───┘
    │         │        │
    └─────────┴────────┘
```

### Common Commands

#### Creating a Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/TICKET-description
```

#### Working on a Feature
```bash
# Make changes
git add <files>
git commit -m "Description of changes"
git push -u origin feature/TICKET-description
```

#### Creating a Merge Request
```bash
# Push your branch
git push origin feature/TICKET-description

# Create MR (GitLab) or PR (GitHub)
# Through web UI or CLI tools
```

#### Merging to Main
```bash
# After MR/PR approval
git checkout main
git merge --no-ff feature/TICKET-description
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin main --tags
```

---

## Release Process

### Step-by-Step Release Guide

#### 1. Preparation

```bash
# Ensure you're on the latest main
git checkout main
git pull origin main

# Create release branch
git checkout -b release/0.2.0
```

#### 2. Version Update

Update version in `pyproject.toml`:
```toml
[project]
version = "0.2.0"
```

#### 3. Update CHANGELOG

Add release notes to `CHANGELOG.md`:
```markdown
## [0.2.0] - 2025-03-20

### Added
- New feature X
- Support for Y

### Fixed
- Bug in Z

### Changed
- Updated dependency A to version B
```

#### 4. Final Testing

```bash
# Run all tests
uv run pytest

# Type checking
uv run mypy comcheck_api

# Format checking
uv run black --check comcheck_api

# Build package
uv build

# Test installation
pip install dist/comcheck_api-0.2.0-py3-none-any.whl
```

#### 5. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Prepare release v0.2.0"
```

#### 6. Merge to Main

```bash
git checkout main
git merge --no-ff release/0.2.0
```

#### 7. Create Git Tag

```bash
# Annotated tag (preferred)
git tag -a v0.2.0 -m "Release version 0.2.0

- New feature X
- Bug fix for Y
- Performance improvements"

# View tag
git show v0.2.0
```

#### 8. Push Everything

```bash
git push origin main
git push origin v0.2.0
```

#### 9. Create GitHub Release

Via GitHub UI or CLI:
```bash
gh release create v0.2.0 \
  --title "Version 0.2.0" \
  --notes-file CHANGELOG.md \
  dist/comcheck_api-0.2.0-py3-none-any.whl \
  dist/comcheck_api-0.2.0.tar.gz
```

#### 10. Publish to PyPI

```bash
# Test on TestPyPI first
uv publish --repository testpypi

# Verify
pip install --index-url https://test.pypi.org/simple/ comcheck-api==0.2.0

# Publish to production PyPI
uv publish
```

#### 11. Cleanup

```bash
# Delete release branch
git branch -d release/0.2.0

# If pushed to remote
git push origin --delete release/0.2.0
```

---

## Version Numbering

### Current Version: `0.1.0`

### Version History (Planned)

| Version | Type | Status | Description |
|---------|------|--------|-------------|
| 0.1.0 | Alpha | Current | Initial development release |
| 0.2.0 | Alpha | Planned | Additional features, bug fixes |
| 0.5.0 | Beta | Planned | Feature complete, API stabilizing |
| 0.9.0 | RC | Planned | Release candidate, final testing |
| 1.0.0 | Stable | Planned | First production release |

### Versioning Rules

**Pre-1.0.0 (Current):**
- Breaking changes allowed in minor versions
- No stability guarantees
- Rapid iteration expected
- Documentation may lag

**Post-1.0.0:**
- Strict semantic versioning
- Breaking changes only in major versions
- Deprecation warnings before removal
- Maintain backward compatibility

### When to Release

#### Patch Release (0.1.X)
- Critical bug fixes
- Security patches
- Documentation fixes
- Release frequency: As needed

#### Minor Release (0.X.0)
- New features
- Non-breaking improvements
- Dependency updates
- Release frequency: Every 2-4 weeks

#### Major Release (X.0.0)
- Breaking API changes
- Major architecture changes
- Removal of deprecated features
- Release frequency: Every 6-12 months

---

## Git Tags

### Viewing Tags

```bash
# List all tags
git tag

# List with messages
git tag -n

# Show tag details
git show v0.1.0
```

### Creating Tags

```bash
# Lightweight tag
git tag v0.1.0

# Annotated tag (preferred)
git tag -a v0.1.0 -m "Release message"

# Tag specific commit
git tag -a v0.1.0 <commit-hash> -m "Message"
```

### Pushing Tags

```bash
# Push specific tag
git push origin v0.1.0

# Push all tags
git push origin --tags
```

### Deleting Tags

```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin --delete v0.1.0
```

---

## Best Practices

### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(client): add support for async operations

Add async versions of all client methods using httpx AsyncClient.
Maintains backward compatibility with sync methods.

Closes #123
```

### Branch Naming

```
feature/TICKET-short-description
hotfix/VERSION-issue-description
release/X.Y.Z
```

### Pull Request Guidelines

- One feature per PR
- Update tests
- Update documentation
- Pass all CI checks
- Request review from maintainers

### Changelog Maintenance

- Update CHANGELOG.md with every PR
- Use "Unreleased" section for in-progress work
- Move to version section on release
- Include migration guides for breaking changes

---

## Automation Opportunities

### GitHub Actions / GitLab CI

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build package
        run: uv build
      - name: Publish to PyPI
        run: uv publish
```

### Pre-commit Hooks

Already configured in `.pre-commit-config.yaml`:
- Black formatting
- Type checking (could add)
- Test running (could add)

---

*Document created: March 20, 2026*
