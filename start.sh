#!/bin/sh
set -e

echo "Corriendo migraciones..."
python -m alembic upgrade head

echo "Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000