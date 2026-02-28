# ATLAS ML Risk Prediction Stack

Complete ML-powered stablecoin risk prediction system with blockchain attestation and web interface.

## 🚀 Quick Start (Docker - Recommended)

```bash
# 1. Copy your trained models
cp /path/to/*.pkl backend/src/data/models/

# 2. Start everything (includes Flutter web build)
./start-docker.sh
```

Access:
- **🌐 Web App**: http://localhost:3000
- **📖 ML API Docs**: http://localhost:8000/docs
- **🦀 Logger API**: http://localhost:8080

That's it! The script builds Flutter web, starts 4 Docker services, and opens your browser.

---

## 📦 What's Running

| Service | Port | Description |
|---------|------|-------------|
| **Flutter Web** (nginx) | `3000` | Web dashboard with ML visualizations |
| **ML Backend** (FastAPI) | `8000` | Risk prediction + SHAP explainability |
| **Logger API** (Rust) | `8080` | Solana blockchain attestation |
| **PostgreSQL** | `5432` | Log storage database |

---

## 📚 Documentation

- [Docker Deployment](DOCKER_DEPLOYMENT.md) - Run everything with Docker
- [API Specification](API_SPECIFICATION.md) - REST API reference
- [ML Deployment](backend/ML_DEPLOYMENT.md) - Manual ML backend setup
- [Flutter Web](flutter/FLUTTER_WEB_DEPLOYMENT.md) - Frontend integration

---

## 🏗️ Architecture

```
Price Data → Feature Engineering (58 features)
  → ML Models (Isolation Forest + XGBoost)  
  → SHAP Explanations
  → FastAPI (:8000)
  → Logger API (:8080)
  → Solana Blockchain
```

**Key Features**:
- 58-feature engineering pipeline
- Ensemble ML (40% ISO + 60% XGB)
- SHAP explainability (XAI)
- TCS confidence gating (≥0.7)
- On-chain attestation (Solana)
- Real-time WebSocket updates

---

## 🧪 Testing

```bash
# Check health
curl http://localhost:8000/health

# Get risk prediction
curl "http://localhost:8000/risk/current?coin=USDC&chain=ethereum"

# View logs
docker-compose logs -f ml-backend
```

---

## 📊 Production Checklist

- [ ] Copy trained ML models to `backend/src/data/models/`
- [ ] Update `.env` with production values
- [ ] Set `SOLANA_RPC_URL` to mainnet
- [ ] Configure strong `POSTGRES_PASSWORD`
- [ ] Build Flutter web: `flutter build web --release`
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure monitoring & alerts

---

## 🤝 Support

For issues:
1. Check [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) troubleshooting
2. Review service logs: `docker-compose logs`
3. Verify model files are in place

---

**License**: MIT
