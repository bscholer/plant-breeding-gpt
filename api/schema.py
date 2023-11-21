from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DECIMAL, ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Seed(Base):
    __tablename__ = 'seeds'
    seed_id = Column(Integer, primary_key=True, autoincrement=True)
    yield_id = Column(Integer, ForeignKey('yield.yield_id'), nullable=True)
    species = Column(String(255), nullable=True)
    variety = Column(String(255), nullable=True)
    number_of_seeds = Column(Integer, nullable=True)
    comments = Column(Text, nullable=True)


class Germination(Base):
    __tablename__ = 'germination'
    germination_id = Column(Integer, primary_key=True, autoincrement=True)
    seed_id = Column(Integer, ForeignKey('seeds.seed_id'))
    planted_date = Column(Date)
    germination_date = Column(Date, nullable=True)
    seeds_attempted = Column(Integer)
    seeds_successful = Column(Integer, nullable=True)
    method = Column(String(255))
    comments = Column(Text, nullable=True)


class Plant(Base):
    __tablename__ = 'plants'
    plant_id = Column(Integer, primary_key=True, autoincrement=True)
    germination_id = Column(Integer, ForeignKey('germination.germination_id'))
    system_id = Column(Integer, ForeignKey('hydroponic_system.system_id'), nullable=True)
    comments = Column(Text, nullable=True)

    # Relationships
    plants = relationship("PlantPlantCross", back_populates="plant")


class Yield(Base):
    __tablename__ = 'yield'
    yield_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    cross_id = Column(Integer, ForeignKey('plant_crosses.cross_id'), nullable=True)
    date = Column(Date)
    color = Column(String(255))
    texture = Column(String(255))
    # photo = Column(BLOB, nullable=True)
    notes = Column(Text, nullable=True)


class PlantCross(Base):
    __tablename__ = 'plant_crosses'
    cross_id = Column(Integer, primary_key=True, autoincrement=True)
    cross_date = Column(Date)
    method = Column(String(255))
    comments = Column(Text, nullable=True)

    # Relationship to the associative table
    plants = relationship("PlantPlantCross", back_populates="cross")


class PlantPlantCross(Base):
    __tablename__ = 'plant_plant_cross'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    cross_id = Column(Integer, ForeignKey('plant_crosses.cross_id'))
    role = Column(String(255))  # Male or Female

    # Relationship to the Plant and PlantCross tables
    plant = relationship("Plant", back_populates="plants")
    cross = relationship("PlantCross", back_populates="plants")


class TasteTest(Base):
    __tablename__ = 'taste_test'
    taste_test_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    date = Column(Date)
    taste = Column(String(255))
    texture = Column(String(255))
    appearance = Column(String(255))
    overall = Column(Integer)
    comments = Column(Text, nullable=True)


class Observation(Base):
    __tablename__ = 'observations'
    observation_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    date = Column(Date)
    height_cm = Column(DECIMAL(5, 2), nullable=True)
    leaf_count = Column(Integer, nullable=True)
    color = Column(String(255), nullable=True)
    texture = Column(String(255), nullable=True)
    # photo = Column(BLOB)
    comments = Column(Text, nullable=True)


class HydroponicSystem(Base):
    __tablename__ = 'hydroponic_system'
    system_id = Column(Integer, primary_key=True, autoincrement=True)
    system_type = Column(String(255))
    comments = Column(Text, nullable=True)

    # Relationships
    conditions = relationship("HydroponicCondition")
    plants = relationship("Plant")


class HydroponicCondition(Base):
    __tablename__ = 'hydroponic_conditions'
    condition_id = Column(Integer, primary_key=True, autoincrement=True)
    system_id = Column(Integer, ForeignKey('hydroponic_system.system_id'))
    date = Column(Date)
    water_ph = Column(DECIMAL(3, 2), nullable=True)
    electrical_conductivity = Column(DECIMAL(5, 2), nullable=True)
    water_temperature_f = Column(Integer, nullable=True)
    comments = Column(Text, nullable=True)


# create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')

# Create all tables by issuing CREATE TABLE commands to the DB.
Base.metadata.create_all(engine)
