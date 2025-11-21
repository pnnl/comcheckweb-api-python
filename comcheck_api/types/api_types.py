from typing import Any, NotRequired, TypedDict


class ApiResponse(TypedDict):
    success: bool
    message: NotRequired[str | None]
    data: NotRequired[Any]
    errors: NotRequired[list[str] | None]
