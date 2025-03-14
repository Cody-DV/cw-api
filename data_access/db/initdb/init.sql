-- 1. Create the database
CREATE DATABASE patient_nutrition_demo;

-- 2. Connect to the new database
\connect patient_nutrition_demo;

-- 3. Create tables

-- Patients Table
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    height_cm DECIMAL(5, 2),
    weight_kg DECIMAL(5, 2),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Allergies Table
CREATE TABLE allergies (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    allergen VARCHAR(100) NOT NULL,
    severity VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_patient
        FOREIGN KEY(patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE
);

-- Nutrition Reference Table
CREATE TABLE nutrition_reference (
    id SERIAL PRIMARY KEY,
    food_name VARCHAR(255) NOT NULL,
    calories DECIMAL(6,2),
    protein_g DECIMAL(6,2),
    fat_g DECIMAL(6,2),
    carbs_g DECIMAL(6,2),
    fiber_g DECIMAL(6,2),
    sodium_mg DECIMAL(6,2),
    additional_nutrients_json JSONB
);

-- Food Transactions Table
CREATE TABLE food_transactions (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    nutrition_ref_id INT NOT NULL,
    servings DECIMAL(4,2) NOT NULL,
    consumption_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_ft_patient
        FOREIGN KEY(patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ft_nutrition_ref
        FOREIGN KEY(nutrition_ref_id)
        REFERENCES nutrition_reference(id)
        ON DELETE CASCADE
);

-- Nutrient Targets Table (Optional, if you store daily recommended intakes by patient)
CREATE TABLE nutrient_targets (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL,
    calories_target DECIMAL(6,2),
    protein_target DECIMAL(6,2),
    fat_target DECIMAL(6,2),
    carbs_target DECIMAL(6,2),
    fiber_target DECIMAL(6,2),
    sodium_target DECIMAL(6,2),
    additional_targets_json JSONB,
    CONSTRAINT fk_nt_patient
        FOREIGN KEY(patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE
);


SELECT 'Database and tables created successfully!' AS info;
