# Docker Deployment Guide

## Quick Start

### 1. Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- Your trained ML model files (`.pkl`)

### 2. Copy Model Files

```bash
# Copy your 4 trained model files
cp /path/to/isolation_forest.pkl backend/src/data/models/
cp /path/to/xgboost_model.pkl backend/src/data/models/
cp /path/to/scaler.pkl backend/src/data/models/
cp /path/to/feature_names.pkl backend/src/data/models/
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit if needed (optional)
nano .env
```

### 4. Start Services

```bash
# Make startup script executable
chmod +x start-docker.sh

# Run startup script
./start-docker.sh
```

---

## Services

The Docker stack includes:

| Service | Port | Description |
|---------|------|-------------|
| **PostgreSQL** | `5432` | Database for logger API |
| **Logger API** (Rust) | `8080` | Solana attestation service |
| **ML Backend** (FastAPI) | `8000` | Risk prediction API |

---

## Manual Commands

### Build Images

```bash
docker-compose build
```

### Start Services

```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ml-backend
docker-compose logs -f logger-api
docker-compose logs -f postgres
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes

```bash
docker-compose down -v
```

---

## Health Checks

### Check Service Status

```bash
docker-compose ps
```

### API Health Endpoints

```bash
# ML Backend
curl http://localhost:8000/health

# Logger API
curl http://localhost:8080/api/v1/health
```

---

## Accessing Services

### ML API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Test ML Prediction

```bash
curl "http://localhost:8000/risk/current?coin=USDC&chain=ethereum"
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it atlas-postgres psql -U atlas -d atlas_logs

# List tables
\dt

# Query logs
SELECT * FROM logs LIMIT 10;
```

---

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart ml-backend
```

### Model Files Missing

```
⚠️  WARNING: ML model files not found
```

**Solution**: Copy your `.pkl` files to `backend/src/data/models/`

### Database Connection Issues

```bash
# Check Postgres logs
docker-compose logs postgres

# Recreate database
docker-compose down -v
docker-compose up -d postgres
```

### Port Already in Use

```
Error: port is already allocated
```

**Solution**: Change port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

---

## Production Deployment

### Update Environment Variables

```bash
# Edit .env for production
nano .env
```

Set:
- `SOLANA_RPC_URL` to mainnet
- `POSTGRES_PASSWORD` to strong password
- Update `CORS_ORIGINS` for your domain

### Use Production Compose File

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Enable HTTPS

Add Nginx reverse proxy:

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
```

---

## Flutter Web (Optional)

To serve Flutter web from Docker:

### 1. Build Flutter Web

```bash
cd flutter
flutter build web --release
```

### 2. Add Nginx Service

```yaml
# docker-compose.yml
services:
  flutter-web:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./flutter/build/web:/usr/share/nginx/html:ro
```

### 3. Start

```bash
docker-compose up -d flutter-web
```

Access at: http://localhost:3000

---

## Maintenance

### Update Images

```bash
docker-compose pull
docker-compose up -d
```

### Backup Database

```bash
docker exec atlas-postgres pg_dump -U atlas atlas_logs > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker exec -i atlas-postgres psql -U atlas -d atlas_logs
```

---

## Architecture

```
┌─────────────────┐
│  Flutter Web    │
│  (localhost:3000)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     ML Backend (FastAPI)            │
│     localhost:8000                  │
│  ┌──────────────────────────────┐  │
│  │ • Feature Engineering        │  │
│  │ • ML Models (ISO + XGB)      │  │
│  │ • SHAP Explainability        │  │
│  │ • TCS Gating                 │  │
│  └──────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     Logger API (Rust)               │
│     localhost:8080                  │
│  ┌──────────────────────────────┐  │
│  │ • Risk Log Storage           │  │
│  │ • Solana Attestation         │  │
│  │ • Blockchain Verification    │  │
│  └──────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────┐
│   PostgreSQL    │     │   Solana    │
│   localhost:5432│     │  Blockchain │
└─────────────────┘     └─────────────┘
```

---

**Ready to deploy!** 🚀
