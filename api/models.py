from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Seed(BaseModel):
    """
    Used to create a new seed.
    """
    seed_id: Optional[int] = Field(None, description='id')
    number_of_seeds: Optional[int] = Field(..., description='Number of Seeds')
    species: Optional[str] = Field(..., description='Species')
    variety: Optional[str] = Field(..., description='Variety')
    comments: Optional[str] = Field(None, description='Comments')


class Germination(BaseModel):
    """
    Used to track germination of seeds. This exists to track the germination method and date, and to track how fertile
    seeds are.
    """
    germination_id: Optional[int] = Field(None, description='id')
    seed_id: int = Field(..., description='Seed ID (FK)')
    planted_date: date
    germination_date: Optional[date]
    seeds_attempted: int = Field(..., description='Number of seeds attempted')
    seeds_successful: Optional[int] = Field(..., description='Number of seeds that germinated')
    method: str = Field(..., description='Germination Method')
    comments: Optional[str] = Field(None, description='Comments')


class Plant(BaseModel):
    """
    Used to create a new plant.
    """
    plant_id: Optional[int] = Field(None, description='id')
    germination_id: int = Field(..., description='Germination ID (FK)')
    system_id: Optional[int] = Field(..., description='Hydroponic System ID (FK)')
    death_date: Optional[date] = Field(None, description='Death Date')
    comments: Optional[str] = Field(None, description='Comments')


class Yield(BaseModel):
    yield_id: Optional[int] = Field(None, description='id')
    plant_id: int = Field(..., description='Plant ID (FK)')
    cross_id: Optional[int] = Field(None, description='Cross ID, include if applicable (FK)')
    date: date
    color: str = Field(..., description='Color (e.g. "Red", "Green", etc.)')
    texture: str = Field(..., description='Texture (e.g. "Crisp", "Tender", etc.)')
    # photo: Optional[bytes] = Field(None, description='Photo')
    notes: Optional[str] = Field(None, description='Notes')


# Pydantic models for request/response schemas
class PlantCross(BaseModel):
    """
    Used to create a new plant cross entry.
    Ensure that the user specifies the male and female plants.
    """
    cross_id: Optional[int] = Field(None, description='id')
    # parent_1_id: int = Field(..., description='Male parent')
    # parent_2_id: int = Field(..., description='Female parent')
    cross_date: date
    method: str = Field(..., description='Pollination Method, e.g. "Hand Pollination", "Open Pollination"')
    comments: Optional[str] = Field(None, description='Comments')


class PlantPlantCross(BaseModel):
    """
    Used to create a new PlantPlantCross entry, associating plants with their crosses.
    """
    # id: Optional[int] = Field(None, description='Auto-generated id of the plant-plant cross entry')
    plant_id: int = Field(..., description='Plant ID (FK)')
    cross_id: int = Field(..., description='Cross ID (FK)')
    role: str = Field(..., description='Role in the cross, either "Male" or "Female"')


class TasteTest(BaseModel):
    """
    Used to create a new taste test. These are separate from yield entries because they are not necessarily
    associated with a yield entry.
    Before calling, request that the user tell you taste, texture, appearance, and overall ratings.
    Do not call this endpoint if the user does not give you all of these ratings.
    """
    taste_test_id: Optional[int] = Field(None, description='id')
    plant_id: int = Field(..., description='Plant ID (FK)')
    date: date
    taste: str = Field(..., description='Taste rating (1-10)')
    texture: str = Field(..., description='Texture rating (1-10)')
    appearance: str = Field(..., description='Appearance rating (1-10)')
    overall: int = Field(..., description='Overall rating (1-10)')
    comments: Optional[str] = Field(None, description='Comments')


class Observation(BaseModel):
    """
    Used to create a new observation.
    Do not input height or leaf count if not measured by the user and told explicitly
    """
    observation_id: Optional[int] = Field(None, description='id')
    plant_id: int = Field(..., description='Plant ID (FK)')
    date: date
    height_cm: Optional[float] = Field(..., description='Height (cm) DO NOT INPUT IF NOT MEASURED')
    leaf_count: Optional[int] = Field(..., description='Leaf Count DO NOT INPUT IF NOT MEASURED')
    color: Optional[str] = Field(..., description='Color of leaves (e.g. "Red", "Green", etc.)')
    texture: Optional[str] = Field(..., description='Texture of leaves (e.g. "Crisp", "Tender", etc.)')
    # photo: Optional[bytes] = None
    comments: Optional[str] = Field(None, description='Comments')


class HydroponicSystem(BaseModel):
    """
    Used to create a new hydroponic system.
    """
    system_id: Optional[int] = Field(None, description='id')
    system_type: str = Field(..., description='System Type')
    comments: Optional[str] = Field(None, description='Comments')


class HydroponicCondition(BaseModel):
    """
    Used to create a new hydroponic condition entry.
    """
    condition_id: Optional[int] = Field(None, description='id')
    system_id: int = Field(..., description='System ID (FK)')
    date: date
    water_ph: Optional[float] = Field(..., description='Water pH')
    electrical_conductivity: Optional[float] = Field(..., description='Electrical Conductivity')
    water_temperature_f: Optional[int] = Field(..., description='Water Temperature (F)')
    comments: Optional[str] = Field(None, description='Comments')
