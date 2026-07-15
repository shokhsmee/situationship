#!/usr/bin/env sh
set -e

# Wait for Postgres to accept connections (compose healthcheck also gates this).
echo "Waiting for database…"
python - <<'PY'
import asyncio, os, sys
import asyncpg

dsn = os.environ["DATABASE_URL"].replace("+asyncpg", "")

async def wait():
    for _ in range(30):
        try:
            conn = await asyncpg.connect(dsn)
            await conn.close()
            return
        except Exception:
            await asyncio.sleep(1)
    sys.exit("database never became ready")

asyncio.run(wait())
PY

echo "Running migrations…"
alembic upgrade head

echo "Seeding demo content…"
python -m app.scripts.seed || true

echo "Starting API…"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
