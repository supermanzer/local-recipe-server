#!/bin/sh
set -e

echo "Waiting for database to become available..."

python - <<'PY'
import os
import sys
import time
import socket
from urllib.parse import urlparse

url = os.getenv('DATABASE_URL')
if not url:
    print('No DATABASE_URL provided; skipping wait.')
    sys.exit(0)

p = urlparse(url)
host = p.hostname or 'localhost'
port = int(p.port or 5432)

for i in range(60):
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        print('Database reachable at %s:%d' % (host, port))
        sys.exit(0)
    except Exception:
        print('Waiting for DB... attempt', i+1)
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
