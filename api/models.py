from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Seed(BaseModel):
    """
    Used to create a new seed.
    """
    seed_id: Optional[int] = Field(None, description='id')
    yield_id: Optional[int] = Field(None, description='Yield ID (FK) - Optional')
    number_of_seeds: Optional[int] = Field(None, description='Number of Seeds - Optional')
    species: Optional[str] = Field(None, description='Species')
    variety: Optional[str] = Field(None, description='Variety')
    heirloom: Optional[int] = Field(None, description='Heirloom (1 if true, 0 if false) - Optional')
    comments: Optional[str] = Field(None, description='Comments - Optional')


class Germination(BaseModel):
    """
    Used to track germination of seeds. This exists to track the germination method and date, and to track how fertile
    seeds are.
    """
    germination_id: Optional[int] = Field(None, description='id')
    seed_id: int = Field(..., description='Seed ID (FK)')
    planted_date: date = Field(..., description='Planted Date - Required')
    germination_date: Optional[date] = Field(None, description='Germination Date - Optional')
    seeds_attempted: int = Field(None, description='Number of seeds attempted')
    seeds_successful: Optional[int] = Field(None, description='Number of seeds that germinated - Optional')
    method: str = Field(..., description='Germination Method')
    comments: Optional[str] = Field(None, description='Comments - Optional')


class Plant(BaseModel):
    """
    Used to create a new plant.
    """
    plant_id: Optional[int] = Field(None, description='id')
    germination_id: Optional[int] = Field(None, description='Germination ID (FK)')
    system_id: Optional[int] = Field(None, description='Hydroponic System ID (FK)')
    planted_date: Optional[date] = Field(None, description='Planted Date - Optional')
    death_date: Optional[date] = Field(None, description='Death Date - Optional')
    comments: Optional[str] = Field(None, description='Comments - Optional')


class Yield(BaseModel):
    yield_id: Optional[int] = Field(None, description='id')
    plant_id: int = Field(..., description='Plant ID (FK)')
    cross_id: Optional[int] = Field(None, description='Cross ID, include if applicable (FK) - Optional')
    date: date
    color: Optional[str] = Field(None, description='Color (e.g. "Red", "Green", etc.)')
    texture: Optional[str] = Field(None, description='Texture (e.g. "Crisp", "Tender", etc.)')
    # photo: Optional[bytes] = Field(None, description='Photo')
    comments: Optional[str] = Field(None, description='Comments - Optional')


# Pydantic models for request/response schemas
class PlantCross(BaseModel):
    """
    Used to create a new plant cross entry.
    Ensure that the user specifies the male and female plants.
    """
    cross_id: Optional[int] = Field(None, description='id')
    cross_date: date
    method: str = Field(..., description='Pollination Method, e.g. "Hand Pollination", "Open Pollination"')
    comments: Optional[str] = Field(None, description='Comments - Optional')


class PlantPlantCross(BaseModel):
    """
    Used to create a new PlantPlantCross entry, associating plants with their crosses.
    """
    id: Optional[int] = Field(None, description='Auto-generated id of the plant-plant cross entry')
    plant_id: int = Field(..., description='Plant ID (FK)')
    cross_id: int = Field(..., description='Cross ID (FK)')


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
    taste: int = Field(..., description='Taste rating (1-10)')
    texture: int = Field(..., description='Texture rating (1-10)')
    appearance: int = Field(..., description='Appearance rating (1-10)')
    overall: int = Field(..., description='Overall rating (1-10)')
    comments: Optional[str] = Field(None, description='Comments - Optional')


class Observation(BaseModel):
    """
    Used to create a new observation.
    Do not input height or leaf count if not measured by the user and told explicitly
    """
    observation_id: Optional[int] = Field(None, description='id')
    plant_id: int = Field(..., description='Plant ID (FK)')
    date: date
    height_cm: Optional[float] = Field(None, description='Height (cm) DO NOT INPUT IF NOT MEASURED - Optional')
    leaf_count: Optional[int] = Field(None, description='Leaf Count DO NOT INPUT IF NOT MEASURED - Optional')
    color: Optional[str] = Field(None, description='Color of leaves (e.g. "Red", "Green", etc.) - Optional')
    texture: Optional[str] = Field(None, description='Texture of leaves (e.g. "Crisp", "Tender", etc.) - Optional')
    # photo: Optional[bytes] = None
    comments: Optional[str] = Field(None, description='Comments - Optional')


class HydroponicSystem(BaseModel):
    """
    Used to create a new hydroponic system.
    """
    system_id: Optional[int] = Field(None, description='id')
    system_type: str = Field(..., description='System Type')
    comments: Optional[str] = Field(None, description='Comments - Optional')


class HydroponicCondition(BaseModel):
    """
    Used to create a new hydroponic condition entry.
    """
    condition_id: Optional[int] = Field(None, description='id')
    system_id: int = Field(..., description='System ID (FK)')
    date: date
    water_ph: Optional[float] = Field(None, description='Water pH - Optional')
    electrical_conductivity_us_cm: Optional[float] = Field(None,
                                                           description='Electrical Conductivity (uS/cm) - Optional')
    water_temperature_f: Optional[float] = Field(None,
                                                 description='Water Temperature (F), convert to F if provided in C - Optional')
    comments: Optional[str] = Field(None, description='Comments - Optional')
