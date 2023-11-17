-- DDL for Plant Crosses
CREATE TABLE plant_crosses
(
    cross_id    INT AUTO_INCREMENT PRIMARY KEY,
    parent_1_id INT,
    parent_2_id INT,
    cross_date  DATE,
    method      VARCHAR(255),
    comments    TEXT
);

-- DDL for Hydroponic Conditions
CREATE TABLE hydroponic_conditions
(
    condition_id            INT AUTO_INCREMENT PRIMARY KEY,
    system_id               INT,
    date                    DATE,
    water_ph                DECIMAL(3, 2),
    electrical_conductivity DECIMAL(5, 2),
    water_temperature_f     INT,
    tds                     DECIMAL(5, 2),
    comments                TEXT
);

-- DDL for Taste Test
CREATE TABLE taste_test
(
    taste_test_id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id      INT,
    date          DATE,
    taste         VARCHAR(255),
    texture       VARCHAR(255),
    appearance    VARCHAR(255),
    overall       INT,
    comments      TEXT
);

-- DDL for Yield
CREATE TABLE yield
(
    yield_id       INT AUTO_INCREMENT PRIMARY KEY,
    plant_id       INT,
    date           DATE,
    height_cm      DECIMAL(5, 2),
    leaf_count     INT,
    color          VARCHAR(255),
    texture        VARCHAR(255),
    nutrient_level INT,
    photo          BLOB,
    notes          TEXT
);

-- DDL for Observations
CREATE TABLE observations
(
    observation_id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id       INT,
    date           DATE,
    comments       TEXT
);
CREATE TABLE plants
(
    plant_id             INT AUTO_INCREMENT PRIMARY KEY,
    seed_id              INT,                         -- New column to reference the seeds table
    plant_type           VARCHAR(255),
    species              VARCHAR(255),
    variety              VARCHAR(255),
    germination_date     DATE,
    hydroponic_system_id INT,
    comments             TEXT
);


-- DDL for Hydroponic System
CREATE TABLE hydroponic_system
(
    system_id   INT AUTO_INCREMENT PRIMARY KEY,
    system_type VARCHAR(255),
    comments    TEXT
);

CREATE TABLE seeds
(
    seed_id         INT AUTO_INCREMENT PRIMARY KEY,
    number_of_seeds INT,
    cross_id        INT, -- This can be NULL if seeds do not come from a cross
    comments        TEXT,
    FOREIGN KEY (cross_id) REFERENCES plant_crosses (cross_id)
);

ALTER TABLE plant_crosses ADD FOREIGN KEY (parent_1_id) REFERENCES plants(plant_id);
ALTER TABLE plant_crosses ADD FOREIGN KEY (parent_2_id) REFERENCES plants(plant_id);

ALTER TABLE hydroponic_conditions ADD FOREIGN KEY (system_id) REFERENCES hydroponic_system(system_id);

ALTER TABLE taste_test ADD FOREIGN KEY (plant_id) REFERENCES plants(plant_id);

ALTER TABLE yield ADD FOREIGN KEY (plant_id) REFERENCES plants(plant_id);

ALTER TABLE observations ADD FOREIGN KEY (plant_id) REFERENCES plants(plant_id);

ALTER TABLE seeds ADD FOREIGN KEY (cross_id) REFERENCES plant_crosses(cross_id);

ALTER TABLE plants ADD FOREIGN KEY (seed_id) REFERENCES seeds(seed_id);
ALTER TABLE plants ADD FOREIGN KEY (hydroponic_system_id) REFERENCES hydroponic_system(system_id);
