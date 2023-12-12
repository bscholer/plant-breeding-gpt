import logging
import os
from typing import List, Union

import sqlparse
from databases import Database
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header
from mangum import Mangum
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from starlette import status

import models
import schema

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()
print('loaded dotenv')

DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:" \
               f"{os.getenv('DB_PASSWORD')}@" \
               f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

metadata = MetaData()

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

database = Database(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print('created sessionmaker')

apiGatewayEndpoint = "https://0ybnxa9zak.execute-api.us-east-2.amazonaws.com"

app = FastAPI(servers=[{"url": apiGatewayEndpoint, "description": "AWS API Gateway"}], title="Plant Database API")


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


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Hello World"}


def get_api_key(api_key: str = Header(...)):
    if api_key != os.getenv('API_KEY'):
        raise HTTPException(status_code=400, detail="Invalid API Key")
    return api_key


def has_subquery(parsed_query):
    for token in parsed_query.tokens:
        if isinstance(token, sqlparse.sql.Parenthesis):
            subquery = token.get_real_name()
            if subquery.strip().lower().startswith("select"):
                return True
    return False


def is_select_only_subquery(subquery):
    for token in subquery.tokens:
        if isinstance(token, sqlparse.sql.Token) and token.value.lower() not in (
                "select", "from", "where", "join", "left", "right", "inner", "outer"):
            return False
    return True


@app.post("/run_select_query/", openapi_extra={"x-openai-isConsequential": False}, operation_id="runSelectQuery")
async def run_select_query(query: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    # Parse the SQL query to check if it's a SELECT statement
    parsed_query = sqlparse.parse(query)

    # Check that the first token is a SELECT keyword
    if not parsed_query:
        raise HTTPException(status_code=400, detail="Invalid SQL query.")

    first_token = parsed_query[0].tokens[0].value.lower()
    if first_token != "select":
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed.")

    # Check for subqueries in the parsed query
    if has_subquery(parsed_query[0]):
        for subquery in parsed_query[0].get_sublists():
            if not is_select_only_subquery(subquery):
                raise HTTPException(status_code=400, detail="Subqueries must be SELECT-only.")

    # Execute the query safely
    try:
        result = db.execute(query).fetchall()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# READ seeds
@app.get("/seeds/{seed_id}", response_model=Union[List[models.Seed], models.Seed],
         openapi_extra={"x-openai-isConsequential": False},
         description="Returns a list of seeds if no seed_id (or 0) is specified, otherwise returns a single seed.",
         operation_id="readSeed")
def read_seed(seed_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not seed_id:
        return db.query(schema.Seed).all()
    else:
        seed = db.query(schema.Seed).filter(schema.Seed.seed_id == seed_id).first()
        if seed is None:
            raise HTTPException(status_code=404, detail="Seed not found")
        return seed


# INSERT/UPDATE a new seed
@app.post("/seeds/", response_model=models.Seed, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertSeed")
def upsert_seed(seed: models.Seed, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_seed = db.query(schema.Seed).filter(schema.Seed.seed_id == seed.seed_id).first()
    if db_seed is None:
        db_seed = schema.Seed(**seed.dict())
        db.add(db_seed)
        db.commit()
        db.refresh(db_seed)
        return db_seed
    else:
        for key, value in seed.dict().items():
            setattr(db_seed, key, value)
        db.commit()
        return db_seed


# DELETE a seed by ID
@app.delete("/seeds/{seed_id}", response_model=models.Seed, openapi_extra={"x-openai-isConsequential": True},
            operation_id="deleteSeed")
def delete_seed(seed_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    seed = db.query(schema.Seed).filter(schema.Seed.seed_id == seed_id).first()
    if seed is None:
        raise HTTPException(status_code=404, detail="Seed not found")
    db.delete(seed)
    db.commit()
    return seed


# READ germinations
@app.get("/germinations/{germination_id}", response_model=Union[List[models.Germination], models.Germination],
         description="Returns all germinations if no germination_id (or 0) is specified, otherwise returns a single germination",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readGermination")
def read_germination(germination_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not germination_id:
        return db.query(schema.Germination).all()
    else:
        germination = db.query(schema.Germination).filter(
            schema.Germination.germination_id == germination_id).first()
        if germination is None:
            raise HTTPException(status_code=404, detail="Germination not found")
        return germination


# INSERT/UPDATE a new germination
@app.post("/germinations/", response_model=models.Germination, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertGermination")
def upsert_germination(germination: models.Germination, db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    db_germination = db.query(schema.Germination).filter(
        schema.Germination.germination_id == germination.germination_id).first()
    if db_germination is None:
        db_germination = schema.Germination(**germination.dict())
        db.add(db_germination)
        db.commit()
        db.refresh(db_germination)
        return db_germination
    else:
        for key, value in germination.dict().items():
            setattr(db_germination, key, value)
        db.commit()
        return db_germination


# DELETE a germination by ID
@app.delete("/germinations/{germination_id}", response_model=models.Germination,
            openapi_extra={"x-openai-isConsequential": True}, operation_id="deleteGermination")
def delete_germination(germination_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    germination = db.query(schema.Germination).filter(schema.Germination.germination_id == germination_id).first()
    if germination is None:
        raise HTTPException(status_code=404, detail="Germination not found")
    db.delete(germination)
    db.commit()
    return germination


# READ plants
@app.get("/plants/{plant_id}", response_model=Union[List[models.Plant], models.Plant],
         description="Returns all plants if no plant_id (or 0) is specified, otherwise returns a single plant",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readPlant")
def read_plant(plant_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not plant_id:
        return db.query(schema.Plant).all()
    else:
        plant = db.query(schema.Plant).filter(schema.Plant.plant_id == plant_id).first()
        if plant is None:
            raise HTTPException(status_code=404, detail="Plant not found")
        return plant


# INSERT/UPDATE a new plant
@app.post("/plants/", response_model=models.Plant, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertPlant")
def upsert_plant(plant: models.Plant, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_plant = db.query(schema.Plant).filter(schema.Plant.plant_id == plant.plant_id).first()
    if db_plant is None:
        db_plant = schema.Plant(**plant.dict())
        db.add(db_plant)
        db.commit()
        db.refresh(db_plant)
        return db_plant
    else:
        for key, value in plant.dict().items():
            setattr(db_plant, key, value)
        db.commit()
        return db_plant


# DELETE a plant by ID
@app.delete("/plants/{plant_id}", response_model=models.Plant, openapi_extra={"x-openai-isConsequential": True},
            operation_id="deletePlant")
def delete_plant(plant_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    plant = db.query(schema.Plant).filter(schema.Plant.plant_id == plant_id).first()
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(plant)
    db.commit()
    return plant


# READ yields
@app.get("/yields/{yield_id}", response_model=Union[List[models.Yield], models.Yield],
         description="Returns all yields if no yield_id (or 0) is specified, otherwise returns a single yield",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readYield")
def read_yield(yield_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not yield_id:
        return db.query(schema.Yield).all()
    else:
        yield_ = db.query(schema.Yield).filter(schema.Yield.yield_id == yield_id).first()
        if yield_ is None:
            raise HTTPException(status_code=404, detail="Yield not found")
        return yield_


# INSERT/UPDATE a new yield
@app.post("/yields/", response_model=models.Yield, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertYield")
def upsert_yield(yield_: models.Yield, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_yield = db.query(schema.Yield).filter(schema.Yield.yield_id == yield_.yield_id).first()
    if db_yield is None:
        db_yield = schema.Yield(**yield_.dict())
        db.add(db_yield)
        db.commit()
        db.refresh(db_yield)
        return db_yield
    else:
        for key, value in yield_.dict().items():
            setattr(db_yield, key, value)
        db.commit()
        return db_yield


# DELETE a yield by ID
@app.delete("/yields/{yield_id}", response_model=models.Yield, openapi_extra={"x-openai-isConsequential": True},
            operation_id="deleteYield")
def delete_yield(yield_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    yield_ = db.query(schema.Yield).filter(schema.Yield.yield_id == yield_id).first()
    if yield_ is None:
        raise HTTPException(status_code=404, detail="Yield not found")
    db.delete(yield_)
    db.commit()
    return yield_


# READ plant_crosses
@app.get("/plant_crosses/{cross_id}", response_model=Union[List[models.PlantCross], models.PlantCross],
         description="Returns all plant_crosses if no cross_id (or 0) is specified, otherwise returns a single plant_cross",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readPlantCross")
def read_plant_cross(cross_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not cross_id:
        return db.query(schema.PlantCross).all()
    else:
        plant_cross = db.query(schema.PlantCross).filter(schema.PlantCross.cross_id == cross_id).first()
        if plant_cross is None:
            raise HTTPException(status_code=404, detail="PlantCross not found")
        return plant_cross


# INSERT/UPDATE a new plant_cross
@app.post("/plant_crosses/", response_model=models.PlantCross, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertPlantCross")
def upsert_plant_cross(plant_cross: models.PlantCross, db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    db_plant_cross = db.query(schema.PlantCross).filter(schema.PlantCross.cross_id == plant_cross.cross_id).first()
    if db_plant_cross is None:
        db_plant_cross = schema.PlantCross(**plant_cross.dict())
        db.add(db_plant_cross)
        db.commit()
        db.refresh(db_plant_cross)
        return db_plant_cross
    else:
        for key, value in plant_cross.dict().items():
            setattr(db_plant_cross, key, value)
        db.commit()
        return db_plant_cross


# DELETE a plant_cross by ID
@app.delete("/plant_crosses/{cross_id}", response_model=models.PlantCross,
            openapi_extra={"x-openai-isConsequential": True}, operation_id="deletePlantCross")
def delete_plant_cross(cross_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    plant_cross = db.query(schema.PlantCross).filter(schema.PlantCross.cross_id == cross_id).first()
    if plant_cross is None:
        raise HTTPException(status_code=404, detail="PlantCross not found")
    db.delete(plant_cross)
    db.commit()
    return plant_cross


# READ plant_plant_crosses
@app.get("/plant_plant_crosses/{id}", response_model=Union[List[models.PlantPlantCross], models.PlantPlantCross],
         description="Returns all plant_plant_crosses if no id (or 0) is specified, otherwise returns a single plant_plant_cross",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readPlantPlantCross")
def read_plant_plant_cross(id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not id:
        return db.query(schema.PlantPlantCross).all()
    else:
        plant_plant_cross = db.query(schema.PlantPlantCross).filter(schema.PlantPlantCross.id == id).first()
        if plant_plant_cross is None:
            raise HTTPException(status_code=404, detail="PlantPlantCross not found")
        return plant_plant_cross


# INSERT/UPDATE a new plant_plant_cross
@app.post("/plant_plant_crosses/", response_model=models.PlantPlantCross, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertPlantPlantCross")
def upsert_plant_plant_cross(plant_plant_cross: models.PlantPlantCross, db: Session = Depends(get_db),
                             api_key: str = Depends(get_api_key)):
    db_plant_plant_cross = db.query(schema.PlantPlantCross).filter(
        schema.PlantPlantCross.id == plant_plant_cross.id).first()
    if db_plant_plant_cross is None:
        db_plant_plant_cross = schema.PlantPlantCross(**plant_plant_cross.dict())
        db.add(db_plant_plant_cross)
        db.commit()
        db.refresh(db_plant_plant_cross)
        return db_plant_plant_cross
    else:
        for key, value in plant_plant_cross.dict().items():
            setattr(db_plant_plant_cross, key, value)
        db.commit()
        return db_plant_plant_cross


# DELETE a plant_plant_cross by ID
@app.delete("/plant_plant_crosses/{id}", response_model=models.PlantPlantCross,
            openapi_extra={"x-openai-isConsequential": True}, operation_id="deletePlantPlantCross")
def delete_plant_plant_cross(id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    plant_plant_cross = db.query(schema.PlantPlantCross).filter(schema.PlantPlantCross.id == id).first()
    if plant_plant_cross is None:
        raise HTTPException(status_code=404, detail="PlantPlantCross not found")
    db.delete(plant_plant_cross)
    db.commit()
    return plant_plant_cross


# READ taste_tests
@app.get("/taste_tests/{taste_test_id}", response_model=Union[List[models.TasteTest], models.TasteTest],
         description="Returns all taste_tests if no taste_test_id (or 0) is specified, otherwise returns a single taste_test",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readTasteTest")
def read_taste_test(taste_test_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not taste_test_id:
        return db.query(schema.TasteTest).all()
    else:
        taste_test = db.query(schema.TasteTest).filter(schema.TasteTest.taste_test_id == taste_test_id).first()
        if taste_test is None:
            raise HTTPException(status_code=404, detail="TasteTest not found")
        return taste_test


# INSERT/UPDATE a new taste_test
@app.post("/taste_tests/", response_model=models.TasteTest, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertTasteTest")
def upsert_taste_test(taste_test: models.TasteTest, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_taste_test = db.query(schema.TasteTest).filter(
        schema.TasteTest.taste_test_id == taste_test.taste_test_id).first()
    if db_taste_test is None:
        db_taste_test = schema.TasteTest(**taste_test.dict())
        db.add(db_taste_test)
        db.commit()
        db.refresh(db_taste_test)
        return db_taste_test
    else:
        for key, value in taste_test.dict().items():
            setattr(db_taste_test, key, value)
        db.commit()
        return db_taste_test


# Commented out to save space for the select query endpoint (30 endpoints is the limit)
# DELETE a taste_test by ID
# @app.delete("/taste_tests/{taste_test_id}", response_model=models.TasteTest,
#             openapi_extra={"x-openai-isConsequential": True}, operation_id="deleteTasteTest")
# def delete_taste_test(taste_test_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
#     taste_test = db.query(schema.TasteTest).filter(schema.TasteTest.taste_test_id == taste_test_id).first()
#     if taste_test is None:
#         raise HTTPException(status_code=404, detail="TasteTest not found")
#     db.delete(taste_test)
#     db.commit()
#     return taste_test


# READ observations
@app.get("/observations/{observation_id}", response_model=Union[List[models.Observation], models.Observation],
         description="Returns all observations if no observation_id (or 0) is specified, otherwise returns a single observation",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readObservation")
def read_observation(observation_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not observation_id:
        return db.query(schema.Observation).all()
    else:
        observation = db.query(schema.Observation).filter(
            schema.Observation.observation_id == observation_id).first()
        if observation is None:
            raise HTTPException(status_code=404, detail="Observation not found")
        return observation


# INSERT/UPDATE a new observation
@app.post("/observations/", response_model=models.Observation, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertObservation")
def upsert_observation(observation: models.Observation, db: Session = Depends(get_db),
                       api_key: str = Depends(get_api_key)):
    db_observation = db.query(schema.Observation).filter(
        schema.Observation.observation_id == observation.observation_id).first()
    if db_observation is None:
        db_observation = schema.Observation(**observation.dict())
        db.add(db_observation)
        db.commit()
        db.refresh(db_observation)
        return db_observation
    else:
        for key, value in observation.dict().items():
            setattr(db_observation, key, value)
        db.commit()
        return db_observation


# DELETE an observation by ID
@app.delete("/observations/{observation_id}", response_model=models.Observation,
            openapi_extra={"x-openai-isConsequential": True}, operation_id="deleteObservation")
def delete_observation(observation_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    observation = db.query(schema.Observation).filter(schema.Observation.observation_id == observation_id).first()
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    db.delete(observation)
    db.commit()
    return observation


# READ hydroponic_systems
@app.get("/hydroponic_systems/{system_id}",
         response_model=Union[List[models.HydroponicSystem], models.HydroponicSystem],
         description="Returns all hydroponic_systems if no system_id (or 0) is specified, otherwise returns a single hydroponic_system",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readHydroponicSystem")
def read_hydroponic_system(system_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not system_id:
        return db.query(schema.HydroponicSystem).all()
    else:
        hydroponic_system = db.query(schema.HydroponicSystem).filter(
            schema.HydroponicSystem.system_id == system_id).first()
        if hydroponic_system is None:
            raise HTTPException(status_code=404, detail="HydroponicSystem not found")
        return hydroponic_system


# INSERT/UPDATE a new hydroponic_system
@app.post("/hydroponic_systems/", response_model=models.HydroponicSystem, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertHydroponicSystem")
def upsert_hydroponic_system(hydroponic_system: models.HydroponicSystem, db: Session = Depends(get_db),
                             api_key: str = Depends(get_api_key)):
    db_hydroponic_system = db.query(schema.HydroponicSystem).filter(
        schema.HydroponicSystem.system_id == hydroponic_system.system_id).first()
    if db_hydroponic_system is None:
        db_hydroponic_system = schema.HydroponicSystem(**hydroponic_system.dict())
        db.add(db_hydroponic_system)
        db.commit()
        db.refresh(db_hydroponic_system)
        return db_hydroponic_system
    else:
        for key, value in hydroponic_system.dict().items():
            setattr(db_hydroponic_system, key, value)
        db.commit()
        return db_hydroponic_system


# DELETE a hydroponic_system by ID
@app.delete("/hydroponic_systems/{system_id}", response_model=models.HydroponicSystem,
            openapi_extra={"x-openai-isConsequential": True}, operation_id="deleteHydroponicSystem")
def delete_hydroponic_system(system_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    hydroponic_system = db.query(schema.HydroponicSystem).filter(
        schema.HydroponicSystem.system_id == system_id).first()
    if hydroponic_system is None:
        raise HTTPException(status_code=404, detail="HydroponicSystem not found")
    db.delete(hydroponic_system)
    db.commit()
    return hydroponic_system


# READ hydroponic_conditions
@app.get("/hydroponic_conditions/{condition_id}",
         response_model=Union[List[models.HydroponicCondition], models.HydroponicCondition],
         description="Returns all hydroponic_conditions if no condition_id (or 0) is specified, otherwise returns a single hydroponic_condition",
         openapi_extra={"x-openai-isConsequential": False}, operation_id="readHydroponicCondition")
def read_hydroponic_condition(condition_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if not condition_id:
        return db.query(schema.HydroponicCondition).all()
    else:
        hydroponic_condition = db.query(schema.HydroponicCondition).filter(
            schema.HydroponicCondition.condition_id == condition_id).first()
        if hydroponic_condition is None:
            raise HTTPException(status_code=404, detail="HydroponicCondition not found")
        return hydroponic_condition


# INSERT/UPDATE a new hydroponic_condition
@app.post("/hydroponic_conditions/", response_model=models.HydroponicCondition, status_code=status.HTTP_201_CREATED,
          openapi_extra={"x-openai-isConsequential": True}, operation_id="upsertHydroponicCondition")
def upsert_hydroponic_condition(hydroponic_condition: models.HydroponicCondition, db: Session = Depends(get_db),
                                api_key: str = Depends(get_api_key)):
    db_hydroponic_condition = db.query(schema.HydroponicCondition).filter(
        schema.HydroponicCondition.condition_id == hydroponic_condition.condition_id).first()
    if db_hydroponic_condition is None:
        db_hydroponic_condition = schema.HydroponicCondition(**hydroponic_condition.dict())
        db.add(db_hydroponic_condition)
        db.commit()
        db.refresh(db_hydroponic_condition)
        return db_hydroponic_condition
    else:
        for key, value in hydroponic_condition.dict().items():
            setattr(db_hydroponic_condition, key, value)
        db.commit()
        return db_hydroponic_condition


# DELETE a hydroponic_condition by ID
@app.delete("/hydroponic_conditions/{condition_id}", response_model=models.HydroponicCondition,
            openapi_extra={"x-openai-isConsequential": True}, operation_id="deleteHydroponicCondition")
def delete_hydroponic_condition(condition_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    hydroponic_condition = db.query(schema.HydroponicCondition).filter(
        schema.HydroponicCondition.condition_id == condition_id).first()
    if hydroponic_condition is None:
        raise HTTPException(status_code=404, detail="HydroponicCondition not found")
    db.delete(hydroponic_condition)
    db.commit()
    return hydroponic_condition


handler = Mangum(app)
