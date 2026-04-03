# Lab 02: Congo Returns — ML Processing Pipeline

## Overview

This lab implements a containerized machine learning pipeline for Congo's automated returns processing system. The pipeline consists of two Docker containers that communicate over HTTP:

1. **Inference API**: A FastAPI service running MobileNetV2 for product image classification
2. **Preprocessor**: A folder watcher that processes incoming images and sends them to the inference API

## Architecture

```
[Warehouse Datacenter]          [Main Datacenter]
    /incoming/                      /logs/
        ↓                              ↑
    Preprocessor Container  →  Inference API Container
        (Watch files)           (Classify images)
        (Parse metadata)        (Log results)
        (Send to API)           (MobileNetV2 model)
```

## Setup Instructions

### Prerequisites
- Docker Desktop installed and running
- Python 3.11+ (for host testing)
- Windows/Mac with `host.docker.internal` support (or Linux with `--add-host` flag)

### Critical Dependencies & Fixes

**NumPy Compatibility:** The inference API uses `numpy<2.0` because PyTorch 2.0.1 was compiled against NumPy 1.x and will crash if used with NumPy 2.x. This is handled automatically by the requirements.txt.

**PyTorch Wheels:** The Dockerfile uses CPU-only PyTorch wheels with dual pip indices:
```dockerfile
--index-url https://download.pytorch.org/whl/cpu \
--extra-index-url https://pypi.org/simple
```
This ensures torch/torchvision come from PyTorch's repository (CPU wheels), while other packages come from PyPI. CPU wheels are ~195MB vs 620MB+ for CUDA versions—much faster to download and no GPU required.

### Directory Structure

Create these directories on your host machine before running containers:
```
c:\Users\manny\Documents\BUS675\bus675_s26\
├── incoming/         (where warehouse images are placed)
└── logs/            (where API writes classification results)
```

## Docker Build Commands

### Build the Inference API Image

```powershell
cd labs\LAB02_submission\inference_api
docker build -t congo-inference:v1 .
```

**Output:** Image `congo-inference:v1` (~310MB with CPU-only PyTorch wheels)

**Key optimization:** Uses `python:3.11-slim` base image and CPU-only PyTorch wheels instead of CUDA variants, reducing download size from 620MB+ to 195MB and improving startup time.

**Build time:** ~3-4 minutes on standard machine

### Build the Preprocessor Image

```powershell
cd labs\LAB02_submission\preprocessor
docker build -t congo-preprocessor:v1 .
```

**Output:** Image `congo-preprocessor:v1` (~150MB, minimal dependencies)

## Docker Run Commands

### Run the Inference API Container

```powershell
docker run `
  --name congo-api `
  -v C:\Users\manny\Documents\BUS675\bus675_s26\logs:/logs `
  -p 8000:8000 `
  congo-inference:v1
```

