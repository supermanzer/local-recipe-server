#!/bin/sh
set -e

echo "Waiting for database to become available..."

python - <<'PY'
import os
import sys
import time
import socket

# Get PostgreSQL connection parameters from environment variables
host = os.getenv('POSTGRES_HOST', 'postgres')  # Default to 'postgres' for Docker
port = int(os.getenv('POSTGRES_PORT', 5432))
user = os.getenv('POSTGRES_USER', 'admin_user')
db = os.getenv('POSTGRES_DB', 'recipes')

print(f'Attempting to connect to {user}@{host}:{port}/{db}')

for i in range(60):
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        print(f'Database reachable at {host}:{port}')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting for DB... attempt {i+1}/60')
        time.sleep(1)

print('Timed out waiting for DB after 60s')
sys.exit(1)
PY

echo "Database is available. Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell <<'PYEOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.getenv('DJ_SUPERUSER', 'admin')
password = os.getenv('DJ_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, 'admin@example.com', password)
    print(f"Superuser '{username}' created successfully")
else:
    print(f"Superuser '{username}' already exists")
PYEOF

echo "Startup complete. Starting application..."

# Exec the CMD from Dockerfile (so runserver will start)
exec "$@"
