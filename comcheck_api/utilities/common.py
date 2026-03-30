"""Common utility helpers used across the package."""

import json
import logging
import random
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_random_number(min_value: int = 0, max_value: int = 100) -> int:
    """Return a pseudo-random integer between min_value and max_value inclusive."""
    return random.randint(min_value, max_value)


def export_to_json(data: Any, output_file: str | Path | None = None) -> str:
    """Convert and optionally save data to JSON.

    Args:
        data: The data to convert to JSON.
        output_file: Optional file path to save JSON data.

    Returns:
        JSON string representation of the data.

    Raises:
        Exception: If there's an error exporting data to JSON.
    """
    try:
        json_data = json.dumps(data, indent=2, ensure_ascii=False)

        if output_file:
            output_path = Path(output_file).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json_data, encoding="utf-8")
            logger.info("Data exported to %s", output_file)

        return json_data
    except Exception as error:
        logger.error("Error exporting data to JSON: %s", error, exc_info=True)
        raise
