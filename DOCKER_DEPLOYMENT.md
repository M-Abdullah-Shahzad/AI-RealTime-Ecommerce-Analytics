# Docker Deployment Guide

## AI-Powered E-Commerce Analytics Platform - Docker Setup

---

## 📋 PREREQUISITES

### System Requirements
- Docker Desktop (3.0+) or Docker Engine
- Docker Compose (2.0+)
- 8GB RAM minimum
- 10GB disk space
- Windows 10/11, macOS, or Linux

### Installation

**Windows:**
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Run installer
3. Restart computer
4. Verify: `docker --version`

**Mac:**
```bash
brew install docker docker-compose
# Or download Docker Desktop
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
```

---

## 🚀 QUICK START (5 MINUTES)

### 1. Build and Run with Docker Compose
```bash
# Navigate to project folder
cd "c:\Users\usama\OneDrive\Desktop\BDA project"

# Start all services (builds Docker image automatically)
docker-compose up --build

# Wait for services to start (~2-3 minutes)
# You'll see: "You can now view your Streamlit app in your browser"
```

### 2. Access the Services

**Streamlit Dashboard:**
- URL: `http://localhost:8501`
- Real-time analytics and KPIs

**Kafka Broker:**
- Host: `kafka:9092` (internal)
- Port: `9092` (external)

**Spark UI (if running):**
- URL: `http://localhost:8080`

### 3. Stop Services
```bash
# Stop all containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View running containers
docker ps

# View logs
docker-compose logs -f bda-app
```

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────┐
│         Docker Compose Network              │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌────────────┐         │
│  │  Zookeeper   │  │   Kafka    │         │
│  │   (2181)     │  │  (9092)    │         │
│  └──────────────┘  └────────────┘         │
│         ▲               ▲                  │
│         └───────────────┘                  │
│              │                             │
│         ┌────▼────────────┐               │
│         │   BDA App       │               │
│         │  (8501,7077)    │               │
│         │ • Batch Process │               │
│         │ • Analytics     │               │
│         │ • Dashboard     │               │
│         └─────────────────┘               │
│                                           │
└─────────────────────────────────────────────┘
         (Isolated Network: bda-network)
```

---

## 📁 FILE STRUCTURE

```
project-root/
├── Dockerfile                 ← Container definition
├── docker-compose.yml         ← Orchestration
├── .dockerignore               ← Files to exclude
├── requirements.txt            ← Python dependencies
├── *.py                        ← Python modules
├── data/
│   └── online_retail_II.csv   ← Input dataset
└── outputs/                   ← Generated results (mounted volume)
```

---

## 🐳 DOCKER COMMANDS REFERENCE

### Build
```bash
# Build image from Dockerfile
docker build -t bda-analytics:latest .

# Build specific service
docker-compose build bda-app

# Build without cache
docker build --no-cache -t bda-analytics:latest .
```

### Run
```bash
# Run all services
docker-compose up

# Run in background (detached)
docker-compose up -d

# Run specific service
docker-compose up bda-app

# Run with verbose output
docker-compose up --verbose
```

### Logs
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs bda-app

# Last 50 lines
docker-compose logs --tail=50
```

### Debugging
```bash
# Open shell in container
docker-compose exec bda-app bash

# Run command in container
docker-compose exec bda-app python batch_processing.py

# Check service health
docker-compose ps

# Inspect container
docker inspect bda-analytics-app

# View resource usage
docker stats
```

### Clean Up
```bash
# Stop all services
docker-compose stop

# Remove all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker rmi bda-analytics:latest

# Remove unused resources
docker system prune -a
```

---

## 📊 SERVICE DETAILS

### Zookeeper Service
```yaml
Container: bda-zookeeper
Port: 2181
Purpose: Kafka coordination
Status: Must be healthy for Kafka
Restart: Always (auto-restart if fails)
```

### Kafka Service
```yaml
Container: bda-kafka
Ports: 9092 (external), 29092 (internal)
Purpose: Message streaming
Topics: retail_orders (auto-created)
Depends On: zookeeper (healthy)
```

### BDA App Service
```yaml
Container: bda-analytics-app
Ports: 8501 (dashboard), 7077 (Spark), 8080 (Spark UI)
Purpose: Analytics pipeline + dashboard
Depends On: kafka (healthy)
Volumes: /data, /outputs, /logs (mounted)
Environment: KAFKA_BROKER=kafka:29092
```

---

## 🚨 TROUBLESHOOTING

### Issue: "Cannot connect to Docker daemon"
```bash
# Solution: Start Docker Desktop or daemon
# Windows: Open Docker Desktop application
# Linux: sudo systemctl start docker
```

### Issue: "Port 8501 already in use"
```bash
# Solution 1: Use different port
docker-compose up -p 8502:8501

# Solution 2: Kill process using port
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux:
lsof -i :8501
kill -9 <PID>
```

### Issue: "Out of memory"
```bash
# Solution: Increase Docker memory
# Docker Desktop Settings → Resources → Memory: 8GB+

# Or limit container memory:
# Edit docker-compose.yml:
services:
  bda-app:
    deploy:
      resources:
        limits:
          memory: 4G
```

