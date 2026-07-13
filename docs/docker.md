# Docker Deployment Guide

The Legal RAG Platform is fully containerized for simplified enterprise deployment. The architecture comprises two core services: the **FastAPI Backend (`api`)** and the **Streamlit Frontend (`ui`)**.

## 1. Prerequisites
- Docker Engine
- Docker Compose v2

## 2. Configuration
Before starting the cluster, copy the example environment file and customize the connection parameters if necessary.

```bash
cp .env.example .env
```
*(By default, `.env.example` points to the Mock LLM providers and local vector databases.)*

## 3. Build & Run
You can build and start the entire cluster with a single command:

```bash
docker compose up --build -d
```
*The `-d` flag runs the containers in detached mode.*

**Note**: The UI container has a strict dependency `depends_on: api: condition: service_healthy`. It will gracefully wait until the FastAPI backend returns `200 OK` on its `/health` probe before booting Streamlit.

## 4. Accessing the System
Once both containers report `Healthy`:
- **UI Presentation Layer**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Backend Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 5. Stopping the Cluster
To cleanly spin down the deployment:

```bash
docker compose down
```

## Troubleshooting
**"The UI container is stuck in 'Created' state"**
This happens if the API backend fails to pass its Healthcheck. View the backend logs to see why the API failed to boot:
```bash
docker compose logs api
```

**"Changes to Python files aren't reflecting"**
Because Docker copies the application code into the image, you must rebuild the cluster to capture code changes:
```bash
docker compose up --build
```
