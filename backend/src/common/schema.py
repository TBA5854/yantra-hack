"""
Unified schema for multi-chain stablecoin risk events.
Includes full Temporal Confidence Score (TCS) support.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class FinalityTier(Enum):
    """Three-tier finality classification."""
    TIER1 = "tier1"  # 0.3 confidence - "probable"
    TIER2 = "tier2"  # 0.8 confidence - "highly likely"
    TIER3 = "tier3"  # 1.0 confidence - "final"


class WindowState(Enum):
    """Window state machine states."""
    OPEN = "OPEN"              # Accepting new events
    PROVISIONAL = "PROVISIONAL"  # Closed for new events, awaiting finality
    FINAL = "FINAL"            # All events finalized, immutable


class AggregationLevel(Enum):
    """Level of data aggregation."""
    RAW = "raw"              # Single event from single source
    SOURCE = "source"        # Aggregated across time for single source
    CROSS_SOURCE = "cross_source"  # Aggregated across sources for single chain
    CROSS_CHAIN = "cross_chain"    # Aggregated across chains


@dataclass
class ConfidenceBreakdown:
    """Detailed breakdown of TCS calculation components."""
    finality_weight: float      # Weighted avg of event finality confidences
    chain_confidence: float     # Min finality across all chains
    completeness: float         # Fraction of expected sources present
    staleness_penalty: float    # Penalty for data age
    temporal_confidence: float  # Final TCS = (f * c * comp) / stale


@dataclass
class RiskEvent:
    """
    Unified event schema for all risk data across chains and sources.

    This schema supports:
    - Multi-chain data (Ethereum, Arbitrum, Solana)
    - Multi-source data (price, liquidity, supply, volatility, sentiment)
    - Temporal Confidence Scoring (TCS)
    - Reorg-aware event versioning
    - Window state machine tracking
    - Cross-chain aggregation
    """

    # ============================================
    # CORE IDENTITY FIELDS (Required)
    # ============================================

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique identifier for this event (persistent across versions)."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when the event was observed/aggregated."""

    coin: str = ""
    """Stablecoin symbol (e.g., 'USDC', 'USDT', 'DAI')."""

    chain: str = ""
    """Blockchain name (e.g., 'ethereum', 'arbitrum', 'solana')."""

    source: str = ""
    """Data source identifier (e.g., 'coingecko', 'uniswap_v3', 'chainlink')."""

    # ============================================
    # DATA PAYLOAD FIELDS (Optional - depends on source)
    # ============================================

    price: Optional[float] = None
    """Current price in USD."""

    volume: Optional[float] = None
    """24h trading volume in USD."""

    liquidity_depth: Optional[float] = None
    """Available liquidity depth (e.g., $1M slippage test)."""

    net_supply_change: Optional[float] = None
    """Net change in circulating supply (mints - burns)."""

    market_volatility: Optional[float] = None
    """Market volatility metric (e.g., 24h price stddev)."""

    sentiment_score: Optional[float] = None
    """Sentiment analysis score (-1.0 to +1.0)."""

    # ============================================
    # FINALITY TRACKING FIELDS
    # ============================================

    block_number: Optional[int] = None
    """Block number where on-chain event occurred (if applicable)."""

    tx_hash: Optional[str] = None
    """Transaction hash for on-chain events (if applicable)."""

    confirmation_count: int = 0
    """Number of block confirmations (for on-chain events)."""

    finality_tier: str = FinalityTier.TIER1.value
    """Current finality tier: tier1 (0.3), tier2 (0.8), tier3 (1.0)."""

    is_finalized: bool = False
    """True if event has reached tier3 (irreversible)."""

    finality_timestamp: Optional[datetime] = None
    """Timestamp when event reached tier3."""

    # ============================================
    # TEMPORAL CONFIDENCE SCORE (TCS) FIELDS
    # ============================================

    temporal_confidence: float = 0.3
    """
    Temporal Confidence Score (0.0 - 1.0).
    TCS = (finality_weight * chain_confidence * completeness) / staleness_penalty
    """

    confidence_breakdown: Optional[Dict[str, float]] = None
    """
    Detailed breakdown of TCS calculation:
    {
        'finality_weight': float,
        'chain_confidence': float,
        'completeness': float,
        'staleness_penalty': float
    }
    """

    # ============================================
    # WINDOW & AGGREGATION FIELDS
    # ============================================

    window_id: str = ""
    """Identifier for the time window (e.g., '2024-01-15T12:00:00')."""

    window_state: str = WindowState.OPEN.value
    """Current state: OPEN, PROVISIONAL, or FINAL."""

    window_start: Optional[datetime] = None
    """Start time of the time window."""

    window_end: Optional[datetime] = None
    """End time of the time window."""

    aggregation_level: str = AggregationLevel.RAW.value
    """Aggregation level: raw, source, cross_source, cross_chain."""

    aggregated_from: List[str] = field(default_factory=list)
    """List of event_ids that were aggregated to produce this event."""

    # ============================================
    # REORG & VERSIONING FIELDS
    # ============================================

    event_version: int = 1
    """Version number (increments on reorg corrections)."""

    invalidated: bool = False
    """True if this event was invalidated by a reorg."""

    replacement_event_id: Optional[str] = None
    """If invalidated, points to the corrected event_id."""

    reorg_detected_at: Optional[datetime] = None
    """Timestamp when reorg was detected (if applicable)."""

    original_block_number: Optional[int] = None
    """Original block number before reorg (if applicable)."""

    # ============================================
    # QUALITY METRICS
    # ============================================

    is_outlier: bool = False
    """True if flagged as statistical outlier."""

    quality_score: float = 1.0
    """Data quality score (0.0 - 1.0)."""

    deduplication_count: int = 0
    """Number of duplicate events merged into this one."""

    # ============================================
    # METADATA
    # ============================================

    source_importance: float = 1.0
    """Importance weight of this data source (from config)."""

    processing_latency_ms: Optional[float] = None
    """Time from event observation to processing completion."""

    tags: Dict[str, Any] = field(default_factory=dict)
    """Arbitrary metadata tags."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {}
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if isinstance(value, datetime):
                result[field_name] = value.isoformat()
            elif isinstance(value, Enum):
                result[field_name] = value.value
            else:
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskEvent':
        """Create RiskEvent from dictionary."""
        # Convert ISO strings back to datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if isinstance(data.get('finality_timestamp'), str):
            data['finality_timestamp'] = datetime.fromisoformat(data['finality_timestamp'])
        if isinstance(data.get('reorg_detected_at'), str):
            data['reorg_detected_at'] = datetime.fromisoformat(data['reorg_detected_at'])
        if isinstance(data.get('window_start'), str):
            data['window_start'] = datetime.fromisoformat(data['window_start'])
        if isinstance(data.get('window_end'), str):
            data['window_end'] = datetime.fromisoformat(data['window_end'])

        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def get_confidence_tier_value(self) -> float:
        """Get numeric confidence value for current finality tier."""
        tier_map = {
            FinalityTier.TIER1.value: 0.3,
            FinalityTier.TIER2.value: 0.8,
            FinalityTier.TIER3.value: 1.0
        }
        return tier_map.get(self.finality_tier, 0.0)

    def is_stale(self, max_age_sec: int = 600) -> bool:
        """Check if event is stale based on timestamp."""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age > max_age_sec

    def should_attest(self, min_tcs: float = 0.8) -> bool:
        """
        Check if event should be attested to blockchain.
        Only tier2+ events with high TCS are attested.
        """
        return (
            self.temporal_confidence >= min_tcs and
            self.finality_tier in [FinalityTier.TIER2.value, FinalityTier.TIER3.value] and
            not self.invalidated
        )


@dataclass
class AggregatedRiskSnapshot:
    """
    Cross-source and/or cross-chain aggregated risk snapshot.
    Produced by combining multiple RiskEvents in a time window.
    """

    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    coin: str = ""
    chains: List[str] = field(default_factory=list)
    window_id: str = ""
    window_state: str = WindowState.OPEN.value

    # Aggregated metrics
    avg_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    total_liquidity: Optional[float] = None
    total_volume: Optional[float] = None

    net_supply_change: Optional[float] = None
    market_volatility: Optional[float] = None
    sentiment_score: Optional[float] = None

    # TCS for the aggregated snapshot
    temporal_confidence: float = 0.0
    confidence_breakdown: Optional[Dict[str, float]] = None

    # Metadata
    num_events_aggregated: int = 0
    sources_included: List[str] = field(default_factory=list)
    event_ids: List[str] = field(default_factory=list)

    # Depeg alert
    is_depegged: bool = False
    depeg_severity: Optional[float] = None  # Distance from $1.00

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {}
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if isinstance(value, datetime):
                result[field_name] = value.isoformat()
            elif isinstance(value, Enum):
                result[field_name] = value.value
            else:
                result[field_name] = value
        return result
