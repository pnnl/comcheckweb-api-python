from typing import List, Optional
from pydantic import Field
from .core_types import *

class BgWallMinimalMixin:
	description: Optional[str] = Field(
		'Default Description',
		description='The name of the component',
	)
	assemblyType: str = Field(
		'Basement:Default Basement',
		description='The type of the component',
	)
	window: List[Window] = Field(
		[],
		description='Windows on the wall',
	)
	door: List[Door] = Field(
		[],
		description='Doors on the wall',
	)
	propUValue: float = Field(
		0.0,
		description='Proposed thermal transmittance of the below grade wall.',
	)
	concreteThickness: ConcreteThicknessOptions = Field(
		0.0,
		description='Concrete thickness',
	)
	concreteDensity: ConcreteDensityOptions = Field(
		0.0,
		description='Concrete density',
	)
	wallHeightBelowGrade: float = Field(
		0.0,
		description='Wall height below grade',
	)
	bldgUseKey: str = Field(
		'0',
		description='key reference of the building use area data group',
	)
	wallHeight: float = Field(
		0.0,
		description='Total height of a below grade wall',
	)
	adjacentSpaceType: Optional[AdjacentSpaceTypeOptions] = Field(
		None,
		description='Space type of the adjacent space',
	)
	insulationPosition: Optional[str] = Field(
		None,
		description='Not sure why basement has this data, likely deprecated. Use null',
	)
	heatCapacity: float = Field(
		0.0,
		description='heat capacity of a mass wall. Used in other mass wall type',
	)
	cmuType: Optional[CMUTypeOptions] = Field(
		None,
		description='CMU type',
	)
	allowanceType: Optional[EnvelopeAssemblyAllowanceTypeOptions] = Field(
		None,
		description='allowance type',
	)
	grossArea: float = Field(
		...,
		description='gross area',
	)
	orientation: OrientationOptions = Field(
		...,
	)
	wallType: Optional[BgWallTypeOptions] = Field(
		...,
		description='Below grade wall type',
	)
	cavityRValue: float = Field(
		...,
		description='Average insulation R-value in the cavity between two studs.',
	)
	continuousRValue: Optional[float] = Field(
		...,
		description='Continuous insulation on the below grade wall. Can be exterior or interior or both.',
	)

class BgWallMinimal(BgWallMinimalMixin, BgWall):
	pass
