import psycopg2
from psycopg2.extras import DictCursor

def get_db_connection():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname="patient_nutrition_demo",
        user="postgres",  # Replace with your database username
        password="pass",
        host="localhost",  # or your database host
        port="5432"  # Default port for PostgreSQL
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
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    if food_name:
        cur.execute("SELECT * FROM nutrition_reference WHERE food_name = %s", (food_name,))
    else:
        cur.execute("SELECT * FROM nutrition_reference")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in results]

def get_food_transactions(patient_id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    if patient_id:
        cur.execute("SELECT * FROM food_transactions WHERE patient_id = %s", (patient_id,))
    else:
        cur.execute("SELECT * FROM food_transactions")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in results]

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