### Issue: "Kafka not connecting"
```bash
# Check Kafka health
docker-compose exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# View Kafka logs
docker-compose logs kafka

# Recreate Kafka
docker-compose down -v
docker-compose up kafka zookeeper
```

### Issue: "Dashboard not loading"
```bash
# Check app logs
docker-compose logs bda-app

# Restart app
docker-compose restart bda-app

# Check if port is accessible
curl http://localhost:8501
```

---

## 📈 MONITORING & LOGS

### Real-time Monitoring
```bash
# Watch all services
docker-compose logs -f

# Watch specific service
docker-compose logs -f bda-app

# With timestamps
docker-compose logs -f --timestamps
```

### Metrics
```bash
# CPU, Memory, I/O
docker stats

# Specific container
docker stats bda-analytics-app
```

### Health Checks
```bash
# View container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check service status
docker-compose ps
```

---

## 🔐 SECURITY BEST PRACTICES

### 1. Environment Variables
```bash
# Create .env file
KAFKA_BROKER=kafka:29092
DB_PASSWORD=secure_password

# Reference in docker-compose.yml
environment:
  - KAFKA_BROKER=${KAFKA_BROKER}
```

### 2. Volume Permissions
```bash
# Run container as non-root
docker run -u 1000:1000 ...

# Edit docker-compose.yml:
services:
  bda-app:
    user: "1000:1000"
```

### 3. Network Isolation
```bash
# Services communicate via named network
# No direct access unless exposed ports
networks:
  - bda-network  # Isolated network
```

---

## 📦 IMAGE OPTIMIZATION

### Image Size
```dockerfile
# Multi-stage build reduces size
# Stage 1: Builder (with build tools)
# Stage 2: Runtime (only runtime deps)
```

Current image size: ~1.5GB (Python 3.9 + Spark + Kafka client)

### Reducing Size
```dockerfile
# Use slim base image
FROM python:3.9-slim

# Remove unnecessary packages
RUN apt-get remove build-essential

# Clean apt cache
RUN rm -rf /var/lib/apt/lists/*
```

---

## 📱 DEPLOYMENT OPTIONS

### Option 1: Local Docker (Development)
```bash
docker-compose up --build
```
✅ Full control, debugging
✅ Local testing
❌ Not accessible remotely

### Option 2: Docker Swarm (Production)
```bash
docker swarm init
docker stack deploy -c docker-compose.yml bda

# Scale services
docker service scale bda-app=3
```
✅ Multi-node
✅ Load balancing
⚠️ More complex

### Option 3: Kubernetes (Enterprise)
See KUBERNETES_DEPLOYMENT.md for K8s setup

### Option 4: Cloud Deployment
- **AWS ECS**: Docker on AWS Fargate
- **Azure**: Azure Container Instances
- **GCP**: Cloud Run or GKE

---

## 🔄 CI/CD INTEGRATION

### GitHub Actions Example
```yaml
name: Build and Deploy

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: docker/build-push-action@v2
        with:
          push: true
          tags: user/bda-analytics:latest
```

---

## 📊 PERFORMANCE TIPS

1. **Use volumes for data**: Faster I/O
2. **Health checks**: Auto-restart on failure
3. **Resource limits**: Prevent runaway containers
4. **Networking**: Internal communication is fast
5. **Caching**: Docker layers cache builds

---

## 🎯 COMMON TASKS

### Run Specific Module
```bash
docker-compose exec bda-app python batch_processing.py
```

### Copy Files from Container
```bash
docker-compose exec bda-app cp outputs/file.csv ./
docker cp bda-analytics-app:/app/outputs/file.csv ./
```

### Copy Files to Container
```bash
docker cp ./data.csv bda-analytics-app:/app/data/
```

### Interactive Bash
```bash
docker-compose exec bda-app bash
# Inside container:
python -c "import pyspark; print(pyspark.__version__)"
```

---

## ✅ VERIFICATION CHECKLIST

After `docker-compose up`:

- [ ] Zookeeper running (port 2181)
- [ ] Kafka running (port 9092)
- [ ] BDA App running (port 8501)
- [ ] Dashboard accessible at `http://localhost:8501`
- [ ] No error logs in `docker-compose logs`
- [ ] Health checks passing: `docker-compose ps`

---

## 📞 SUPPORT

### Logs Location
```bash
# View container logs
docker-compose logs bda-app > app.log

# View system logs
docker system events
```

### Getting Help
1. Check logs: `docker-compose logs`
2. Review docker-compose.yml
3. Check Dockerfile
4. Verify port availability
5. Ensure disk space available

---

## 🎉 SUCCESS!

You've successfully containerized your BDA Analytics Platform!

Next steps:
1. Access dashboard at `http://localhost:8501`
2. Monitor logs: `docker-compose logs -f`
3. Explore generated outputs in `outputs/`
4. Customize docker-compose.yml as needed

---

**For production deployment, see KUBERNETES_DEPLOYMENT.md or CLOUD_DEPLOYMENT.md**
