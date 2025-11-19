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

# Exec the CMD from Dockerfile (so runserver will start)
exec "$@"
