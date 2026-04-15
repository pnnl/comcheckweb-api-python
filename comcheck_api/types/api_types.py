"""Pydantic models for COMcheck API request and response payloads.

These models represent the JSON structures returned by the COMcheck Web API
and are used internally by :class:`~comcheck_api.api.COMCheckApiService` and
:class:`~comcheck_api.client.COMcheckClient` for type-safe deserialization.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict


class ApiResponse(BaseModel):
    """Base model for all COMcheck API responses.

    Attributes:
        success: Whether the API call succeeded.
        message: Optional human-readable message from the server.
        data: Response payload (type varies by endpoint).
        errors: List of error strings, if any.
    """

    success: bool
    message: str | None = None
    data: Any = None
    errors: list[str] | None = None


class SessionInfo(BaseModel):
    """Session metadata returned when a simulation is started.

    Attributes:
        sessionId: Unique identifier for the simulation session.
    """

    model_config = ConfigDict(extra="allow")
    sessionId: str


class RunSimulationResponse(ApiResponse):
    """Response from the ``start-run-simulation`` endpoint.

    Attributes:
        data: Session information for the started simulation, or ``None`` on failure.
    """

    data: SessionInfo | None = None


class StatusInfo(BaseModel):
    """Simulation status details.

    Attributes:
        sessionId: The simulation session identifier.
        status: Current status string (e.g. ``"COMPLETED"``, ``"IN_PROGRESS"``).
        message: Optional status message from the server.
    """

    sessionId: str
    status: str
    message: str | None = None


class SimulationStatusResponse(ApiResponse):
    """Response from the ``get-status-simulation`` endpoint.

    Attributes:
        data: Status details for the queried session, or ``None`` on failure.
    """

    data: StatusInfo | None = None


class SimulationResultInfo(BaseModel):
    """Simulation result metrics.

    Attributes:
        sessionId: The simulation session identifier.
        performanceRating: Overall performance rating (percentage).
        energyCreditPerformanceRating: Energy credit performance rating.
        proposedBpf: Proposed building performance factor.
        baselineBpf: Baseline building performance factor.
    """

    sessionId: str
    performanceRating: float | None = None
    energyCreditPerformanceRating: float | None = None
    proposedBpf: float | None = None
    baselineBpf: float | None = None


class SimulationResultResponse(ApiResponse):
    """Response from the ``get-result-simulation`` endpoint.

    Attributes:
        data: Result metrics for the queried session, or ``None`` on failure.
    """

    data: SimulationResultInfo | None = None
