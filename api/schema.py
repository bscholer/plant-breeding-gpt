from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DECIMAL, ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Associative table for seeds and plant crosses
class SeedCross(Base):
    __tablename__ = 'seed_cross'
    id = Column(Integer, primary_key=True, autoincrement=True)
    seed_id = Column(Integer, ForeignKey('seeds.seed_id'))
    cross_id = Column(Integer, ForeignKey('plant_crosses.cross_id'))


class PlantCross(Base):
    __tablename__ = 'plant_crosses'
    cross_id = Column(Integer, primary_key=True, autoincrement=True)
    parent_1_id = Column(Integer, ForeignKey('plants.plant_id'))
    parent_2_id = Column(Integer, ForeignKey('plants.plant_id'))
    cross_date = Column(Date)
    method = Column(String(255))
    comments = Column(Text)

    # Relationship to the associative table
    seeds = relationship('SeedCross', back_populates='cross')


class HydroponicCondition(Base):
    __tablename__ = 'hydroponic_conditions'
    condition_id = Column(Integer, primary_key=True, autoincrement=True)
    system_id = Column(Integer, ForeignKey('hydroponic_system.system_id'))
    date = Column(Date)
    water_ph = Column(DECIMAL(3, 2))
    electrical_conductivity = Column(DECIMAL(5, 2))
    water_temperature_f = Column(Integer)
    tds = Column(DECIMAL(5, 2))
    comments = Column(Text, nullable=True)


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


class Yield(Base):
    __tablename__ = 'yield'
    yield_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    date = Column(Date)
    color = Column(String(255))
    texture = Column(String(255))
    photo = Column(BLOB)
    notes = Column(Text)


class Observation(Base):
    __tablename__ = 'observations'
    observation_id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey('plants.plant_id'))
    date = Column(Date)
    height_cm = Column(DECIMAL(5, 2))
    leaf_count = Column(Integer)
    color = Column(String(255))
    texture = Column(String(255))
    # photo = Column(BLOB)
    comments = Column(Text, nullable=True)


class Plant(Base):
    __tablename__ = 'plants'
    plant_id = Column(Integer, primary_key=True, autoincrement=True)
    germination_date = Column(Date)
    hydroponic_system_id = Column(Integer, ForeignKey('hydroponic_system.system_id'))
    seed_id = Column(Integer, ForeignKey('seeds.seed_id'))
    comments = Column(Text)

    # Relationships
    plant_crosses_as_parent1 = relationship('PlantCross', foreign_keys=[PlantCross.parent_1_id])
    plant_crosses_as_parent2 = relationship('PlantCross', foreign_keys=[PlantCross.parent_2_id])


class HydroponicSystem(Base):
    __tablename__ = 'hydroponic_system'
    system_id = Column(Integer, primary_key=True, autoincrement=True)
    system_type = Column(String(255))
    comments = Column(Text, nullable=True)

    # Relationships
    conditions = relationship("HydroponicCondition")
    plants = relationship("Plant")


class Seed(Base):
    __tablename__ = 'seeds'
    seed_id = Column(Integer, primary_key=True, autoincrement=True)
    species = Column(String(255))
    variety = Column(String(255))
    number_of_seeds = Column(Integer)
    comments = Column(Text)

    # Relationship to the associative table
    crosses = relationship('SeedCross', back_populates='seed')


# Define back_populates for relationships in associative table
SeedCross.cross = relationship('PlantCross', back_populates='seeds')
SeedCross.seed = relationship('Seed', back_populates='crosses')

# create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')

# Create all tables by issuing CREATE TABLE commands to the DB.
Base.metadata.create_all(engine)
