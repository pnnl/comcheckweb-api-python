"""Example of calculating mechanical efficiency requirements with the COMcheck API client."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.defaults import get_default_project_template
from comcheck_api.types.core_types import (
    EnergyCodeOptions,
    ServiceWaterHeatingSystem,
    HVACSystem,
    HVACPlant,
    FanSystem,
    FanSystemPressureDropCredits,
    Fan,
    HVAC,
)

# Initialize client
load_dotenv(override=True)
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Build an IECC 2024 project
project = get_default_project_template()
project.control.code = EnergyCodeOptions.CEZ_IECC2024
energy_code = str(project.control.code)

# Example 1: Calculate water heater efficiency requirements
print("=== Water Heater Efficiency ===")
water_heater = ServiceWaterHeatingSystem(
    description="Domestic Hot Water",
    swhSystemType="SWH_SYSTEM_TYPE_STORAGE_TANK",
    fuelType="NATURAL_GAS",
)
efficiency = client.calculate_water_heater_efficiency(water_heater, energy_code)
for desc, eff in efficiency.items():
    print(f"{desc}: {eff.minEfficiency} - {eff.maxEfficiency} {eff.efficiencyUnits}")

# Example 2: Calculate HVAC system efficiency requirements
print("\n=== HVAC System Efficiency ===")
hvac_system = HVACSystem(
    description="Rooftop Unit 1",
    systemType="HVAC_SYSTEM_TYPE_PACKAGED_COOLING_AND_HEATING",
    quantity=2,
)
hvac_eff = client.calculate_hvac_system_efficiency(hvac_system, energy_code)
for desc, eff in hvac_eff.items():
    print(f"{desc}:")
    print(f"  Cooling: {eff.minCoolingEfficiency} {eff.coolingEfficiencyUnits}")
    if eff.minHeatingEfficiency:
        print(f"  Heating: {eff.minHeatingEfficiency} {eff.heatingEfficiencyUnits}")

# Example 3: Validate economizer requirements
print("\n=== Economizer Validation ===")
hvac_system.coolingCapacity = 80000  # Btu/h
validation = client.validate_hvac_system_economizer(hvac_system, energy_code)
print(f"Complies: {validation.complies}")
print(f"Limit without economizer: {validation.coolingCapLimitNoEconomizer}")

# Example 4: Calculate plant efficiency requirements
print("\n=== Plant Efficiency ===")
plant = HVACPlant(
    description="Chiller 1",
    plantType="PLANT_TYPE_CHILLER",
    systemType="PLANT_SYSTEM_TYPE_WATER_COOLED",
)
plant_eff = client.calculate_plant_efficiency(plant, energy_code)
for desc, eff in plant_eff.items():
    print(f"{desc}:")
    if eff.plantRequiredCoolingEfficiency:
        print(f"  Required cooling efficiency: {eff.plantRequiredCoolingEfficiency}")

# Example 5: Calculate fan pressure drop credit
print("\n=== Fan Pressure Drop Credit ===")
credit = FanSystemPressureDropCredits(
    type="PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12",
)
credit_value = client.calculate_fan_pressure_drop_credit(credit, energy_code)
print(f"Pressure drop credit: {credit_value}")

# Example 6: Check fan system compliance
print("\n=== Fan System Compliance ===")
fan_system = FanSystem(
    description="Supply Fan System 1",
    complyMethod="FAN_SYSTEM_MOTOR_NAMEPLATE_HP",
)
compliance = client.check_fan_system_compliance(fan_system, energy_code)
print(f"Complies: {compliance.complies}")
print(f"Method: {compliance.complyMethod}")
print(f"Proposed: {compliance.proposed}, Max allowed: {compliance.maxAllowed}")
print(f"Message: {compliance.complianceMessage}")

# Example 7: Calculate fan maximum allowable HP
print("\n=== Fan Maximum Allowable HP ===")
fan = Fan(
    description="Supply Fan 1",
    motorHp=5.0,
    airflow=10000,
)
max_hp = client.calculate_fan_maximum_allowable_hp(fan, energy_code)
print(f"Maximum allowable nameplate HP: {max_hp}")

# Example 8: Project write-back for fan system compliance
print("\n=== Update Fan System Compliance in Project ===")
project.hvac = HVAC(
    hvacSystem=[],
    hvacPlant=[],
    fanSystem=[
        FanSystem(
            description="Main Supply Fan System",
            complyMethod="FAN_SYSTEM_MOTOR_NAMEPLATE_HP",
            pressureDropCredits=[
                FanSystemPressureDropCredits(
                    type="PARTICULATE_FILTRATION_CREDIT_MERV_9_THRU_12",
                )
            ],
        )
    ],
)

# Update compliance fields
project = client.update_fan_system_compliance(project, "Main Supply Fan System")
fs = project.hvac.fanSystem[0]
print(f"Updated fan system - Complies: {fs.complies}, Method: {fs.complyMethod}")

# Update pressure drop credit values
project = client.update_fan_pressure_drop_credits(project, "Main Supply Fan System")
credit = fs.pressureDropCredits[0]
print(f"Updated pressure drop credit: {credit.pressureDropCredit}")

client.close()
