FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code + seed scripts
COPY main.py seed_all.py seed_units.py seed_bank_statements.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Persistent data directories (mounted as Docker volumes in production)
RUN mkdir -p /app/uploads /app/data

ENV DB_FILE=/app/data/app.db
ENV UPLOADS_DIR=/app/uploads

EXPOSE 8000

# entrypoint.sh auto-seeds a fresh DB then starts uvicorn
ENTRYPOINT ["./entrypoint.sh"]


