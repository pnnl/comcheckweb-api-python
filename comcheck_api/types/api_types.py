from typing import Any
from pydantic import BaseModel, ConfigDict


class ApiResponse(BaseModel):
    success: bool
    message: str | None = None
    data: Any = None
    errors: list[str] | None = None


class SessionInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    sessionId: str


class RunSimulationResponse(ApiResponse):
    data: SessionInfo | None = None


class StatusInfo(BaseModel):
    sessionId: str
    status: str
    message: str | None = None


class SimulationStatusResponse(ApiResponse):
    data: StatusInfo | None = None


class SimulationResultInfo(BaseModel):
    sessionId: str
    performanceRating: float | None = None
    energyCreditPerformanceRating: float | None = None
    proposedBpf: float | None = None
    baselineBpf: float | None = None


class SimulationResultResponse(ApiResponse):
    data: SimulationResultInfo | None = None
