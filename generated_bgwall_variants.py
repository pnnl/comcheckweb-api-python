from typing import Optional
from pydantic import Field
from comcheck_api.types.core_types import *

class BgWallMinimalMixin:
    description: Optional = Field(
        'Default Description',
        description='The name of the component',
    )
    assemblyType: str = Field(
        'Basement:Default Basement',
        description='The type of the component',
    )
    window: list = Field(
        [],
        description='Windows on the wall',
    )
    door: list = Field(
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
    grossArea: float = Field(
        ...,
        description='gross area',
    )
    orientation: OrientationOptions = Field(
        ...,
    )
    wallType: Optional = Field(
        ...,
        description='Below grade wall type',
    )
    cavityRValue: float = Field(
        ...,
        description='Average insulation R-value in the cavity between two studs.',
    )
    continuousRValue: Optional = Field(
        ...,
        description='Continuous insulation on the below grade wall. Can be exterior or interior or both.',
    )

class BgWallMinimal(BgWallMinimalMixin, BgWall):
    pass
