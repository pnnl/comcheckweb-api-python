# Documentation Index

This directory contains comprehensive documentation for the COMcheck API Python client library, including development guidelines, improvement plans, and version control strategies.

## Documentation Files

### 📋 [IMPROVEMENTS.md](IMPROVEMENTS.md)
**Complete improvement plan before publishing to GitHub/PyPI**

Contains:
- Critical security issues (API key in git)
- Code quality improvements needed
- Missing documentation requirements
- Pre-publication checklist
- Priority matrix for tasks

**Start here** to understand what needs to be fixed before publishing.

### 🔄 [VERSION_CONTROL.md](VERSION_CONTROL.md)
**Version control and release management strategy**

Contains:
- Semantic versioning guidelines
- Git branching strategy
- Release process step-by-step
- Git tag management
- Best practices for commits and branches

**Reference this** when creating releases or managing versions.

## Root Documentation Files

### 📝 [../CHANGELOG.md](../CHANGELOG.md)
**Version history and release notes**

- Tracks all changes by version
- Documents breaking changes
- Provides migration guides
- Follows [Keep a Changelog](https://keepachangelog.com/) format

**Update this** with every significant change.

### 🔧 [../.env.example](../.env.example)
**Environment configuration template**

- Template for required environment variables
- No sensitive data (safe to commit)
- Copy to `.env` and fill in actual values

**Use this** to set up your local environment.

---

## Quick Start for Developers

1. **Check** [IMPROVEMENTS.md](IMPROVEMENTS.md) - See current priorities
2. **Review** [VERSION_CONTROL.md](VERSION_CONTROL.md) - Understand release process
3. **Copy** [../.env.example](../.env.example) to `.env` and configure

---

## Quick Start for Maintainers

### Before First Release

Follow the checklist in [IMPROVEMENTS.md](IMPROVEMENTS.md):

**Critical (P0):**
- [ ] Remove `.env` from git
- [ ] Fix LICENSE placeholders
- [ ] Fix import paths in `__init__.py`

**High Priority (P1):**
- [ ] Replace `print()` with `logging`
- [ ] Make `BASE_URL` configurable
- [ ] Update README.md

### Creating a Release

Follow the process in [VERSION_CONTROL.md](VERSION_CONTROL.md):

```bash
# 1. Create release branch
git checkout -b release/0.1.0

# 2. Update version and changelog
# Edit pyproject.toml and CHANGELOG.md

# 3. Test everything
uv run pytest
uv run mypy comcheck_api
uv build

# 4. Merge and tag
git checkout main
git merge release/0.1.0
git tag -a v0.1.0 -m "Release v0.1.0"

# 5. Publish
git push origin main --tags
uv publish
```

---

## Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| IMPROVEMENTS.md | ✅ Complete | 2026-03-20 |
| VERSION_CONTROL.md | ✅ Complete | 2026-03-20 |
| ../CHANGELOG.md | ✅ Complete | 2026-03-20 |
| ../.env.example | ✅ Complete | 2026-03-20 |
| API Reference | ❌ TODO | - |
| User Guide | ⚠️ Partial (README) | - |
| Tutorial | ⚠️ Partial (examples/) | - |

---

## Additional Documentation Needed

### High Priority

1. **Enhanced README.md**
   - Installation instructions
   - Quick start guide
   - Feature overview
   - Usage examples
   - Configuration options
   - Links to docs

2. **API Reference** (`api-reference.md`)
   - Complete API documentation
   - All classes and methods
   - Parameters and return types
   - Examples for each method

3. **Type Reference** (`types-reference.md`)
   - All Pydantic models
   - Field descriptions
   - Validation rules
   - Usage examples

### Medium Priority

4. **User Guide** (`user-guide.md`)
   - Common use cases
   - Best practices
   - Troubleshooting
   - FAQ

5. **Tutorial** (`tutorial.md`)
   - Step-by-step walkthrough
   - Building a complete example
   - Explaining concepts

### Low Priority

6. **Architecture Guide** (`architecture.md`)
   - System design
   - Component overview
   - Design decisions

7. **Performance Guide** (`performance.md`)
   - Optimization tips
   - Benchmarks
   - Best practices

---

## Documentation Standards

### Markdown Style

- Use proper heading hierarchy (# → ## → ###)
- Include table of contents for long documents
- Use code blocks with language specification
- Use tables for structured data
- Include links between related documents

### Code Examples

```python
# Always include:
# 1. Import statements
# 2. Complete, runnable examples
# 3. Expected output (if relevant)
# 4. Error handling

from comcheck_api import COMcheckClient

# Initialize client
client = COMcheckClient(api_key="your-key")

# Use the client
try:
    projects = client.list_projects()
    print(f"Found {len(projects)} projects")
except Exception as e:
    print(f"Error: {e}")
```

### Document Structure

Each documentation file should have:
1. Clear title
2. Table of contents (if > 500 words)
3. Overview/introduction
4. Detailed sections
5. Examples
6. Related links
7. Last updated date

---

## Maintenance

### Regular Updates

Update documentation when:
- Adding new features
- Changing APIs
- Fixing bugs that affect usage
- Improving processes
- Learning new best practices

### Review Schedule

- **Weekly**: Check for outdated information
- **Monthly**: Review and update examples
- **Per Release**: Full documentation audit

---

## Documentation Tools

The project uses:
- **Markdown**: All documentation
- **GitHub/GitLab**: Rendering and hosting
- **Examples**: Live code in `examples/`
- **Docstrings**: In-code documentation

Consider adding in future:
- Sphinx/MkDocs for generated docs
- API documentation generator
- Documentation tests (doctest)

---

## Getting Help

### For Users

If you have questions about:
- **Using the library**: Check examples/ and README.md
- **Bug reports**: Open an issue on GitHub
- **Documentation**: Refer to the docs/ directory

### For Internal Development Team

- **Code improvements**: See [IMPROVEMENTS.md](IMPROVEMENTS.md)
- **Release process**: See [VERSION_CONTROL.md](VERSION_CONTROL.md)
- **Internal coordination**: Contact the development team

---

## Project Status

**🔓 Open Source** - Publicly available on GitHub
**🔒 Internal Development** - External contributions not accepted

This library is maintained by PNNL and developed internally. While the code is open source and free to use, we do not accept pull requests from external contributors. Issue reports and feedback are welcome.

---

*Documentation created: March 20, 2026*
*Last updated: March 20, 2026*
