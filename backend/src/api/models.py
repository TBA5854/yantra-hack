"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classification."""
    MINIMAL = "MINIMAL"      # 0-20
    LOW = "LOW"              # 20-40
    ELEVATED = "ELEVATED"    # 40-60
    HIGH = "HIGH"            # 60-80
    CRITICAL = "CRITICAL"    # 80-100


class WindowState(str, Enum):
    """Windowing state for aggregation."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    FINAL = "FINAL"


class ChainFinality(BaseModel):
    """Chain finality information."""
    chain: str
    finality_tier: int = Field(..., ge=1, le=3)
    block_confirmations: int
    is_finalized: bool


class StressBreakdown(BaseModel):
    """Stress factor breakdown."""
    price_volatility: float = Field(..., ge=0, le=100)
    peg_deviation: float = Field(..., ge=0, le=100)
    velocity: float = Field(..., ge=0, le=100)
    market_correlation: float = Field(..., ge=0, le=100)


class RiskState(BaseModel):
    """Current risk state response."""
    coin: str
    chain: str
    timestamp: datetime
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    risk_rating: str  # AAA, AA, A, B, C
    tcs: float = Field(..., ge=0, le=1)
    window_state: WindowState
    stress_breakdown: StressBreakdown
    chain_finality_list: List[ChainFinality]
    
    # ML-specific fields
    ml_enabled: bool = True
    models: Optional[Dict[str, Any]] = None
    explainability: Optional[Dict[str, Any]] = None


class RiskSnapshot(BaseModel):
    """Historical risk data point."""
    timestamp: datetime
    risk_score: float
    tcs: float
    window_state: WindowState


class RiskHistory(BaseModel):
    """Historical risk data response."""
    coin: str
    chain: str
    from_time: datetime
    to_time: datetime
    interval: str
    snapshots: List[RiskSnapshot]


class Alert(BaseModel):
    """On-chain attested alert."""
    id: str
    timestamp: datetime
    coin: str
    chain: str
    severity: str  # info, warning, critical
    risk_score: float
    rating: str
    tcs_score: float
    tx_hash: Optional[str] = None
    attested: bool = False
    message: str


class AlertDetail(Alert):
    """Detailed alert with full prediction data."""
    models: Dict[str, Any]
    explainability: Dict[str, Any]
    blockchain_verification: Optional[Dict[str, Any]] = None


class AlertList(BaseModel):
    """List of alerts with pagination."""
    total: int
    alerts: List[Alert]
    limit: int
    offset: int


class CoinConfig(BaseModel):
    """Coin configuration."""
    ticker: str
    name: str
    chains: List[str]
    enabled: bool


class ChainConfig(BaseModel):
    """Chain configuration."""
    name: str
    finality_time_seconds: int
    block_time_seconds: float
    enabled: bool


class WSMessage(BaseModel):
    """WebSocket message."""
    type: str  # risk_update, alert, config_change
    data: Dict[str, Any]
    timestamp: datetime
