#!/bin/bash

# ATLAS ML Risk Prediction - Docker Startup Script
# This script starts the entire stack using Docker Compose

set -e

echo "🚀 Starting ATLAS ML Risk Prediction Stack..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed.${NC}"
    exit 1
fi

# Check if model files exist
MODELS_DIR="backend/src/data/models"
if [ ! -f "$MODELS_DIR/isolation_forest.pkl" ] || \
   [ ! -f "$MODELS_DIR/xgboost_model.pkl" ] || \
   [ ! -f "$MODELS_DIR/scaler.pkl" ] || \
   [ ! -f "$MODELS_DIR/feature_names.pkl" ]; then
    echo -e "${YELLOW}⚠️  WARNING: ML model files not found in $MODELS_DIR${NC}"
    echo "Please copy your trained models:"
    echo "  cp /path/to/isolation_forest.pkl $MODELS_DIR/"
    echo "  cp /path/to/xgboost_model.pkl $MODELS_DIR/"
    echo "  cp /path/to/scaler.pkl $MODELS_DIR/"
    echo "  cp /path/to/feature_names.pkl $MODELS_DIR/"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build Flutter web
echo ""
echo -e "${GREEN}🎨 Building Flutter web...${NC}"
cd flutter
if ! flutter build web --release; then
    echo -e "${RED}❌ Flutter build failed${NC}"
    exit 1
fi
cd ..
echo -e "${GREEN}✅ Flutter web built${NC}"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cat > .env << EOF
# Database
POSTGRES_USER=atlas
POSTGRES_PASSWORD=atlas_dev_password
POSTGRES_DB=atlas_logs

# Solana (use devnet for testing)
SOLANA_RPC_URL=https://api.devnet.solana.com

# ML Backend
TCS_THRESHOLD=0.7
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
fi

# Build and start services
echo ""
echo -e "${GREEN}🔨 Building Docker images...${NC}"
docker-compose build

echo ""
echo -e "${GREEN}🚢 Starting services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo ""
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"

# Function to check service health
check_health() {
    local service=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep $service | grep -q "healthy"; then
            echo -e "${GREEN}✅ $service is healthy${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    echo -e "${RED}❌ $service failed to become healthy${NC}"
    return 1
}

# Check each service
check_health "postgres" || exit 1
check_health "logger-api" || exit 1
check_health "ml-backend" || exit 1
check_health "flutter-web" || exit 1

echo ""
echo -e "${GREEN}✨ All services are running!${NC}"
echo ""
echo "═══════════════════════════════════════════════════"
echo "  📊 ATLAS ML Risk Prediction Stack"
echo "═══════════════════════════════════════════════════"
echo ""
echo "Services:"
echo "  🗄️  PostgreSQL:      localhost:5432"
echo "  🦀 Logger API:       http://localhost:8080"
echo "  🧠 ML Backend:       http://localhost:8000"
echo "  🌐 Flutter Web:      http://localhost:3000"
echo ""
echo "API Documentation:"
echo "  📖 ML API Docs:      http://localhost:8000/docs"
echo "  💚 ML Health:        http://localhost:8000/health"
echo "  💙 Logger Health:    http://localhost:8080/api/v1/health"
echo ""
echo "Logs:"
echo "  docker-compose logs -f ml-backend"
echo "  docker-compose logs -f logger-api"
echo "  docker-compose logs -f flutter-web"
echo ""
echo "Stop:"
echo "  docker-compose down"
echo ""
echo "═══════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}🎉 Ready to receive requests!${NC}"
echo ""
