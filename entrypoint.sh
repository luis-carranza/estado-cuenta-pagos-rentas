#!/bin/bash
# entrypoint.sh — run seed if DB is empty, then start the API
set -e

DB_FILE="${DB_FILE:-/app/data/app.db}"

if [ ! -f "$DB_FILE" ] || [ ! -s "$DB_FILE" ]; then
  echo "▶ Fresh database detected — running seed_all.py ..."
  python seed_all.py
  echo "✅ Seed complete."
else
  echo "▶ Database found at $DB_FILE — skipping seed."
fi

echo "▶ Starting FastAPI server ..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