**Windows CMD syntax (if PowerShell backtick doesn't work):**
```cmd
docker run ^
  --name congo-api ^
  -v C:\Users\manny\Documents\BUS675\bus675_s26\logs:/logs ^
  -p 8000:8000 ^
  congo-inference:v1
```

**Linux/Mac syntax:**
```bash
docker run \
  --name congo-api \
  -v ~/bus675_s26/logs:/logs \
  -p 8000:8000 \
  congo-inference:v1
```

**Parameters:**
- `--name congo-api`: Gives the container a friendly name
- `-v` (volume): Mounts host's `logs/` to container's `/logs/` (enables data persistence)
- `-p 8000:8000`: Maps port 8000 from container to host machine
- Image tag: `congo-inference:v1`

**Verify:** Open `http://localhost:8000/docs` in browser to see Swagger UI

**First run:** Model downloads pretrained weights (~30MB) on first inference request. Subsequent requests use cached model.

### Run the Preprocessor Container

```powershell
docker run `
  --name congo-preprocessor `
  -v C:\Users\manny\Documents\BUS675\bus675_s26\incoming:/incoming `
  -e API_URL=http://host.docker.internal:8000 `
  congo-preprocessor:v1
```

**Windows CMD syntax:**
```cmd
docker run ^
  --name congo-preprocessor ^
  -v C:\Users\manny\Documents\BUS675\bus675_s26\incoming:/incoming ^
  -e API_URL=http://host.docker.internal:8000 ^
  congo-preprocessor:v1
```

**Linux/Mac syntax (requires adding host entry):**
```bash
docker run \
  --add-host=host.docker.internal:host-gateway \
  --name congo-preprocessor \
  -v ~/bus675_s26/incoming:/incoming \
  -e API_URL=http://host.docker.internal:8000 \
  congo-preprocessor:v1
```

**Parameters:**
- `--name congo-preprocessor`: Container name
- `-v` (volume): Mounts host's `incoming/` to container's `/incoming/`
- `-e API_URL=...`: Sets environment variable (preprocessor needs this to find the API)
  - **Key insight:** Uses `host.docker.internal` instead of `localhost` because from inside the container, `localhost` refers to the container itself, not the host machine
  - On Linux, you must add `--add-host=host.docker.internal:host-gateway` flag
- Image tag: `congo-preprocessor:v1`

**Verify:** Run `docker logs -f congo-preprocessor` and you should see:
```
============================================================
Congo Returns - Preprocessor / Folder Watcher
============================================================
Watching: /incoming for new images
API URL: http://host.docker.internal:8000
Poll interval: 2 seconds
```

## How the Containers Communicate

### Data Flow

The preprocessor and inference API containers communicate using HTTP:

1. **Preprocessor role**: Watches the `/incoming/` folder on the host (mounted via volume mount)
2. **When an image arrives**: Preprocessor extracts metadata from the filename (e.g., CUST12345_PROD67890_laptop.png)
3. **Preprocessor sends to API**: Makes HTTP POST request to `http://host.docker.internal:8000/predict` with the image file and metadata
4. **API processes image**: Runs inference using MobileNetV2 neural network, returns classification result
5. **API logs result**: Writes JSON-formatted result to `/logs/classifications.jsonl` (mounted volume)
6. **Results persist on host**: Since `/logs/` is a mounted volume, the JSON logs are written to the **host machine** at `c:\Users\manny\Documents\BUS675\bus675_s26\logs\classifications.jsonl`
7. **Preprocessor moves image**: After successful processing, moves image to `/incoming/processed/` (prevents reprocessing)

### The Networking Challenge

Inside a Docker container, **`localhost` and `127.0.0.1` refer to that container**, not the host machine. This means:

❌ **Wrong:** `API_URL=http://localhost:8000` (preprocessor would try to contact itself)
✅ **Correct:** `API_URL=http://host.docker.internal:8000` (Docker Desktop feature that resolves to the host's IP)

### Volume Mounting Strategy

Both containers share data with the host through mounted volumes:

```
Host Machine (Windows)              Docker Containers
    c:\...\incoming/    ←mount→    /incoming (both can read/write)
    c:\...\logs/        ←mount→    /logs (API can write, host can read)
```

This approach enables:
- **Data persistence**: Logs survive container restarts
- **Separation of concerns**: Containers are stateless; data lives on host
- **Easy debugging**: Can inspect files on host while containers are running
- **Scalability**: Multiple containers could write to same logs folder

## Testing the Pipeline

### 1. Create directories on host
```powershell
mkdir incoming
mkdir logs
```

### 2. Copy test images
```powershell
Copy-Item "labs\LAB02_submission\warehouse_images\CUST*.png" -Destination "incoming"
```

### 3. Monitor processing
```bash
docker logs -f congo-preprocessor
```

Expected output:
```
  Processing: CUST95991_PROD31293_headphones.png
    Customer: 95991, Product: 31293
    ✅ Classified as: headphones (92.3%)
```

### 4. Check results
```powershell
Get-Content logs\classifications.jsonl
```

Each line is a JSON object:
```json
{"timestamp":"2024-01-15T10:30:45.123456","filename":"CUST95991_PROD31293_headphones.png","customer_id":"95991","product_id":"31293","top_prediction":"headphones","confidence":92.3}
```

## API Endpoints Reference

### GET `/health`
Health check for load balancers and orchestration systems.
```bash
curl http://localhost:8000/health
```

### POST `/predict`
Classify a product image.
```bash
curl -X POST "http://localhost:8000/predict" `
  -F "file=@image.png" `
  -F "customer_id=12345" `
  -F "product_id=67890"
```

### GET `/stats`
Get processing statistics (total count, breakdown by category, average confidence).
```bash
curl http://localhost:8000/stats
```

### GET `/docs`
View Swagger UI documentation.
```
http://localhost:8000/docs
```

## Container Lifecycle Management

### View running containers
```bash
docker ps
```

### View container logs
```bash
docker logs -f congo-api        # Stream logs from inference API
docker logs -f congo-preprocessor  # Stream logs from preprocessor
```

### Stop containers
```bash
docker stop congo-api congo-preprocessor
```

### Remove containers
```bash
docker rm congo-api congo-preprocessor
```

### Remove images
```bash
docker rmi congo-inference:v1 congo-preprocessor:v1
```

## Production Considerations

### For distributing across datacenters:
1. Replace mounted volumes with object storage (S3)
2. Replace HTTP with message queues (RabbitMQ, Kafka) for resilience
3. Use container orchestration (Kubernetes) for deployment
4. Add proper monitoring (Prometheus, Datadog) and alerting
5. Implement service discovery for dynamic API endpoint resolution

### For handling higher throughput:
1. Run multiple preprocessor containers (each watching different folders)
2. Run multiple API containers behind a load balancer
3. Use batch processing endpoint for grouped predictions
4. Stream results to database instead of JSONL files

