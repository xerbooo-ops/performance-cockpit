#!/bin/sh
set -eu

alembic upgrade head
exec uvicorn performance_cockpit.main:app --host 0.0.0.0 --port 8000
