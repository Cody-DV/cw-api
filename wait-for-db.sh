#!/bin/sh
# wait-for-db.sh - Script to wait for PostgreSQL database to be ready

set -e

host="$1"
shift
cmd="$@"

# Give some time for PostgreSQL to initialize
echo "Waiting for PostgreSQL to fully initialize..."
sleep 5

# Function to test database availability with all tables
db_ready() {
  PGPASSWORD=pass psql -h "$host" -U postgres -d patient_nutrition_demo -c "SELECT COUNT(*) FROM patients" >/dev/null 2>&1
  return $?
}

# Wait for the database to be ready
echo "Waiting for database tables to be available..."
for i in $(seq 1 30); do
  if db_ready; then
    echo "✅ Database is ready - executing command"
    exec $cmd
    exit 0
  fi
  
  echo "Database tables not ready yet (attempt $i/30) - waiting..."
  sleep 2
done

echo "❌ Error: Failed to connect to database after 30 attempts"
echo "Attempting to diagnose the issue..."

# Diagnostic checks
echo "1. Checking if PostgreSQL server is running..."
PGPASSWORD=pass psql -h "$host" -U postgres -c '\l' || echo "Cannot connect to PostgreSQL server"

echo "2. Checking if database exists..."
PGPASSWORD=pass psql -h "$host" -U postgres -l | grep patient_nutrition_demo || echo "Database 'patient_nutrition_demo' not found"

echo "3. Checking database tables..."
PGPASSWORD=pass psql -h "$host" -U postgres -d patient_nutrition_demo -c '\dt' || echo "Cannot list tables"

echo "❌ Database initialization failed. Please check logs and fix the issue."
exit 1