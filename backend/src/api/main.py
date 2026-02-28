"""
FastAPI Main Application

REST API + WebSocket server for ML risk prediction system.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
import logging

from .models import (
    RiskState, RiskHistory, Alert, AlertDetail, AlertList,
    CoinConfig, ChainConfig, WSMessage,
    RiskLevel, WindowState, StressBreakdown, ChainFinality
)

try:
    from ..ml.feature_engineer import FeatureEngineer
    from ..ml.explainer import ExplainableRiskPredictor
    from ..ml.logger_client import LoggerClient
    _ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML modules unavailable: {e}")
    FeatureEngineer = None
    ExplainableRiskPredictor = None
    LoggerClient = None
    _ML_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ATLAS ML Risk API",
    description="Machine Learning Risk Prediction for Stablecoins",
    version="1.0.0"
)

# CORS middleware (allow Flutter web frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
feature_engineer: Optional[FeatureEngineer] = None
predictor: Optional[ExplainableRiskPredictor] = None
logger_client: Optional[LoggerClient] = None

# WebSocket connections
websocket_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup():
    """Initialize ML models and connections on startup."""
    global feature_engineer, predictor, logger_client

    logger.info("🚀 Starting ATLAS ML Risk API...")

    if _ML_AVAILABLE:
        # Initialize feature engineer
        try:
            feature_engineer = FeatureEngineer(window_size=96)
            logger.info("✅ Feature Engineer initialized")
        except Exception as e:
            logger.warning(f"⚠️  Feature Engineer unavailable: {e}")

        # Initialize ML predictor
        try:
            predictor = ExplainableRiskPredictor(model_dir='data/models')
            logger.info("✅ ML Predictor initialized")
        except Exception as e:
            logger.error(f"❌ Failed to load ML models: {e}")
            logger.warning("⚠️  API will run without ML predictions")
            predictor = None

        # Initialize logger client
        try:
            logger_client = LoggerClient(logger_api_url='http://localhost:8080')
            health = await logger_client.get_health()
            if health:
                logger.info("✅ Logger API connected")
            else:
                logger.warning("⚠️  Logger API unavailable")
        except Exception as e:
            logger.warning(f"⚠️  Logger API unavailable: {e}")
    else:
        logger.warning("⚠️  ML modules not installed, running API without ML")

    logger.info("✅ API ready!")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down...")
    for ws in websocket_connections:
        await ws.close()


# ==========================================
# RISK ENDPOINTS
# ==========================================

@app.get("/risk/current", response_model=RiskState)
async def get_current_risk(
    coin: str,
    chain: str = "ethereum"
):
    """
    Get current real-time risk state for a coin.
    
    Returns ML prediction with SHAP explanations if available.
    """
    # TODO: Get latest data from data collection pipeline
    # For now, return mock response

    return RiskState(
        coin=coin.upper(),
        chain=chain,
        timestamp=datetime.utcnow(),
        risk_score=45.0,
        risk_level=RiskLevel.ELEVATED,
        risk_rating="A",
        tcs=0.92,
        window_state=WindowState.FINAL,
        stress_breakdown=StressBreakdown(
            price_volatility=30.0,
            peg_deviation=15.0,
            velocity=25.0,
            market_correlation=30.0
        ),
        chain_finality_list=[
            ChainFinality(
                chain="ethereum",
                finality_tier=3,
                block_confirmations=64,
                is_finalized=True
            )
        ],
        ml_enabled=predictor is not None
    )


@app.get("/risk/history", response_model=RiskHistory)
async def get_risk_history(
    coin: str,
    from_: datetime,
    to: datetime,
    chain: str = "ethereum",
    interval: str = "5m"
):
    """
    Get historical risk data for a coin over time range.
    
    Args:
        coin: Coin ticker (USDC, USDT, etc.)
        from_: Start timestamp
        to: End timestamp
        chain: Chain name
        interval: Data interval (5m, 15m, 1h, 6h, 1d)
    """
    # TODO: Query from database
    
    return RiskHistory(
        coin=coin.upper(),
        chain=chain,
        from_time=from_,
        to_time=to,
        interval=interval,
        snapshots=[]
    )


# ==========================================
# ALERT ENDPOINTS
# ==========================================

@app.get("/alerts", response_model=AlertList)
async def get_alerts(
    coin: Optional[str] = None,
    min_risk: Optional[int] = None,
    tier: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get list of on-chain attested alerts.
    
    Filters:
    - coin: Filter by coin ticker
    - min_risk: Minimum risk score (0-100)
    - tier: Finality tier filter
    - limit: Max results (default 50)
    - offset: Pagination offset
    """
    # TODO: Query from database/logger
    
    return AlertList(
        total=0,
        alerts=[],
        limit=limit,
        offset=offset
    )


