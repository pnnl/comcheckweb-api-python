"""Project-data validation helpers.

Discoverable from the package root:

    >>> from comcheck_api import validate_project
    >>> result = validate_project(project_data)
    >>> if not result.ok:
    ...     for err in result.errors:
    ...         print(err.loc, err.msg)

No network calls. Validates against the SDK's ``ComBuilding`` Pydantic
model.
"""

from __future__ import annotations

from typing import Any

import pydantic
from pydantic import BaseModel

from comcheck_api.types.core_types import ComBuilding


class ValidationError(BaseModel):
    """One Pydantic validation failure with a dotted location path."""

    loc: str
    msg: str
    type: str


class ValidationResult(BaseModel):
    """Outcome of validating a project against ``ComBuilding``."""

    ok: bool
    errors: list[ValidationError] = []


def validate_project(data: dict[str, Any] | ComBuilding) -> ValidationResult:
    """Validate ``data`` against the :class:`ComBuilding` Pydantic model.

    Accepts a dict or an existing ``ComBuilding`` (round-trips through
    ``model_dump`` so the same code path runs in both cases).
    """
    payload = data.model_dump() if isinstance(data, ComBuilding) else data
    try:
        ComBuilding.model_validate(payload)
    except pydantic.ValidationError as e:
        return ValidationResult(
            ok=False,
            errors=[
                ValidationError(
                    loc=".".join(str(x) for x in err["loc"]),
                    msg=err["msg"],
                    type=err["type"],
                )
                for err in e.errors()
            ],
        )
    return ValidationResult(ok=True, errors=[])


__all__ = ["ValidationError", "ValidationResult", "validate_project"]
