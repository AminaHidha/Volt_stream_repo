# Official Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed by psycopg2 (PostgreSQL adapter)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (faster rebuilds if only code changes)
COPY requirements.txt .

# Install all Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django project
COPY . .

# Expose port 8000 (Django/Daphne's default port)
EXPOSE 8000

# Start Django using Daphne (ASGI server for WebSocket support)
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && daphne -b 0.0.0.0 -p 8000 ev_project.asgi:application"]