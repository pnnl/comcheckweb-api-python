"""Custom exceptions for COMcheck API client."""


class COMCheckAPIError(Exception):
    """Base exception for COMcheck API errors."""

    pass


class COMCheckHTTPError(COMCheckAPIError):
    """HTTP request failed."""

    def __init__(self, status_code: int, message: str, response_data: str = ""):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(f"HTTP {status_code}: {message}")


class COMCheckValidationError(COMCheckAPIError):
    """Validation failed."""

    pass


class COMCheckConnectionError(COMCheckAPIError):
    """Connection to COMcheck API failed."""

    pass


class COMCheckSimulationError(COMCheckAPIError):
    """Simulation-related error."""

    pass


class COMCheckProjectNotFoundError(COMCheckAPIError):
    """Project not found."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project with ID '{project_id}' not found")
