import logging
import os
from typing import List

from databases import Database
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.openapi.models import Server
from mangum import Mangum
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from starlette import status

import models
import schema

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()

DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:" \
               f"{os.getenv('DB_PASSWORD')}@" \
               f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

metadata = MetaData()

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

database = Database(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print('created sessionmaker')

apiGatewayEndpoint = "https://7l6fx6h5y5.execute-api.us-east-2.amazonaws.com"

app = FastAPI(servers=[{"url": apiGatewayEndpoint, "description": "AWS API Gateway"}])


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def get_api_key(api_key: str = Header(...)):
    if api_key != os.getenv('API_KEY'):
        raise HTTPException(status_code=400, detail="Invalid API Key")
    return api_key


@app.post("/run_select_query/")
async def run_select_query(query: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    # Check that only SELECT statements are allowed
    if not query.strip().lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed.")

    # Execute the query safely
    try:
        result = db.execute(query).fetchall()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# CREATE a new plant_cross
@app.post("/plant_crosses/", response_model=models.PlantCross, status_code=status.HTTP_201_CREATED)
def create_plant_cross(plant_cross: models.PlantCross, db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    db_plant_cross = schema.PlantCross(**plant_cross.dict())
    db.add(db_plant_cross)
    db.commit()
    db.refresh(db_plant_cross)
    return db_plant_cross


# CREATE many new plant_crosses
@app.post("/plant_crosses/bulk", response_model=List[models.PlantCross], status_code=status.HTTP_201_CREATED)
def create_plant_crosses(plant_crosses: List[models.PlantCross], db: Session = Depends(get_db),
                         api_key: str = Depends(get_api_key)):
    db_plant_crosses = [schema.PlantCross(**plant_cross.dict()) for plant_cross in plant_crosses]
    db.add_all(db_plant_crosses)
    db.commit()
    return db_plant_crosses


# READ all plant_crosses
@app.get("/plant_crosses/", response_model=List[models.PlantCross])
def read_plant_crosses(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.PlantCross).all()


# READ a single plant_cross by ID
@app.get("/plant_crosses/{cross_id}", response_model=models.PlantCross)
def read_plant_cross(cross_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    plant_cross = db.query(schema.PlantCross).filter(schema.PlantCross.cross_id == cross_id).first()
    if plant_cross is None:
        raise HTTPException(status_code=404, detail="PlantCross not found")
    return plant_cross


# UPDATE a plant_cross by ID
@app.put("/plant_crosses/{cross_id}", response_model=models.PlantCross)
def update_plant_cross(cross_id: int, update_data: models.PlantCross, db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    plant_cross = db.query(schema.PlantCross).filter(schema.PlantCross.cross_id == cross_id).first()
    if plant_cross is None:
        raise HTTPException(status_code=404, detail="PlantCross not found")
    for key, value in update_data.dict().items():
        setattr(plant_cross, key, value)
    db.commit()
    return plant_cross


# DELETE a plant_cross by ID
@app.delete("/plant_crosses/{cross_id}", response_model=models.PlantCross)
def delete_plant_cross(cross_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    plant_cross = db.query(schema.PlantCross).filter(schema.PlantCross.cross_id == cross_id).first()
    if plant_cross is None:
        raise HTTPException(status_code=404, detail="PlantCross not found")
    db.delete(plant_cross)
    db.commit()
    return plant_cross


# CREATE a new hydroponic_condition
@app.post("/hydroponic_conditions/", response_model=models.HydroponicCondition, status_code=status.HTTP_201_CREATED)
def create_hydroponic_condition(hydroponic_condition: models.HydroponicCondition, db: Session = Depends(get_db),
                                api_key: str = Depends(get_api_key)):
    db_hydroponic_condition = schema.HydroponicCondition(**hydroponic_condition.dict())
    db.add(db_hydroponic_condition)
    db.commit()
    db.refresh(db_hydroponic_condition)
    return db_hydroponic_condition


# CREATE many new hydroponic_conditions
@app.post("/hydroponic_conditions/bulk", response_model=List[models.HydroponicCondition],
          status_code=status.HTTP_201_CREATED)
def create_hydroponic_conditions(hydroponic_conditions: List[models.HydroponicCondition], db: Session = Depends(get_db),
                                 api_key: str = Depends(get_api_key)):
    db_hydroponic_conditions = [schema.HydroponicCondition(**hydroponic_condition.dict()) for hydroponic_condition in
                                hydroponic_conditions]
    db.add_all(db_hydroponic_conditions)
    db.commit()
    return db_hydroponic_conditions


# READ all hydroponic_conditions
@app.get("/hydroponic_conditions/", response_model=List[models.HydroponicCondition])
def read_hydroponic_conditions(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.HydroponicCondition).all()


# READ a single hydroponic_condition by ID
@app.get("/hydroponic_conditions/{condition_id}", response_model=models.HydroponicCondition)
def read_hydroponic_condition(condition_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    hydroponic_condition = db.query(schema.HydroponicCondition).filter(
        schema.HydroponicCondition.condition_id == condition_id).first()
    if hydroponic_condition is None:
        raise HTTPException(status_code=404, detail="HydroponicCondition not found")
    return hydroponic_condition


# UPDATE a hydroponic_condition by ID
@app.put("/hydroponic_conditions/{condition_id}", response_model=models.HydroponicCondition)
def update_hydroponic_condition(condition_id: int, update_data: models.HydroponicCondition,
                                db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    hydroponic_condition = db.query(schema.HydroponicCondition).filter(
        schema.HydroponicCondition.condition_id == condition_id).first()
    if hydroponic_condition is None:
        raise HTTPException(status_code=404, detail="HydroponicCondition not found")
    for key, value in update_data.dict().items():
        setattr(hydroponic_condition, key, value)
    db.commit()
    return hydroponic_condition


# DELETE a hydroponic_condition by ID
@app.delete("/hydroponic_conditions/{condition_id}", response_model=models.HydroponicCondition)
def delete_hydroponic_condition(condition_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    hydroponic_condition = db.query(schema.HydroponicCondition).filter(
        schema.HydroponicCondition.condition_id == condition_id).first()
    if hydroponic_condition is None:
        raise HTTPException(status_code=404, detail="HydroponicCondition not found")
    db.delete(hydroponic_condition)
    db.commit()
    return hydroponic_condition


# CREATE a new taste_test
@app.post("/taste_tests/", response_model=models.TasteTest, status_code=status.HTTP_201_CREATED)
def create_taste_test(taste_test: models.TasteTest, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_taste_test = schema.TasteTest(**taste_test.dict())
    db.add(db_taste_test)
    db.commit()
    db.refresh(db_taste_test)
    return db_taste_test


# CREATE many new taste_tests
@app.post("/taste_tests/bulk", response_model=List[models.TasteTest], status_code=status.HTTP_201_CREATED)
def create_taste_tests(taste_tests: List[models.TasteTest], db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    db_taste_tests = [schema.TasteTest(**taste_test.dict()) for taste_test in taste_tests]
    db.add_all(db_taste_tests)
    db.commit()
    return db_taste_tests


# READ all taste_tests
@app.get("/taste_tests/", response_model=List[models.TasteTest])
def read_taste_tests(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.TasteTest).all()


# READ a single taste_test by ID
@app.get("/taste_tests/{taste_test_id}", response_model=models.TasteTest)
def read_taste_test(taste_test_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    taste_test = db.query(schema.TasteTest).filter(schema.TasteTest.taste_test_id == taste_test_id).first()
    if taste_test is None:
        raise HTTPException(status_code=404, detail="TasteTest not found")
    return taste_test


# UPDATE a taste_test by ID
@app.put("/taste_tests/{taste_test_id}", response_model=models.TasteTest)
def update_taste_test(taste_test_id: int, update_data: models.TasteTest, db: Session = Depends(get_db),
                      api_key: str = Depends(get_api_key)):
    taste_test = db.query(schema.TasteTest).filter(schema.TasteTest.taste_test_id == taste_test_id).first()
    if taste_test is None:
        raise HTTPException(status_code=404, detail="TasteTest not found")
    for key, value in update_data.dict().items():
        setattr(taste_test, key, value)
    db.commit()
    return taste_test


# DELETE a taste_test by ID
@app.delete("/taste_tests/{taste_test_id}", response_model=models.TasteTest)
def delete_taste_test(taste_test_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    taste_test = db.query(schema.TasteTest).filter(schema.TasteTest.taste_test_id == taste_test_id).first()
    if taste_test is None:
        raise HTTPException(status_code=404, detail="TasteTest not found")
    db.delete(taste_test)
    db.commit()
    return taste_test


# CREATE a new yield
@app.post("/yields/", response_model=models.Yield, status_code=status.HTTP_201_CREATED)
def create_yield(yield_: models.Yield, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_yield = schema.Yield(**yield_.dict())
    db.add(db_yield)
    db.commit()
    db.refresh(db_yield)
    return db_yield


# CREATE many new yields
@app.post("/yields/bulk", response_model=List[models.Yield], status_code=status.HTTP_201_CREATED)
def create_yields(yields: List[models.Yield], db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_yields = [schema.Yield(**yield_.dict()) for yield_ in yields]
    db.add_all(db_yields)
    db.commit()
    return db_yields


# READ all yields
@app.get("/yields/", response_model=List[models.Yield])
def read_yields(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.Yield).all()


# READ a single yield by ID
@app.get("/yields/{yield_id}", response_model=models.Yield)
def read_yield(yield_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    yield_ = db.query(schema.Yield).filter(schema.Yield.yield_id == yield_id).first()
    if yield_ is None:
        raise HTTPException(status_code=404, detail="Yield not found")
    return yield_


# UPDATE a yield by ID
@app.put("/yields/{yield_id}", response_model=models.Yield)
def update_yield(yield_id: int, update_data: models.Yield, db: Session = Depends(get_db),
                 api_key: str = Depends(get_api_key)):
    yield_ = db.query(schema.Yield).filter(schema.Yield.yield_id == yield_id).first()
    if yield_ is None:
        raise HTTPException(status_code=404, detail="Yield not found")
    for key, value in update_data.dict().items():
        setattr(yield_, key, value)
    db.commit()
    return yield_


# DELETE a yield by ID
@app.delete("/yields/{yield_id}", response_model=models.Yield)
def delete_yield(yield_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    yield_ = db.query(schema.Yield).filter(schema.Yield.yield_id == yield_id).first()
    if yield_ is None:
        raise HTTPException(status_code=404, detail="Yield not found")
    db.delete(yield_)
    db.commit()
    return yield_


# CREATE a new observation
@app.post("/observations/", response_model=models.Observation, status_code=status.HTTP_201_CREATED)
def create_observation(observation: models.Observation, db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    db_observation = schema.Observation(**observation.dict())
    db.add(db_observation)
    db.commit()
    db.refresh(db_observation)
    return db_observation


# CREATE many new observations
@app.post("/observations/bulk", response_model=List[models.Observation], status_code=status.HTTP_201_CREATED)
def create_observations(observations: List[models.Observation], db: Session = Depends(get_db),
                        api_key: str = Depends(get_api_key)):
    db_observations = [schema.Observation(**observation.dict()) for observation in observations]
    db.add_all(db_observations)
    db.commit()
    return db_observations


# READ all observations
@app.get("/observations/", response_model=List[models.Observation])
def read_observations(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.Observation).all()


# READ a single observation by ID
@app.get("/observations/{observation_id}", response_model=models.Observation)
def read_observation(observation_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    observation = db.query(schema.Observation).filter(schema.Observation.observation_id == observation_id).first()
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    return observation


# UPDATE a observation by ID
@app.put("/observations/{observation_id}", response_model=models.Observation)
def update_observation(observation_id: int, update_data: models.Observation, db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    observation = db.query(schema.Observation).filter(schema.Observation.observation_id == observation_id).first()
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    for key, value in update_data.dict().items():
        setattr(observation, key, value)
    db.commit()
    return observation


# DELETE a observation by ID
@app.delete("/observations/{observation_id}", response_model=models.Observation)
def delete_observation(observation_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    observation = db.query(schema.Observation).filter(schema.Observation.observation_id == observation_id).first()
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    db.delete(observation)
    db.commit()
    return observation


# CREATE a new plant
@app.post("/plants/", response_model=models.Plant, status_code=status.HTTP_201_CREATED)
def create_plant(plant: models.Plant, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_plant = schema.Plant(**plant.dict())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant


# CREATE many new plants
@app.post("/plants/bulk", response_model=List[models.Plant], status_code=status.HTTP_201_CREATED)
def create_plants(plants: List[models.Plant], db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_plants = [schema.Plant(**plant.dict()) for plant in plants]
    db.add_all(db_plants)
    db.commit()
    return db_plants


# READ all plants
@app.get("/plants/", response_model=List[models.Plant])
def read_plants(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.Plant).all()


# READ a single plant by ID
@app.get("/plants/{plant_id}", response_model=models.Plant)
def read_plant(plant_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    plant = db.query(schema.Plant).filter(schema.Plant.plant_id == plant_id).first()
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


# UPDATE a plant by ID
@app.put("/plants/{plant_id}", response_model=models.Plant)
def update_plant(plant_id: int, update_data: models.Plant, db: Session = Depends(get_db),
                 api_key: str = Depends(get_api_key)):
    plant = db.query(schema.Plant).filter(schema.Plant.plant_id == plant_id).first()
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    for key, value in update_data.dict().items():
        setattr(plant, key, value)
    db.commit()
    return plant


# DELETE a plant by ID
@app.delete("/plants/{plant_id}", response_model=models.Plant)
def delete_plant(plant_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    plant = db.query(schema.Plant).filter(schema.Plant.plant_id == plant_id).first()
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(plant)
    db.commit()
    return plant


# CREATE a new hydroponic_system
@app.post("/hydroponic_systems/", response_model=models.HydroponicSystem, status_code=status.HTTP_201_CREATED)
def create_hydroponic_system(hydroponic_system: models.HydroponicSystem, db: Session = Depends(get_db),
                             api_key: str = Depends(get_api_key)):
    db_hydroponic_system = schema.HydroponicSystem(**hydroponic_system.dict())
    db.add(db_hydroponic_system)
    db.commit()
    db.refresh(db_hydroponic_system)
    return db_hydroponic_system


# CREATE many new hydroponic_systems
@app.post("/hydroponic_systems/bulk", response_model=List[models.HydroponicSystem],
          status_code=status.HTTP_201_CREATED)
def create_hydroponic_systems(hydroponic_systems: List[models.HydroponicSystem], db: Session = Depends(get_db),
                              api_key: str = Depends(get_api_key)):
    db_hydroponic_systems = [schema.HydroponicSystem(**hydroponic_system.dict()) for hydroponic_system in
                             hydroponic_systems]
    db.add_all(db_hydroponic_systems)
    db.commit()
    return db_hydroponic_systems


# READ all hydroponic_systems
@app.get("/hydroponic_systems/", response_model=List[models.HydroponicSystem])
def read_hydroponic_systems(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.HydroponicSystem).all()


# READ a single hydroponic_system by ID
@app.get("/hydroponic_systems/{system_id}", response_model=models.HydroponicSystem)
def read_hydroponic_system(system_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    hydroponic_system = db.query(schema.HydroponicSystem).filter(
        schema.HydroponicSystem.system_id == system_id).first()
    if hydroponic_system is None:
        raise HTTPException(status_code=404, detail="HydroponicSystem not found")
    return hydroponic_system


# UPDATE a hydroponic_system by ID
@app.put("/hydroponic_systems/{system_id}", response_model=models.HydroponicSystem)
def update_hydroponic_system(system_id: int, update_data: models.HydroponicSystem, db: Session = Depends(get_db),
                             api_key: str = Depends(get_api_key)):
    hydroponic_system = db.query(schema.HydroponicSystem).filter(
        schema.HydroponicSystem.system_id == system_id).first()
    if hydroponic_system is None:
        raise HTTPException(status_code=404, detail="HydroponicSystem not found")
    for key, value in update_data.dict().items():
        setattr(hydroponic_system, key, value)
    db.commit()
    return hydroponic_system


# DELETE a hydroponic_system by ID
@app.delete("/hydroponic_systems/{system_id}", response_model=models.HydroponicSystem)
def delete_hydroponic_system(system_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    hydroponic_system = db.query(schema.HydroponicSystem).filter(
        schema.HydroponicSystem.system_id == system_id).first()
    if hydroponic_system is None:
        raise HTTPException(status_code=404, detail="HydroponicSystem not found")
    db.delete(hydroponic_system)
    db.commit()
    return hydroponic_system


# CREATE a new seed
@app.post("/seeds/", response_model=models.Seed, status_code=status.HTTP_201_CREATED)
def create_seed(seed: models.Seed, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_seed = schema.Seed(**seed.dict())
    db.add(db_seed)
    db.commit()
    db.refresh(db_seed)
    return db_seed


# CREATE many new seeds
@app.post("/seeds/bulk", response_model=List[models.Seed], status_code=status.HTTP_201_CREATED)
def create_seeds(seeds: List[models.Seed], db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_seeds = [schema.Seed(**seed.dict()) for seed in seeds]
    db.add_all(db_seeds)
    db.commit()
    return db_seeds


# READ all seeds
@app.get("/seeds/", response_model=List[models.Seed])
def read_seeds(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.Seed).all()


# READ a single seed by ID
@app.get("/seeds/{seed_id}", response_model=models.Seed)
def read_seed(seed_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    seed = db.query(schema.Seed).filter(schema.Seed.seed_id == seed_id).first()
    if seed is None:
        raise HTTPException(status_code=404, detail="Seed not found")
    return seed


# UPDATE a seed by ID
@app.put("/seeds/{seed_id}", response_model=models.Seed)
def update_seed(seed_id: int, update_data: models.Seed, db: Session = Depends(get_db),
                api_key: str = Depends(get_api_key)):
    seed = db.query(schema.Seed).filter(schema.Seed.seed_id == seed_id).first()
    if seed is None:
        raise HTTPException(status_code=404, detail="Seed not found")
    for key, value in update_data.dict().items():
        setattr(seed, key, value)
    db.commit()
    return seed


# DELETE a seed by ID
@app.delete("/seeds/{seed_id}", response_model=models.Seed)
def delete_seed(seed_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    seed = db.query(schema.Seed).filter(schema.Seed.seed_id == seed_id).first()
    if seed is None:
        raise HTTPException(status_code=404, detail="Seed not found")
    db.delete(seed)
    db.commit()
    return seed


# CREATE a new seed_cross
@app.post("/seed_crosses/", response_model=models.SeedCross, status_code=status.HTTP_201_CREATED)
def create_seed_cross(seed_cross: models.SeedCross, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_seed_cross = schema.SeedCross(**seed_cross.dict())
    db.add(db_seed_cross)
    db.commit()
    db.refresh(db_seed_cross)
    return db_seed_cross


# CREATE many new seed_crosses
@app.post("/seed_crosses/bulk", response_model=List[models.SeedCross], status_code=status.HTTP_201_CREATED)
def create_seed_crosses(seed_crosses: List[models.SeedCross], db: Session = Depends(get_db),
                        api_key: str = Depends(get_api_key)):
    db_seed_crosses = [schema.SeedCross(**seed_cross.dict()) for seed_cross in seed_crosses]
    db.add_all(db_seed_crosses)
    db.commit()
    return db_seed_crosses


# READ all seed_crosses
@app.get("/seed_crosses/", response_model=List[models.SeedCross])
def read_seed_crosses(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(schema.SeedCross).all()


# READ a single seed_cross by ID
@app.get("/seed_crosses/{cross_id}", response_model=models.SeedCross)
def read_seed_cross(cross_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    seed_cross = db.query(schema.SeedCross).filter(schema.SeedCross.cross_id == cross_id).first()
    if seed_cross is None:
        raise HTTPException(status_code=404, detail="SeedCross not found")
    return seed_cross


# UPDATE a seed_cross by ID
@app.put("/seed_crosses/{cross_id}", response_model=models.SeedCross)
def update_seed_cross(cross_id: int, update_data: models.SeedCross, db: Session = Depends(get_db),
                      api_key: str = Depends(get_api_key)):
    seed_cross = db.query(schema.SeedCross).filter(schema.SeedCross.cross_id == cross_id).first()
    if seed_cross is None:
        raise HTTPException(status_code=404, detail="SeedCross not found")
    for key, value in update_data.dict().items():
        setattr(seed_cross, key, value)
    db.commit()
    return seed_cross


# DELETE a seed_cross by ID
@app.delete("/seed_crosses/{cross_id}", response_model=models.SeedCross)
def delete_seed_cross(cross_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    seed_cross = db.query(schema.SeedCross).filter(schema.SeedCross.cross_id == cross_id).first()
    if seed_cross is None:
        raise HTTPException(status_code=404, detail="SeedCross not found")
    db.delete(seed_cross)
    db.commit()
    return seed_cross


handler = Mangum(app)
