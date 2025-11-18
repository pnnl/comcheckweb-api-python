#!/usr/bin/env bash
set -euo pipefail

# Configuration (override via env vars)
REPO_SSH="${REPO_SSH:-ssh://git@gitlab-data.pnnl.gov:2222/becp/comcheck-schema.git}"
BRANCH="${BRANCH:-main}"
PATH_IN_REPO="${PATH_IN_REPO:-comCheck.schema.json}"
OUT="${OUT:-src/schemas/comCheck.schema.json}"

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
uv run src/schemas/schema_generate.py