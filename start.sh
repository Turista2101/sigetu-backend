#!/bin/bash
set -e

echo "Marcando migraciones como aplicadas..."
python -m alembic stamp head || true

echo "Corriendo migraciones..."
python -m alembic upgrade head

echo "Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000