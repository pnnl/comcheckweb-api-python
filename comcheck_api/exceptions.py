"""Custom exceptions for COMcheck API client."""


class COMCheckAPIError(Exception):
    """Base exception for COMcheck API errors."""

    pass


class COMCheckHTTPError(COMCheckAPIError):
    """HTTP request failed."""

    def __init__(self, status_code: int, message: str, response_data: str = ""):
        """Initialize with the HTTP status code, message, and optional response body.

        Args:
            status_code: The HTTP status code returned by the API.
            message: Human-readable error description.
            response_data: Raw response body text (empty string if unavailable).
        """
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
        """Initialize with the ID of the project that was not found.

        Args:
            project_id: The project ID that could not be located.
        """
        self.project_id = project_id
        super().__init__(f"Project with ID '{project_id}' not found")
