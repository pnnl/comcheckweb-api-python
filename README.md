# COMcheckWeb API — Python Package

This repository contains the COMcheckWeb API Python package. It provides tools and scripts for working with the COMcheckWeb API and is intended to be used as a Python package maintained with `uv` for package management.

**Requirements:**
- Python: `>=3.12`

**Package management:**
- This project uses `uv` (configured in `pyproject.toml`) for dependency and workspace management. The `tool.uv` settings in `pyproject.toml` control workspace members and local sources.

Quickly useful notes:
- If you reference this package from other workspace packages, keep the `tool.uv.sources` entry that maps `comcheckweb-api-python = { workspace = true }` so `uv` resolves it to the local workspace copy.
- For a single-package repo you can also rely on `members = ["."]` and omit additional sources, but leaving the explicit source entry is harmless and makes intent clear.

## Usage

### 1. Obtain an API Key

Get a Personal Access Token from the new
[COMcheck Web site](https://comcheck.energycode.pnl.gov):

1. Log in (or register a new account if you don't have one).
2. Click your **username** in the left-side navigation.
3. From the menu that appears, choose **Settings**.
4. Click **Developer Setting** to open the Personal Access Token
   page.
5. Click **Generate**, then immediately copy the token.

> **Important:** the token is shown **only once**. Save it somewhere
> safe (a password manager, your `.env`, etc.) before leaving the
> page. If you lose it, generate a new one — the old one will stop
> working.

### 2. Configure the API Key

Create a `.env` file at the root of your project and add:

```
COM_API_KEY=<your-api-key-here>
```

The SDK does **not** auto-load this — you read it yourself and pass
it to the client. With `python-dotenv` this is two lines:

```python
import os
from dotenv import load_dotenv
from comcheck_api import COMcheckClient

load_dotenv()
client = COMcheckClient(api_key=os.environ["COM_API_KEY"])
```

(`client.set_api_key(api_key)` is the equivalent post-construction
setter if you'd rather defer.)

For more detail, see the
[Getting Started](https://pnnl.github.io/comcheckweb-api-python/getting-started/)
guide.

### 3. Install the Package

```bash
pip install comcheckweb-api-python
```

### 4. Start Using the Package

- **Simulation only:** You can use the simulation features directly without creating a project on COMcheck Web.
- **Updating a project:** You must first create the project under your account on [COMcheck Web](https://comcheck.energycode.pnl.gov) before using this package to update it. Project creation is not yet supported through this package.

For detailed usage examples and API reference, see the [documentation](https://pnnl.github.io/comcheckweb-api-python/).

## Introspection helpers

The package ships typed helpers for discovering what the SDK exposes
and for validating project data — useful from notebooks, IDE plugins,
and AI agents alike. All return Pydantic models; call `.model_dump()`
when you need JSON.

```python
import comcheck_api as cc

# What operation functions does the SDK ship?
for op in cc.list_operations():
    print(op.group, op.signature)

# What does the ComBuilding model look like?
schema = cc.lookup_type("ComBuilding")
for field in schema.fields:
    print(field.name, field.type, field.required)

# Does this dict satisfy the SDK schema?
result = cc.validate_project(project_dict)
if not result.ok:
    for err in result.errors:
        print(err.loc, err.msg)
```

See [`api/introspection`](https://pnnl.github.io/comcheckweb-api-python/api/introspection/)
in the docs for the full reference.

## AI integration: the Claude Skill

A bundled Claude Skill teaches Claude how to use this SDK correctly —
operation modules, default templates, the simulation polling loop,
common pitfalls. The Skill folder lives at
[`comcheck_api/ai/skill/`](comcheck_api/ai/skill/) and ships in the
wheel.

### Setup in your own repo

Install the bundled Skill into a project-level
`.claude/skills/comcheck-api/`. Claude Code scans
`<project>/.claude/skills/` when a session opens against the repo,
so the guidance kicks in only for projects that actually use this
SDK — not on every Claude session everywhere.

```bash
# Run this once in the root of the project that consumes comcheck_api:
comcheck-api install-skill
```

Commit `.claude/skills/comcheck-api/`. Teammates get the same
guidance the moment they open the repo in Claude Code, and Claude
can pull in the reference docs, examples, and `validate_code.py`
script on demand — not just the SKILL.md body. Re-run the command
with `--force` after upgrading the package to refresh the skill.

To install globally for every Claude session instead of per-project,
pass `--global` (writes to `~/.claude/skills/comcheck-api/`).

## Development

Clone the repository and follow the commands below to set up developer tooling.

```bash
git clone https://github.com/pnnl/comcheckweb-api-python.git
cd comcheckweb-api-python
uv sync
```

## Common commands

- Setup pre-commit (run once after cloning):
	`uv run pre-commit install`

- Fetch the latest COMcheck schema and regenerate types:
	`./tools/fetch_comcheck_schema.sh`

- Regenerate types from existing schema (without fetching):
	`uv run tools/generate_core_types.py`

- Run a file from `examples/`:
	`uv run examples/<script>`

- Run tests:
	`uv run pytest`

- Format the repository with Black:
	`uv run black comcheck_api tests examples`

- Run type checking:
	`uv run mypy comcheck_api`

## Running the docs locally

The documentation site is built with MkDocs (Material theme +
mkdocstrings). The dependencies live in the optional `docs` group
defined in `pyproject.toml`.

```bash
# Install the docs group (mkdocs, mkdocs-material, mkdocstrings).
uv sync --group docs

# Serve with live reload at http://127.0.0.1:8000
uv run mkdocs serve

# One-shot build into ./site/
uv run mkdocs build

# Fail on warnings (good before committing)
uv run mkdocs build --strict
```

## Support

This is a publicly available library maintained by PNNL. While the code is open source and free to use, **external contributions are not accepted** at this time.

### Reporting Issues

If you encounter bugs or have questions:
- Open an issue on GitHub for bug reports
- Check the [examples/](examples/) directory for usage guidance
- Review the [documentation](docs/) for detailed information

**Note:** Issues are welcome, but pull requests from external contributors will not be accepted.

## License

See the `LICENSE` file at the repository root for license details.
