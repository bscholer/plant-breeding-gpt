from datetime import date
from typing import Optional

from pydantic import BaseModel


# Pydantic models for request/response schemas
class PlantCross(BaseModel):
    cross_id: Optional[int] = None
    parent_1_id: int
    parent_2_id: int
    cross_date: date
    method: str
    comments: Optional[str] = None


class HydroponicCondition(BaseModel):
    condition_id: Optional[int] = None
    system_id: int
    date: date
    water_ph: float
    electrical_conductivity: float
    water_temperature_f: int
    tds: float
    comments: Optional[str] = None


class TasteTest(BaseModel):
    taste_test_id: Optional[int] = None
    plant_id: int
    date: date
    taste: str
    texture: str
    appearance: str
    overall: int
    comments: Optional[str] = None


class Yield(BaseModel):
    yield_id: Optional[int] = None
    plant_id: int
    date: date
    height_cm: float
    leaf_count: int
    color: str
    texture: str
    nutrient_level: int
    photo: Optional[bytes] = None
    notes: Optional[str] = None


class Observation(BaseModel):
    observation_id: Optional[int] = None
    plant_id: int
    date: date
    comments: Optional[str] = None


class Plant(BaseModel):
    plant_id: Optional[int] = None
    # Removed seed_id as it's now handled by the associative table
    plant_type: str
    species: str
    variety: str
    germination_date: date
    hydroponic_system_id: int
    comments: Optional[str] = None


class HydroponicSystem(BaseModel):
    system_id: Optional[int] = None
    system_type: str
    comments: Optional[str] = None


class Seed(BaseModel):
    seed_id: Optional[int] = None
    number_of_seeds: int
    # Removed cross_id; relationship is managed by SeedCross model
    comments: Optional[str] = None


class SeedCross(BaseModel):
    id: Optional[int] = None
    seed_id: int
    cross_id: int
