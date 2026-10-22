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


class EnergyCreditMessage(BaseModel):
    """A warning or user alert from the energy credit calculation.

    Attributes:
        level: ``info``, ``warning``, or ``error``.
        category: Message category, e.g. ``energy_credit`` or ``renewable``.
        message: Human-readable message.
        metadata: Extra details, if any.
    """

    model_config = ConfigDict(extra="allow")

    level: str | None = None
    category: str | None = None
    message: str | None = None
    metadata: dict[str, Any] | None = None


class BuildingAreaCredit(BaseModel):
    """Credits achieved by one energy credit in one building area.

    Attributes:
        creditType: The energy credit type (``EfficiencyPackage.type``).
        bldgUseKey: The building area key (``WholeBldgUse.key``).
        category: ``regular``, or ``renewable_load`` for renewable and load
            management credits. May be ``None`` from older backends.
        value: Credits achieved, weighted by the building area's share of the
            gross floor area.
    """

    model_config = ConfigDict(extra="allow")

    creditType: str | None = None
    bldgUseKey: str | None = None
    category: str | None = None
    value: float | None = None


class EnergyCreditResult(BaseModel):
    """Result of the ``update-energy-credits`` endpoint.

    Attributes:
        energyCredits: Credits achieved per building area and credit type.
        proposed: Total proposed credits.
        required: Total required credits.
        proposedRenewableAndLoadMgmt: Proposed renewable and load management
            credits. ``0`` for codes without the renewable trade-off.
        requiredRenewableAndLoadMgmt: Required renewable and load management
            credits. ``0`` for codes without the renewable trade-off.
        warnings: Calculation warnings, e.g. a credit missing an input.
        userAlerts: Alerts for the user, e.g. insufficient credits.
    """

    model_config = ConfigDict(extra="allow")

    energyCredits: list[BuildingAreaCredit] = []
    proposed: float | None = None
    required: float | None = None
    proposedRenewableAndLoadMgmt: float | None = None
    requiredRenewableAndLoadMgmt: float | None = None
    warnings: list[EnergyCreditMessage] = []
    userAlerts: list[EnergyCreditMessage] = []

    @property
    def passes(self) -> bool | None:
        """Whether proposed credits meet the required credits.

        Checks the renewable and load management credits too. ``None`` when
        the totals are missing. This is derived from the totals; the
        compliance check reports the official energy credit status.
        """
        if self.proposed is None or self.required is None:
            return None
        if self.proposed < self.required:
            return False
        return (self.proposedRenewableAndLoadMgmt or 0) >= (
            self.requiredRenewableAndLoadMgmt or 0
        )


class WaterHeaterEfficiency(BaseModel):
    """Efficiency requirements for a water heater.

    Attributes:
        minEfficiency: Minimum required efficiency.
        maxEfficiency: Maximum required efficiency.
        efficiencyUnits: Units for the efficiency values.
    """

    model_config = ConfigDict(extra="allow")

    minEfficiency: float | None = None
    maxEfficiency: float | None = None
    efficiencyUnits: str | None = None


class HVACSystemEfficiency(BaseModel):
    """Efficiency requirements for an HVAC system.

    Attributes:
        minCoolingEfficiency: Minimum cooling efficiency required.
        maxCoolingEfficiency: Maximum cooling efficiency required.
        minHeatingEfficiency: Minimum heating efficiency required.
        maxHeatingEfficiency: Maximum heating efficiency required.
        minPartLoadEfficiency: Minimum part-load efficiency.
        partLoadEfficiency: Part-load efficiency value.
        coolingEfficiencyUnits: Units for cooling efficiency.
        heatingEfficiencyUnits: Units for heating efficiency.
    """

    model_config = ConfigDict(extra="allow")

    minCoolingEfficiency: float | None = None
    maxCoolingEfficiency: float | None = None
    minHeatingEfficiency: float | None = None
    maxHeatingEfficiency: float | None = None
    minPartLoadEfficiency: float | None = None
    partLoadEfficiency: str | float | None = None
    coolingEfficiencyUnits: str | None = None
    heatingEfficiencyUnits: str | None = None


class EconomizerValidation(BaseModel):
    """Economizer validation results for an HVAC system.

    Attributes:
        coolingCapLimitNoEconomizer: Cooling capacity limit without economizer.
        coolCapNoReqLimit: Cooling capacity without requirement limit.
        coolCapNoEconomizer: Cooling capacity without economizer.
        complies: Whether the system complies with economizer requirements.
    """

    model_config = ConfigDict(extra="allow")

    coolingCapLimitNoEconomizer: str | float | None = None
    coolCapNoReqLimit: str | float | None = None
    coolCapNoEconomizer: str | float | None = None
    complies: bool | None = None


class PlantEfficiency(BaseModel):
    """Efficiency requirements for an HVAC plant.

    Attributes:
        plantMinHeatingEfficiency: Minimum plant heating efficiency.
        plantRequiredCoolingEfficiency: Required plant cooling efficiency.
        minPartLoadEfficiency: Minimum part-load efficiency.
        coolingEfficiencyUnits: Units for cooling efficiency.
        heatingEfficiencyUnits: Units for heating efficiency.
        partLoadEfficiencyUnits: Units for part-load efficiency.
    """

    model_config = ConfigDict(extra="allow")

    plantMinHeatingEfficiency: float | None = None
    plantRequiredCoolingEfficiency: float | None = None
    minPartLoadEfficiency: float | None = None
    coolingEfficiencyUnits: str | None = None
    heatingEfficiencyUnits: str | None = None
    partLoadEfficiencyUnits: str | None = None


class FanSystemComplianceResult(BaseModel):
    """Fan system compliance check results.

    Attributes:
        hasPressureDropCredits: Whether the system has pressure drop credits.
        complyMethod: Compliance method used.
        complies: Whether the system complies.
        complianceMessage: Compliance status message.
        proposed: Proposed fan system value.
        maxAllowed: Maximum allowed value.
    """

    model_config = ConfigDict(extra="allow")

    hasPressureDropCredits: bool | None = None
    complyMethod: str | None = None
    complies: bool | None = None
    complianceMessage: str | None = None
    proposed: float | None = None
    maxAllowed: float | None = None
