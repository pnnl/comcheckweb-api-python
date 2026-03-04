from typing import Any, List, Dict, Optional

from comcheck_api.types.core_types import *
from pydantic import BaseModel


class EndpointCallArgs(BaseModel):
    endpoint_name: str
    path_params: Dict[str, Any] | None = None
    query_params: Dict[str, Any] | None = None
    payload: BaseModel | Dict[str, Any] | None = None


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


class AgWallAssembliesUValuesArgs(CustomBaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    description: str = "Ext Wall"
    assemblyType: str = "Ext Wall:Ext Wall"
    bldgUseKey: str = "0"
    wallType: WallTypeOptions = WallTypeOptions.METAL_FRAME_24_AG_WALL
    agWallConstructionDetailsType: AgWallConstructionDetailsTypeOptions = AgWallConstructionDetailsTypeOptions.NONE
    agWallExteriorFinishDetailsType: Optional[AgWallExteriorFinishDetailsTypeOptions] = None
    insulationPosition: Optional[str] = None
    otherWallType: AgWallOtherTypeOptions = AgWallOtherTypeOptions.NONE
    adjacentSpaceType: Optional[AdjacentSpaceTypeOptions] = None
    thermalBridge: list[ThermalBridge] = []
    thermalBridgeExceptionType: ThermalBridgeExceptionTypeOptions = ThermalBridgeExceptionTypeOptions.THERMAL_BRIDGE_EXCEPTION_NONE
    effectiveUFactor: float = 0.0
    allowanceType: Optional[EnvelopeAssemblyAllowanceTypeOptions] = None
    cmuType: Optional[CMUTypeOptions] = None
    concreteDensity: float = 0.0
    concreteThickness: float = 0.0
    constructionType: Optional[ConstructionTypeOptions] = None
    exemptionType: Optional[EnvelopeAssemblyExemptionOptions] = EnvelopeAssemblyExemptionOptions.ENV_EXEMPTION_NONE
    furringType: Optional[FurringTypeOptions] = FurringTypeOptions.NO_FURRING
    heatCapacity: float = 0.0
    orientation: OrientationOptions = OrientationOptions.UNSPECIFIED_ORIENTATION
    window: list[Window] = []
    door: list[Door] = []
    cavityRValue: float = 0.0
    continuousRValue: float = 0.0
    propUValue: float = 0.0
    altExemptType: Optional[AltExemptTypeOptions] = None
    grossArea: float = 0.0

class BgWallAssembliesUValuesArgs(CustomBaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    description: str = "Basement"
    assemblyType: str = "Basement:Basement"
    bldgUseKey: str = "0"
    wallType: Optional[BgWallTypeOptions] = BgWallTypeOptions.CMU_LE_8IN_EMPTY_CELLS_BG_WALL
    wallHeight: float = 0.0
    wallHeightBelowGrade: float = 0.0
    adjacentSpaceType: Optional[AdjacentSpaceTypeOptions] = None
    adjacentSpaceBuildingType: Optional[WholeBuildingTypeOptions] = None
    allowanceType: Optional[EnvelopeAssemblyAllowanceTypeOptions] = None
    cmuType: Optional[CMUTypeOptions] = None
    concreteDensity: float = 0.0
    concreteThickness: float = 0.0
    constructionType: Optional[ConstructionTypeOptions] = None
    exemptionType: Optional[EnvelopeAssemblyExemptionOptions] = None
    furringType: Optional[FurringTypeOptions] = FurringTypeOptions.NO_FURRING
    heatCapacity: float = 0.0
    orientation: OrientationOptions = OrientationOptions.UNSPECIFIED_ORIENTATION
    insulationPosition: Optional[str] = None
    window: list[Window] = []
    door: list[Door] = []
    cavityRValue: float = 0.0
    continuousRValue: Optional[float] = 0.0
    propUValue: float = 0.0
    altExemptType: Optional[AltExemptTypeOptions] = None
    grossArea: float = 0.0

class AssembliesUValuesArgs(CustomBaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    agWall: List[Optional[AgWallAssembliesUValuesArgs]]= []
    bgWall: List[Optional[BgWallAssembliesUValuesArgs]] = []


class PlantEfficiencyArgs(HVACPlant):
    altExemptType: AltExemptTypeOptions = None
    boilerDraftType: BoilerDraftTypeOptions = "FORCED_DRAFT"
    compliancePath: CompliancePathOptions = "NA"
    description: str = "PLANT"
    efficiencyRequirementException: EquipmentEfficiencyRequirementExceptionOptions = "EFF_EXCEPTION_UNSPECIFIED"
    heatingPlant: HeatingPlantTypeOptions = "HOTWATER_PLANT"
    heatingPlantCapacity: float = 0
    propHeatingPlantEfficiency: float = 0
    quantity: int = 1
    systemType: str = "HEATING_PLANT"
    twoPipeSystem: bool = False
    waterloopHeatPump: bool = False