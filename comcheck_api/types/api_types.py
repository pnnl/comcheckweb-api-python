from enum import Enum
from typing import Any, List, NotRequired, Dict, TypedDict

from comcheck_api.types.core_types import *
from pydantic import BaseModel


class EndpointCallArgs(BaseModel):
    endpoint_name: str
    path_params: Dict[str, Any] | None = None
    query_params: Dict[str, Any] | None = None
    payload: Dict[str, Any] | None = None


class ApiResponse(TypedDict):
    success: bool
    message: NotRequired[str | None]
    data: NotRequired[Any]
    errors: NotRequired[list[str] | None]


class AgWallAssembliesUValuesArgs(CustomBaseModel):
    model_config = ConfigDict(
        extra='ignore',
    )
    description: str = "Ext Wall"
    assemblyType: str = "Ext Wall:Ext Wall"
    bldgUseKey: str = "0"
    wallType: WallTypeOptions = WallTypeOptions.METAL_FRAME_24_AG_WALL.value
    agWallConstructionDetailsType: AgWallConstructionDetailsTypeOptions = AgWallConstructionDetailsTypeOptions.NONE.value
    agWallExteriorFinishDetailsType: Optional[AgWallExteriorFinishDetailsTypeOptions] = None
    insulationPosition: Optional[str] = None
    otherWallType: AgWallOtherTypeOptions = AgWallOtherTypeOptions.NONE.value
    adjacentSpaceType: Optional[AdjacentSpaceTypeOptions] = None
    thermalBridge: list[ThermalBridge] = []
    thermalBridgeExceptionType: ThermalBridgeExceptionTypeOptions = ThermalBridgeExceptionTypeOptions.THERMAL_BRIDGE_EXCEPTION_NONE.value
    effectiveUFactor: float = 0.0
    allowanceType: Optional[EnvelopeAssemblyAllowanceTypeOptions] = None
    cmuType: Optional[CMUTypeOptions] = None
    concreteDensity: float = 0.0
    concreteThickness: float = 0.0
    constructionType: Optional[ConstructionTypeOptions] = None
    exemptionType: Optional[EnvelopeAssemblyExemptionOptions] = EnvelopeAssemblyExemptionOptions.ENV_EXEMPTION_NONE.value
    furringType: Optional[FurringTypeOptions] = FurringTypeOptions.NO_FURRING.value
    heatCapacity: float = 0.0
    orientation: OrientationOptions = OrientationOptions.UNSPECIFIED_ORIENTATION.value
    window: list[Window] = []
    door: list[Door] = []
    cavityRValue: float = 0.0
    continuousRValue: float = 0.0
    propUValue: float = 0.0
    altExemptType: Optional[AltExemptTypeOptions] = None
    grossArea: float = 0.0

class BgWallAssembliesUValuesArgs(CustomBaseModel):
    model_config = ConfigDict(
        extra='ignore',
    )
    description: str = "Basement"
    assemblyType: str = "Basement:Basement"
    bldgUseKey: str = "0"
    wallType: Optional[BgWallTypeOptions] = BgWallTypeOptions.CMU_LE_8IN_EMPTY_CELLS_BG_WALL.value
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
    furringType: Optional[FurringTypeOptions] = FurringTypeOptions.NO_FURRING.value
    heatCapacity: float = 0.0
    orientation: OrientationOptions = OrientationOptions.UNSPECIFIED_ORIENTATION.value
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
        extra='ignore',
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