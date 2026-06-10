#!/usr/bin/env bash
#
# (maintainer use only)
#
# Fetch the COMcheck JSON schema from a git repo (sparse-checkout) and
# regenerate the SDK's TypedDict types from it.
#
# Required env var:
#   REPO_SSH  — git SSH URL of the schema-hosting repo
#
# Optional env vars (with sensible defaults):
#   BRANCH        — branch to check out (default: main)
#   PATH_IN_REPO  — path to the schema file inside that repo
#                   (default: comCheck.schema.json)
#   OUT           — destination path inside this repo
#                   (default: comcheck_api/schemas/comCheck.schema.json)
#
# Example:
#   REPO_SSH=ssh://git@example.org/path/to/comcheck-schema.git \
#     ./tools/fetch_comcheck_schema.sh
set -euo pipefail

# Load REPO_SSH (and any other vars) from a .env file at the repo root if present,
# without clobbering values already set in the environment.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-$SCRIPT_DIR/../.env}"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

REPO_SSH="${REPO_SSH:?REPO_SSH must be set, e.g. REPO_SSH=ssh://git@host/path/to/comcheck-schema.git}"
BRANCH="${BRANCH:-main}"
PATH_IN_REPO="${PATH_IN_REPO:-comCheck.schema.json}"
OUT="${OUT:-comcheck_api/schemas/comCheck.schema.json}"

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

echo "Cloning $REPO_SSH (sparse) to fetch $PATH_IN_REPO from branch $BRANCH..."
git clone --no-checkout "$REPO_SSH" "$TMP_DIR"
cd "$TMP_DIR"

git sparse-checkout init --cone
git sparse-checkout set "$PATH_IN_REPO"
git checkout "$BRANCH"

mkdir -p "$(dirname "$OUT")"
cp "$PATH_IN_REPO" "$OLDPWD/$OUT"

echo "Saved $OUT"

# Generate TypedDict types from the schema
echo "Generating TypedDict types..."
cd "$OLDPWD"
uv run tools/generate_core_types.py