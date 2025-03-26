#!/usr/bin/env python3
"""
Script to verify database connectivity and check if tables were properly created
and populated with sample data.
"""
import os
import sys
from main import get_db_connection
import psycopg2

def check_connection():
    print("Checking database connection...")
    try:
        conn = get_db_connection()
        print("Successfully connected to database")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Failed to connect to database: {e}")
        return None

def check_tables(conn):
    print("\nChecking database tables...")
    tables = ['patients', 'allergies', 'nutrition_reference', 'food_transactions', 'nutrient_targets']
    cursor = conn.cursor()
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table '{table}' exists with {count} rows")
        except psycopg2.Error as e:
            print(f"Error with table '{table}': {e}")
    
    cursor.close()

def main():
    conn = check_connection()
    if conn:
        check_tables(conn)
        conn.close()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()