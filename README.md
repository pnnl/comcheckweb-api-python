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

Get your API key from [COMcheck Web](https://comcheck.energycode.pnl.gov):

1. Log in to your COMcheck Web account
2. Navigate to **Settings → Developer Setting**
3. Generate and copy your API key

> **Note:** The Developer Setting feature is currently under development.

### 2. Configure the API Key

Create a `.env` file in your project root (or copy from `.env.example`):

```bash
COM_API_KEY=your-api-key-here
```

### 3. Install the Package

```bash
pip install comcheckweb-api-python
```

### 4. Start Using the Package

- **Simulation only:** You can use the simulation features directly without creating a project on COMcheck Web.
- **Updating a project:** You must first create the project under your account on [COMcheck Web](https://comcheck.energycode.pnl.gov) before using this package to update it. Project creation is not yet supported through this package.

For detailed usage examples and API reference, see the [documentation](https://pnnl-int.github.io/comcheckweb-api-python/).

## Development

Clone the repository and follow the commands below to set up developer tooling.

```bash
git clone https://github.com/pnnl-int/comcheckweb-api-python.git
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
