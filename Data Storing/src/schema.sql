CREATE DATABASE IF NOT EXISTS MobileLegends
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE MobileLegends;

DROP TABLE IF EXISTS Hero_Price;
DROP TABLE IF EXISTS Hero_Lane_Recommendation;
DROP TABLE IF EXISTS Hero_Specialty;
DROP TABLE IF EXISTS Hero_Role;
DROP TABLE IF EXISTS Statistics;
DROP TABLE IF EXISTS Hero;

CREATE TABLE Hero (
    hero_order          INT PRIMARY KEY NOT NULL,
    hero_name           VARCHAR(50) NOT NULL,
    hero_alias          VARCHAR(50),
    region_of_origin    VARCHAR(50),
    release_date        DATE
);

CREATE TABLE Hero_Role (
    hero_order          INT NOT NULL,
    role                VARCHAR(50) NOT NULL,
    PRIMARY KEY (hero_order, role),
    CONSTRAINT role_hero
        FOREIGN KEY (hero_order) REFERENCES Hero(hero_order)
        ON DELETE CASCADE ON UPDATE CASCADE
    -- FOREIGN KEY hero_order REFERENCES Hero ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Hero_Specialty (
    hero_order          INT NOT NULL,
    specialty           VARCHAR(50) NOT NULL,
    PRIMARY KEY (hero_order, specialty),
    CONSTRAINT specialty_hero
        FOREIGN KEY (hero_order) REFERENCES Hero(hero_order)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Hero_Lane_Recommendation (
    hero_order          INT NOT NULL,
    lane_recommendation VARCHAR(50) NOT NULL,
    PRIMARY KEY (hero_order, lane_recommendation),
    CONSTRAINT lane_hero
        FOREIGN KEY (hero_order) REFERENCES Hero(hero_order)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Hero_Price (
    hero_order          INT NOT NULL,
    currency            VARCHAR(50) NOT NULL,
    amount              INT,
    PRIMARY KEY (hero_order, currency, amount),
    CONSTRAINT price_hero
        FOREIGN KEY (hero_order) REFERENCES Hero(hero_order)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Statistics (
    hero_order              INT PRIMARY KEY NOT NULL,
    base_hp                 INT,
    hp_growth               FLOAT,
    base_mana               INT,
    mana_growth             FLOAT,
    base_mana_regen         FLOAT,
    mana_regen_growth       FLOAT,
    base_physical_attack    FLOAT,
    physical_attack_growth  FLOAT,
    base_magic_power        FLOAT,
    magic_power_growth      FLOAT,
    base_physical_defense   FLOAT,
    physical_defense_growth FLOAT,
    base_magic_defense      FLOAT,
    magic_defense_growth    FLOAT,
    base_attack_speed       FLOAT,
    attack_speed_growth     FLOAT,
    attack_speed_ratio      FLOAT,
    critical_damage         FLOAT,
    movement_speed          INT,
    basic_attack_range      FLOAT,
    CONSTRAINT statistics_hero
        FOREIGN KEY (hero_order) REFERENCES Hero(hero_order)
        ON DELETE CASCADE ON UPDATE CASCADE
);

