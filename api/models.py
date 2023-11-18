from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# Pydantic models for request/response schemas
class PlantCross(BaseModel):
    """
    Used to create a new plant cross entry.
    Ensure that the user specifies the male and female plants.
    """
    cross_id: Optional[int] = Field(None, alias='id')
    parent_1_id: int = Field(..., alias='Male parent')
    parent_2_id: int = Field(..., alias='Female parent')
    cross_date: date
    method: str = Field(..., alias='Pollination Method, e.g. "Hand Pollination", "Open Pollination"')
    comments: Optional[str] = Field(None, alias='Comments')


class HydroponicCondition(BaseModel):
    """
    Used to create a new hydroponic condition entry.
    """
    condition_id: Optional[int] = Field(None, alias='id')
    system_id: int = Field(..., alias='System ID')
    date: date
    water_ph: Optional[float] = Field(..., alias='Water pH')
    electrical_conductivity: Optional[float] = Field(..., alias='Electrical Conductivity')
    water_temperature_f: Optional[int] = Field(..., alias='Water Temperature (F)')
    tds: Optional[float] = Field(..., alias='Total Dissolved Solids')
    comments: Optional[str] = Field(None, alias='Comments')


class TasteTest(BaseModel):
    """
    Used to create a new taste test. These are separate from yield entries because they are not necessarily
    associated with a yield entry.
    Before calling, request that the user tell you taste, texture, appearance, and overall ratings.
    Do not call this endpoint if the user does not give you all of these ratings.
    """
    taste_test_id: Optional[int] = Field(None, alias='id')
    plant_id: int = Field(..., alias='Plant ID')
    date: date
    taste: str = Field(..., alias='Taste rating (1-10)')
    texture: str = Field(..., alias='Texture rating (1-10)')
    appearance: str = Field(..., alias='Appearance rating (1-10)')
    overall: int = Field(..., alias='Overall rating (1-10)')
    comments: Optional[str] = Field(None, alias='Comments')


class Yield(BaseModel):
    yield_id: Optional[int] = Field(None, alias='id')
    plant_id: int = Field(..., alias='Plant ID')
    date: date
    color: str = Field(..., alias='Color (e.g. "Red", "Green", etc.)')
    texture: str = Field(..., alias='Texture (e.g. "Crisp", "Tender", etc.)')
    photo: Optional[bytes] = Field(None, alias='Photo')
    notes: Optional[str] = Field(None, alias='Notes')


class Observation(BaseModel):
    """
    Used to create a new observation.
    Do not input height or leaf count if not measured by the user and told explicitly
    """
    observation_id: Optional[int] = Field(None, alias='id')
    plant_id: int = Field(..., alias='Plant ID')
    date: date
    height_cm: Optional[float] = Field(..., alias='Height (cm) DO NOT INPUT IF NOT MEASURED')
    leaf_count: Optional[int] = Field(..., alias='Leaf Count DO NOT INPUT IF NOT MEASURED')
    color: str = Field(..., alias='Color of leaves (e.g. "Red", "Green", etc.)')
    texture: str = Field(..., alias='Texture of leaves (e.g. "Crisp", "Tender", etc.)')
    # photo: Optional[bytes] = None
    comments: Optional[str] = Field(None, alias='Comments')


class Plant(BaseModel):
    """
    Used to create a new plant.
    """
    plant_id: Optional[int] = Field(None, alias='id')
    germination_date: date
    hydroponic_system_id: int = Field(..., alias='Hydroponic System ID')
    seed_id: int = Field(..., alias='Seed ID')
    comments: Optional[str] = Field(None, alias='Comments')


class HydroponicSystem(BaseModel):
    """
    Used to create a new hydroponic system.
    """
    system_id: Optional[int] = Field(None, alias='id')
    system_type: str = Field(..., alias='System Type')
    comments: Optional[str] = Field(None, alias='Comments')


class Seed(BaseModel):
    """
    Used to create a new seed.
    """
    seed_id: Optional[int] = Field(None, alias='id')
    number_of_seeds: int = Field(..., alias='Number of Seeds')
    species: str = Field(..., alias='Species')
    variety: str = Field(..., alias='Variety')
    comments: Optional[str] = Field(None, alias='Comments')


class SeedCross(BaseModel):
    """
    This model is used to create a new seed cross. It is an association table between seeds and plant_crosses.
    """
    id: Optional[int] = Field(None, alias='id')
    seed_id: int = Field(..., alias='Seed ID')
    cross_id: int = Field(..., alias='Cross ID')