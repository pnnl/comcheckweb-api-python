"""Pydantic models for COMcheck API request and response payloads.

These models represent the JSON structures returned by the COMcheck Web API
and are used internally by :class:`~comcheck_api.api.COMCheckApiService` and
:class:`~comcheck_api.client.COMcheckClient` for type-safe deserialization.
"""

from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict


class SimulationStatus(StrEnum):
    """Known lifecycle states for a COMcheck simulation session.

    This catalog is **not exhaustive** — the server may introduce
    additional states without notice. ``StatusInfo.status`` is typed
    as ``str`` so unknown values still parse cleanly; only the
    terminal pair (``SUCCESS`` / ``FAILED``) is guaranteed to remain
    stable. Compare against these members for terminal detection;
    treat anything else as "still in progress."
    """

    INITIALIZING = "INITIALIZING"
    GENERATING_BASELINE = "GENERATING_BASELINE"
    GENERATING_PROPOSED = "GENERATING_PROPOSED"
    RUNNING_SIMULATIONS = "RUNNING_SIMULATIONS"
    CALCULATING_RESULTS = "CALCULATING_RESULTS"
    EVALUATING = "EVALUATING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ApiResponse(BaseModel):
    """Base model for all COMcheck API responses.

    Attributes:
        success: Whether the API call succeeded. Defaults to ``True``
            because the server omits this field on successful responses
            (failures surface as non-2xx HTTP statuses, which the client
            raises as exceptions before validation).
        message: Optional human-readable message from the server.
        data: Response payload (type varies by endpoint).
        errors: List of error strings, if any.
    """

    success: bool = True
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
        status: Current lifecycle state. Typed as ``str`` because the
            server may emit values not yet enumerated in
            :class:`SimulationStatus` (the enum is a known-values
            catalog, not an exhaustive contract). The terminal pair
            (``"SUCCESS"`` / ``"FAILED"``) is guaranteed stable.
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
