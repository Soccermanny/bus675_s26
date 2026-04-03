# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the watcher script
COPY watcher.py watcher.py

# Run the watcher on container startup
CMD ["python", "watcher.py"]
