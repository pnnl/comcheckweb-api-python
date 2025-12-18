# comcheckweb-api-python

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.pnnl.gov/becp/checktool-libraries/comcheckweb-api-python.git
# COMcheckWeb API — Python package

This repository contains the COMcheckWeb API Python package. It provides tools and scripts for working with the COMcheckWeb API and is intended to be used as a Python package maintained with `uv` for package management.

**Requirements:**
- Python: `>=3.12`

**Package management:**
- This project uses `uv` (configured in `pyproject.toml`) for dependency and workspace management. The `tool.uv` settings in `pyproject.toml` control workspace members and local sources.

Quickly useful notes:
- If you reference this package from other workspace packages, keep the `tool.uv.sources` entry that maps `comcheckweb-api-python = { workspace = true }` so `uv` resolves it to the local workspace copy.
- For a single-package repo you can also rely on `members = ["."]` and omit additional sources, but leaving the explicit source entry is harmless and makes intent clear.

## Getting started

Clone the repository and follow the commands below to set up developer tooling.

## Common commands

- Setup pre-commit (run once after cloning):
	`uv run pre-commit install`

- Fetch the latest COMcheck schema and regenerate types:
	`./fetch_comcheck_schema.sh`

- Regenerate types from existing schema (without fetching):
	`uv run comcheck_api/schemas/schema_generate.py`

- Run a script from `scripts/`:
	`uv run scripts/<script>`

- Run tests:
	`uv run pytest`

- Format the repository with Black:
	`uv run black comcheck_api tests scripts`

- Run type checking:
	`uv run mypy comcheck_api`

## Contributing

If you plan to contribute, please run the pre-commit installer, follow the repository style (Black, MyPy where configured), and open merge requests for changes. See `pyproject.toml` for configured dev tools and dependency groups.

## License

See the `LICENSE` file at the repository root for license details.
