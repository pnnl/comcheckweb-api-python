#!/usr/bin/env python3
"""Generate TypedDict from comCheck.schema.json."""

import subprocess
import sys
from pathlib import Path

# Input and output paths
INPUT_SCHEMA = (
    Path(__file__).parent.parent / "comcheck_api" / "schemas" / "comCheck.schema.json"
)
OUTPUT_TYPES = Path(__file__).parent.parent / "comcheck_api" / "types" / "core_types.py"

# Ensure output directory exists
OUTPUT_TYPES.parent.mkdir(parents=True, exist_ok=True)

# Run datamodel-codegen CLI
result = subprocess.run(
    [
        "datamodel-codegen",
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
        "--use-default",  # Use default values from the schema
        "--field-constraints",  # Generate validation constraints (e.g., max_length, minItems)
        "--use-annotated",  # Best practice for Pydantic V2 validations
    ],
    check=False,
)

if result.returncode == 0:
    print(f"Generated: {OUTPUT_TYPES}")
else:
    print(f"Generation failed with exit code {result.returncode}", file=sys.stderr)
    sys.exit(result.returncode)
