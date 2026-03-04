#!/usr/bin/env python3
"""Generate TypedDict from comCheck.schema.json."""
import subprocess
import sys
from pathlib import Path

# Input and output paths
INPUT_SCHEMA = Path(__file__).parent.parent / "comcheck_api" / "schemas" / "comCheck.schema.json"
DEFAULT_VALUES = Path(__file__).parent.parent / "comcheck_api" / "schemas" / "default_values.json"
ALIASES = Path(__file__).parent.parent / "comcheck_api" / "schemas" / "aliases.json"
ALIASES2 = Path(__file__).parent.parent / "comcheck_api" / "schemas" / "aliases2.json"


OUTPUT_TYPES = Path(__file__).parent.parent / "comcheck_api" / "types" /  "core_types_with_defaults.py"

# Ensure output directory exists
OUTPUT_TYPES.parent.mkdir(parents=True, exist_ok=True)

# Run datamodel-codegen CLI
result = subprocess.run(
    [
        "./.venv/bin/datamodel-codegen",
        "--input",
        str(INPUT_SCHEMA),
        "--input-file-type",
        "jsonschema",
        "--output",
        str(OUTPUT_TYPES),
        "--extra-fields",
        "ignore",
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--base-class",
        "comcheck_api.types.custom_base_model.CustomBaseModel",
        "--target-python-version",
        "3.13",
        "--use-standard-collections",
        "--use-schema-description",
        "--default-values",
        str(DEFAULT_VALUES),
        "--use-default",
 
        #         "--aliases",
        # str(ALIASES),
    ],
    check=False,
)

if result.returncode == 0:
    print(f"Generated: {OUTPUT_TYPES}")
else:
    print(f"Generation failed with exit code {result.returncode}", file=sys.stderr)
    sys.exit(result.returncode)