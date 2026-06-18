FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Start
CMD cd backend && python -c "from app.db.database import init_db; init_db()" && uvicorn app.main:app --host 0.0.0.0 --port $PORT