@app.get("/alerts/{alert_id}", response_model=AlertDetail)
async def get_alert_detail(alert_id: str):
    """
    Get detailed information about a specific alert.
    
    Includes full ML model outputs and SHAP explanations.
    """
    # TODO: Query from database
    
    raise HTTPException(status_code=404, detail="Alert not found")


# ==========================================
# CONFIG ENDPOINTS
# ==========================================

@app.get("/config/coins", response_model=List[CoinConfig])
async def get_coin_config():
    """Get list of supported coins and their configurations."""
    return [
        CoinConfig(
            ticker="USDC",
            name="USD Coin",
            chains=["ethereum", "polygon", "avalanche"],
            enabled=True
        ),
        CoinConfig(
            ticker="USDT",
            name="Tether",
            chains=["ethereum", "tron", "bsc"],
            enabled=True
        ),
        CoinConfig(
            ticker="DAI",
            name="Dai Stablecoin",
            chains=["ethereum", "polygon"],
            enabled=True
        ),
        CoinConfig(
            ticker="BUSD",
            name="Binance USD",
            chains=["ethereum", "bsc"],
            enabled=True
        ),
    ]


@app.get("/config/chains", response_model=List[ChainConfig])
async def get_chain_config():
    """Get list of supported chains and their configurations."""
    return [
        ChainConfig(
            name="ethereum",
            finality_time_seconds=768,  # ~64 blocks * 12s
            block_time_seconds=12.0,
            enabled=True
        ),
        ChainConfig(
            name="polygon",
            finality_time_seconds=256,  # ~128 blocks * 2s
            block_time_seconds=2.0,
            enabled=True
        ),
        ChainConfig(
            name="avalanche",
            finality_time_seconds=2,  # Near-instant
            block_time_seconds=2.0,
            enabled=True
        ),
    ]


# ==========================================
# WEBSOCKET ENDPOINT
# ==========================================

@app.websocket("/ws/risk")
async def websocket_risk(websocket: WebSocket, coin: str):
    """
    WebSocket for real-time risk updates.
    
    Client receives updates when:
    - New risk score calculated
    - Alert triggered
    - Configuration changed
    """
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        logger.info(f"📡 WebSocket connected for {coin}")
        
        # Send initial state
        await websocket.send_json({
            "type": "connected",
            "coin": coin,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back for now (TODO: handle client commands)
            await websocket.send_json({
                "type": "echo",
                "message": data
            })
            
    except WebSocketDisconnect:
        logger.info(f"📡 WebSocket disconnected for {coin}")
        websocket_connections.remove(websocket)


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

async def broadcast_risk_update(coin: str, risk_data: dict):
    """Broadcast risk update to all connected WebSocket clients."""
    dead_connections = []
    
    for ws in websocket_connections:
        try:
            await ws.send_json({
                "type": "risk_update",
                "data": risk_data,
                "timestamp": datetime.utcnow().isoformat()
            })
        except:
            dead_connections.append(ws)
    
    # Remove dead connections
    for ws in dead_connections:
        websocket_connections.remove(ws)


# ==========================================
# HEALTH ENDPOINT
# ==========================================

@app.get("/health")
async def health_check():
    """API health check."""
    return {
        "status": "healthy",
        "ml_available": predictor is not None,
        "logger_available": logger_client is not None,
        "timestamp": datetime.utcnow().isoformat()
    }
