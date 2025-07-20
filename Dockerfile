# Start from official Python 3 image
FROM python:3.12-slim

# Set work directory at project root inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Change into Django project directory
WORKDIR /app/WebProject

# Expose port for Django dev server
EXPOSE 8000

# Run Django dev server with watchdog-based auto reload
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]