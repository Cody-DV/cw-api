-- ======================
-- Insert Patients (6 total)
-- ======================
INSERT INTO patients (first_name, last_name, date_of_birth, gender, height_cm, weight_kg)
VALUES
    -- 1
    ('John',  'Doe',     '1980-01-15', 'Male',   175.5, 80.2),
    -- 2
    ('Jane',  'Smith',   '1990-06-20', 'Female', 165.0, 65.0),
    -- 3
    ('Bob',   'Anderson','1975-11-05', 'Male',   180.0, 78.5),
    -- 4
    ('Emily', 'Johnson', '1988-03-12', 'Female', 170.2, 68.0),
    -- 5
    ('Sarah', 'Wilson',  '1995-09-27', 'Female', 162.0, 60.0),
    -- 6
    ('Michael','Brown',  '1982-12-01', 'Male',   183.0, 85.0);

-- ======================
-- Insert Allergies (6 total)
-- ======================
INSERT INTO allergies (patient_id, allergen, severity)
VALUES
    (1, 'Peanuts',    'Severe'),
    (1, 'Shellfish',  'Moderate'),
    (2, 'Gluten',     'Mild'),
    (3, 'Eggs',       'Mild'),
    (4, 'Dairy',      'Moderate'),
    (5, 'Peanuts',    'Severe');

-- ======================
-- Insert Nutrition References (12 total)
-- ======================
INSERT INTO nutrition_reference (
    food_name,
    calories,
    protein_g,
    fat_g,
    carbs_g,
    fiber_g,
    sodium_mg,
    additional_nutrients_json
)
VALUES
    ( 'Apple, raw',                 52,   0.26, 0.17, 14,   2.4,   1,  '{"vitaminC": "4.6mg"}' ),
    ( 'Chicken Breast, roasted',   165,  31.00, 3.60,  0,   0.0,  74,  '{"vitaminB6": "0.6mg"}' ),
    ( 'Rice, white, cooked',       130,   2.70, 0.30, 28,   0.4,   1,  '{"iron": "1.2mg"}' ),
    ( 'Broccoli, raw',             34,   2.80, 0.40,  7,   2.6,  33,  '{"vitaminC": "89.2mg", "vitaminK": "101.6mcg"}' ),
    ( 'Salmon, grilled',           208,  22.10, 12.35, 0,   0.0,  59,  '{"omega3": "1.5g"}' ),
    ( 'Oatmeal, cooked',           158,   5.50, 2.80, 27,   4.0,   2,  '{"iron": "1.5mg"}' ),
    ( 'Yogurt, plain',             59,    10.00, 0.40, 3.6, 0.0,  36,  '{"calcium": "110mg"}' ),
    ( 'Almonds, raw',              579,  21.15, 49.93, 22,  12.5, 1,   '{"vitaminE": "25.6mg"}' ),
    ( 'Banana, raw',               89,    1.09, 0.33, 23,   2.6,   1,  '{"potassium": "358mg"}' ),
    ( 'Spinach, raw',              23,    2.90, 0.40,  3.6, 2.2,   79, '{"vitaminA": "469mcg"}' ),
    ( 'Beef, ground, cooked',      250,  26.00, 15.00, 0,   0.0,   72, '{"iron": "2.6mg"}' ),
    ( 'Potato, baked',             93,    2.50, 0.13, 21,   2.2,    7, '{"vitaminC": "9.0mg"}' );

-- ======================
-- Insert Food Transactions (18 total, 3 per patient)
-- ======================
-- Patient 1
INSERT INTO food_transactions (patient_id, nutrition_ref_id, servings, consumption_date) VALUES
    (1, 1,  2,   '2025-02-01'),  -- 2 servings of Apple
    (1, 2,  1,   '2025-02-01'),  -- 1 serving of Chicken Breast
    (1, 3,  0.5, '2025-02-02');  -- 0.5 servings of Rice

-- Patient 2
INSERT INTO food_transactions (patient_id, nutrition_ref_id, servings, consumption_date) VALUES
    (2, 4,  1,   '2025-02-01'),  -- 1 serving of Broccoli
    (2, 5,  1,   '2025-02-02'),  -- 1 serving of Salmon
    (2, 6,  1,   '2025-02-02');  -- 1 serving of Oatmeal

-- Patient 3
INSERT INTO food_transactions (patient_id, nutrition_ref_id, servings, consumption_date) VALUES
    (3, 7,  1,   '2025-02-01'),  -- 1 serving of Yogurt
    (3, 8,  0.5, '2025-02-01'),  -- 0.5 servings of Almonds
    (3, 9,  2,   '2025-02-02');  -- 2 servings of Banana

-- Patient 4
INSERT INTO food_transactions (patient_id, nutrition_ref_id, servings, consumption_date) VALUES
    (4, 3,  1,   '2025-02-01'),  -- 1 serving of Rice
    (4, 4,  1,   '2025-02-02'),  -- 1 serving of Broccoli
    (4, 11, 1.5, '2025-02-02');  -- 1.5 servings of Beef

-- Patient 5
INSERT INTO food_transactions (patient_id, nutrition_ref_id, servings, consumption_date) VALUES
    (5, 2,  1,   '2025-02-01'),  -- 1 serving of Chicken Breast
    (5, 10, 1,   '2025-02-02'),  -- 1 serving of Spinach
    (5, 12, 2,   '2025-02-02');  -- 2 servings of Baked Potato

-- Patient 6
INSERT INTO food_transactions (patient_id, nutrition_ref_id, servings, consumption_date) VALUES
    (6, 8,  1,   '2025-02-01'),  -- 1 serving of Almonds
    (6, 11, 1,   '2025-02-01'),  -- 1 serving of Beef
    (6, 1,  1,   '2025-02-02');  -- 1 serving of Apple

-- ======================
-- Insert Nutrient Targets (6 total, one for each patient)
-- ======================
INSERT INTO nutrient_targets (
    patient_id,
    calories_target,
    protein_target,
    fat_target,
    carbs_target,
    fiber_target,
    sodium_target,
    additional_targets_json
)
VALUES
    -- Patient 1
    (1, 2000,  60,  70, 250, 25, 2300, '{"vitaminC":"75mg"}'),
    -- Patient 2
    (2, 1800,  50,  60, 200, 20, 2200, '{"vitaminC":"60mg"}'),
    -- Patient 3
    (3, 2200,  70,  80, 300, 30, 2400, '{"vitaminD":"15mcg"}'),
    -- Patient 4
    (4, 1900,  55,  65, 230, 25, 2100, '{"iron":"18mg"}'),
    -- Patient 5
    (5, 2100,  65,  70, 260, 28, 2300, '{"calcium":"1000mg"}'),
    -- Patient 6
    (6, 1800,  55,  60, 220, 25, 2000, '{"vitaminB12":"2.4mcg"}');

-- Optional: Confirmation
SELECT 'Expanded simulated data inserted successfully!' AS info;
