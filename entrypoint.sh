#!/bin/bash
export PYTHONPATH=.

# Let the DB start
python backend_pre_start.py

# Run migrations
alembic upgrade head &&

# Run tests
#pytest . --asyncio-mode=auto &&

# Run FastAPI application
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000