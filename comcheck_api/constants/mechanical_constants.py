"""Mechanical system constants for COMcheck projects."""

from comcheck_api.types.core_types import (
    HVACSystem,
    FanSystem,
    Fan,
    HVACPlant,
    ServiceWaterHeatingSystem,
    HeatingEquipmentTypeOptions,
    CoolingEquipmentTypeOptions,
    CondenserTypeOptions,
    DistributionTypeOptions,
    EconomizerTypeOptions,
    EconomizerExceptionOptions,
    FanControlOptions,
    FuelTypeOptions,
    HeatPumpPoolHeater,
    ZoneLayoutOptions,
    HeatPumpTypeOptions,
    FanSystemComplianceMethodOptions,
    FanTypeOptions,
    FanVolumeTypeOptions,
    FanEfficiencyExceptionTypeOptions,
    PlantTypeOptions,
    HeatingPlantTypeOptions,
    BoilerDraftTypeOptions,
    CompliancePathOptions,
    EquipmentEfficiencyRequirementExceptionOptions,
    SWHSystemTypeOptions,
    SWHFuelTypeOptions,
    SWHSystemDrawPatternTypeOptions,
    SWHSystemSubTypeOptions,
)

# packages/front-end-ui/src/global/add-water-heater/initial-state.ts
# packages/front-end-ui/src/global/add-water-heater/type-creator-util.ts
DEFAULT_WATER_HEATER: ServiceWaterHeatingSystem = ServiceWaterHeatingSystem(
    description="",
    systemType="Water Heater",
    swhSystemType=SWHSystemTypeOptions.STORAGE_WATER_HEATER,
    fuelType=SWHFuelTypeOptions.UNKNOWN_FUEL,
    quantity=1,
    storageCapacity=0.0,
    propSwhEquipEfficiency=0.0,
    circulationPump=False,
    heatTraceTapeInstalled=False,
    poolSystem=False,
    heatPumpPoolHeater=HeatPumpPoolHeater.int_0,
    combinedSystem=False,
    inputRating=75.0,
    swhSystemDrawPatternType=SWHSystemDrawPatternTypeOptions.UNKNOWN_DRAW_PATTERN,
    swhSystemSubType=SWHSystemSubTypeOptions.WATER_HEATER_STANDARD,
    efficiencyRequirementException=EquipmentEfficiencyRequirementExceptionOptions.EFF_EXCEPTION_UNSPECIFIED,
    altExemptType=None,
)

# packages/front-end-ui/src/global/add-hvac/initial-form-state.ts
# packages/front-end-ui/src/global/add-hvac/utils.ts
DEFAULT_HVAC_SYSTEM: HVACSystem = HVACSystem(
    description="",
    systemType="HVAC",
    condenser=CondenserTypeOptions.UNKNOWN_CONDENSER,
    constVolMixingBox=False,
    coolingEquipCapacity=0.0,
    coolingEquipment=CoolingEquipmentTypeOptions.NO_COOLING_EQUIPMENT,
    descriptionCoolEquip="Cooling Equip",
    descriptionHeatEquip="Heating Equip",
    distribution=DistributionTypeOptions.SINGLE_DUCT,
    economizer=EconomizerTypeOptions.NO_ECONOMIZER,
    economizerException=EconomizerExceptionOptions.NO_ECONOMIZER_EXCEPTION,
    electricReheat=False,
    fanControl=FanControlOptions.UNKNOWN_FAN_CONTROL,
    fanPoweredVav=False,
    fanSystemKey=None,
    fuel=FuelTypeOptions.UNKNOWN_FUEL,
    heatingEquipCapacity=0.0,
    heatingEquipment=HeatingEquipmentTypeOptions.NO_HEATING_EQUIPMENT,
    heatPump=HeatPumpTypeOptions.NO_HEATPUMP_TYPE,
    hydronicReheat=False,
    isHeatingSysWeatherized=False,
    perimeterSystem=False,
    propCoolingEquipEfficiencyPartial=0.0,
    propCoolingEquipEfficiency=0.0,
    propHeatingEquipEfficiency=0.0,
    quantity=1,
    quantityCoolEquip=1,
    quantityHeatEquip=1,
    reheatRecoolCoil=False,
    returnFanHp=0.0,
    steamReheat=False,
    supplyFanHp=0.0,
    supplyStaticPressure=0.0,
    totalFanHp=0.0,
    varAirBox=False,
    varAirVolMixingBox=False,
    zone=ZoneLayoutOptions.UNKNOWN_ZONE,
    altExemptType=None,
    spaceHeatingSystemException=None,
)

# packages/front-end-ui/src/global/add-plant/initial-values.ts
# packages/front-end-ui/src/global/add-plant/type-creator-util.ts (toBoiler)
DEFAULT_HVAC_PLANT: HVACPlant = HVACPlant(
    description="",
    systemType="HEATING_PLANT",
    plantType=PlantTypeOptions.HEATING_PLANT,
    heatingPlant=HeatingPlantTypeOptions.HOTWATER_PLANT,
    heatingPlantCapacity=100.0,
    boilerDraftType=BoilerDraftTypeOptions.FORCED_DRAFT,
    quantity=1,
    propHeatingPlantEfficiency=0.0,
    twoPipeSystem=False,
    waterloopHeatPump=False,
    compliancePath=CompliancePathOptions.COMPLIANCE_PATH_A,
    efficiencyRequirementException=EquipmentEfficiencyRequirementExceptionOptions.EFF_EXCEPTION_UNSPECIFIED,
    altExemptType=None,
)

# packages/front-end-ui/src/global/add-fan-system/initial-values.ts
# packages/front-end-ui/src/global/add-fan-system/utils.ts
DEFAULT_FAN_SYSTEM: FanSystem = FanSystem(
    description="",
    description2="",
    complyMethod=FanSystemComplianceMethodOptions.FAN_SYSTEM_MOTOR_NAMEPLATE_HP,
    hasPressureDropCredits=False,
    pressureDropCredits=[],
    fan=[],
    servesAllowanceAreaWithFlowControl=None,
)

# packages/front-end-ui/src/global/add-fan-system/initial-values.ts (fanUnderEdit)
DEFAULT_FAN: Fan = Fan(
    description="",
    fanType=FanTypeOptions.FAN_TYPE_UNSPECIFIED,
    fanVolumeType=FanVolumeTypeOptions.FAN_VOLUME_TYPE_UNSPECIFIED,
    volume=0.0,
    designBrakeHp=0.0,
    nameplateHp=0.0,
    fanEfficiency=0.0,
    totalFanEfficiency=0.0,
    fanDesignEfficiency=0.0,
    fanEfficiencyExceptionType=FanEfficiencyExceptionTypeOptions.FAN_EFFICIENCY_EXCEPTION_TYPE_UNSPECIFIED,
)
