# Use a slim Python base for smaller/faster pulls than CUDA runtime images.
FROM python:3.11-slim

# Keep Python/pip output predictable in containers.
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

# Set working directory in container
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt requirements.txt

# Install dependencies using PyTorch CPU wheels (smaller, faster builds)
# Use CPU index for torch/torchvision, fall back to PyPI for other packages
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple \
    -r requirements.txt

# Copy application code and necessary files
COPY app.py app.py
COPY imagenet_classes.json imagenet_classes.json

# Expose port 8000 (for documentation, doesn't actually do anything)
EXPOSE 8000

# Run the FastAPI application with uvicorn
# --host 0.0.0.0 makes the server accessible from outside the container
# --port 8000 listens on port 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
