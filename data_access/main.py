import psycopg2
from psycopg2.extras import DictCursor

import os
import logging


def get_db_connection():
    # Connect to the PostgreSQL database
    # Get host from environment variable or default to localhost for local development
    db_host = os.environ.get("DB_HOST", "postgres")
    
    conn = psycopg2.connect(
        dbname="patient_nutrition_demo",
        user="postgres",
        password="pass",
        host=db_host,  # Use Docker service name in container, localhost outside
        port="5432"
    )
    return conn


def get_patients(patient_id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    if patient_id:
        cur.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    else:
        cur.execute("SELECT * FROM patients")
    patients = cur.fetchall()

    # Log the number of patients retrieved
    logging.info(f"Retrieved {len(patients)} patients from the database")

    # Log a sample patient if available
    if patients:
        logging.info(f"Sample patient data: {dict(patients[0])}")
    else:
        logging.warning("No patients found in the database!")

    cur.close()
    conn.close()
    return [dict(row) for row in patients]

def get_allergies(patient_id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    if patient_id:
        cur.execute("SELECT * FROM allergies WHERE patient_id = %s", (patient_id,))
    else:
        cur.execute("SELECT * FROM allergies")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in results]

def get_nutrition_reference(food_name=None):
    import logging
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    if food_name:
        cur.execute("SELECT * FROM nutrition_reference WHERE food_name = %s", (food_name,))
    else:
        cur.execute("SELECT * FROM nutrition_reference")
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert to dictionaries and log sample
    result_list = [dict(row) for row in results]
    if result_list:
        logging.info(f"Retrieved {len(result_list)} nutrition references")
        logging.info(f"Sample nutrition reference: {result_list[0]}")
    else:
        logging.warning("No nutrition references found in database!")
        
    return result_list

def get_food_transactions(patient_id=None):
    import logging
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    if patient_id:
        cur.execute("SELECT * FROM food_transactions WHERE patient_id = %s", (patient_id,))
        logging.info(f"Querying food transactions for patient_id: {patient_id}")
    else:
        cur.execute("SELECT * FROM food_transactions")
        logging.info("Querying all food transactions")
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convert to dictionaries and log
    result_list = [dict(row) for row in results]
    logging.info(f"Retrieved {len(result_list)} food transactions")
    if result_list:
        logging.info(f"Sample food transaction: {result_list[0]}")
    
    return result_list

def get_nutrient_targets(patient_id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    if patient_id:
        cur.execute("SELECT * FROM nutrient_targets WHERE patient_id = %s", (patient_id,))
    else:
        cur.execute("SELECT * FROM nutrient_targets")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in results]