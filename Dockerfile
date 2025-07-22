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

# Collect static files (only matters in prod)
WORKDIR /app/WebProject

# Expose port
EXPOSE 8000

# Use an environment variable for flexibility
CMD ["sh", "-c", "${DJANGO_COMMAND}"]
