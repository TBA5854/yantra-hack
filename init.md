Multi-Chain Stablecoin Risk Intelligence Platform - Implementation Plan
Context
Building an institutional-grade distributed risk monitoring platform for stablecoins across multiple chains with meta-confidence quantification.
Vision: Not just a data pipeline, but a production-ready, multi-chain, shard-capable streaming intelligence platform that understands its own epistemic uncertainty.
Current State: Empty /data directory in web3 project. Frontend dashboard exists with mock data at /frontend.
Deliverable: 4-layer progressive architecture demonstrating enterprise-scale thinking while remaining implementable.

🏗️ Four-Layer Progressive Architecture
Layer 1: Perfected Single-Coin Core (Foundation)
    • Scope: USDC on Ethereum only
    • Purpose: Bulletproof foundation with full data quality pipeline
    • Key: Everything must work flawlessly before expanding
Layer 2: Multi-Coin Parallel Monitoring
    • Scope: USDC, USDT, DAI, BUSD on Ethereum
    • Purpose: Generalize core to ecosystem-level monitoring
    • Key: Isolated coin contexts, no shared mutable state
Layer 3: Cross-Chain Synchronization
    • Scope: Coins across Ethereum + Arbitrum (+ Solana optional)
    • Purpose: Handle heterogeneous finality and temporal aggregation
    • Key: Chain-specific confirmation thresholds, reorg awareness
Layer 4: Sharded Scaling Simulation
    • Scope: Logical feature-based sharding (price/liquidity/supply shards)
    • Purpose: Demonstrate horizontal scalability architecture
    • Key: Runs locally but structured like distributed system

🧠 Core Innovation: Temporal Confidence Score (TCS)
The Critical Insight: Cross-chain temporal ordering with heterogeneous finality is the single biggest technical risk. We solve this with meta-confidence quantification.
TCS Formula
TCS = (finality_weight * confidence_chains * completeness) / staleness_penalty
Components
    1. Finality Weight: Per-event confidence based on confirmation tier
    2. Cross-Chain Confidence: Min of all chain finality levels (weakest link)
    3. Completeness: Ratio of present vs expected data sources
    4. Staleness Penalty: Age-based confidence degradation
    5. Reorg History Prior: Bayesian adjustment for chain instability
Three-Tier Finality System
Tier 1: Real-Time Monitoring (Low Finality)
    • Ethereum: ≥ 1 confirmation
    • Arbitrum: Soft commitment
    • Solana: Confirmed
    • Confidence: 0.3
    • Use: Live risk estimation
Tier 2: Probabilistic Confidence (Medium Finality)
    • Ethereum: ≥ 12 confirmations
    • Arbitrum: Batch posted
    • Solana: Confirmed
    • Confidence: 0.8
    • Use: High-confidence alerts
Tier 3: Canonical Finalized (High Finality)
    • Ethereum: ≥ 64 confirmations
    • Arbitrum: L1 finalization
    • Solana: Finalized
    • Confidence: 1.0
    • Use: Immutable attestations
Reorg-Aware Event Versioning
Events are mutable until finalized. We emit correction events on reorgs:
{
  "event_id": "tx_abc123",
  "status": "invalidated",
  "reason": "chain_reorg",
  "replacement_event_id": "tx_def456"
}
Window State Machine
Aggregation windows have states:
    • OPEN: Actively collecting events
    • PROVISIONAL: Closed but contains unfinalized events
    • FINAL: All events finalized, safe for attestation

🎯 Enhanced Features (Beyond Original Spec)
    1. ✅ Sentiment Analysis: 6th data source (Twitter/Reddit sentiment)
    2. ✅ Schema Enforcement: Strict validation prevents malformed data
    3. ✅ Time Normalization: All timestamp formats → UTC datetime
    4. ✅ Deduplication: Sliding window dedup handles retries and reorgs
    5. ✅ Outlier Clipping: Price (0.80-1.20) and sentiment (-1.0, 1.0) range enforcement
    6. ✅ Backpressure Handling: Exponential backoff on API failures
    7. ✅ Enhanced Replay Controls: Pause/resume/jump-to-date for demos
    8. ✅ Time Bucket Alignment: Floor timestamps to window boundaries
    9. ✅ Multi-Chain Support: Ethereum, Arbitrum, Solana with chain-specific finality
    10. ✅ Temporal Confidence Score: Meta-awareness of risk assessment quality
    11. ✅ Reorg-Aware Aggregation: Event versioning and correction handling
    12. ✅ Feature-Based Sharding: Logical horizontal scaling architecture
    13. ✅ Confidence Decay Functions: Time-based confidence evolution
    14. ✅ Alert Upgrade Logic: Provisional → Probable → Confirmed progression
Architecture: Multi-layer, multi-chain, meta-confident pipeline:
    • Source Adapters → Normalization → Quality → Finality Tracking → TCS Computation → Time Alignment → Cross-Chain Aggregation → Sharded Output

Architecture Overview
Multi-Layer, Multi-Chain, Meta-Confident Pipeline
┌──────────────────────────────────────────────────────────┐
│                   CONFIG LAYER                            │
│  MODE = historical | live                                 │
│  COINS = [USDC, USDT, DAI, BUSD]                         │
│  CHAINS = [ethereum, arbitrum, solana]                   │
│  FINALITY_TIERS = {tier1, tier2, tier3}                  │
└──────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ COIN A   │    │ COIN B   │    │ COIN N   │
        │ ETH+ARB  │    │ ETH+ARB  │    │ ETH+ARB  │
        │ +SOL     │    │ +SOL     │    │ +SOL     │
        └────┬─────┘    └────┬─────┘    └────┬─────┘
             │               │                │
             └───────────────┼────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│         SHARDED SOURCE ADAPTER LAYER (by feature)        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │ Price Shard │ │ Liq. Shard  │ │ Supply Shard│        │
│  │ • CoinGecko │ │ • DeFiLlama │ │ • Web3 Events│       │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
│  ┌─────────────┐ ┌─────────────┐                        │
│  │ Vol. Shard  │ │ Sent. Shard │                        │
│  │ • BTC Calc  │ │ • Twitter   │                        │
│  └─────────────┘ └─────────────┘                        │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│          RAW EVENT NORMALIZATION + CHAIN TAGGING         │
│  • Timestamp → UTC datetime                              │
│  • Schema enforcement & validation                       │
│  • Type coercion (str→float, ms→seconds)                │
│  • Chain identification & block number extraction        │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│         FINALITY TRACKING + CONFIRMATION MONITOR         │
│  • Track confirmations per chain (ETH, ARB, SOL)         │
│  • Assign finality tier (tier1/tier2/tier3)              │
│  • Monitor for reorgs (block hash verification)          │
│  • Emit correction events on invalidation                │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│          DATA QUALITY LAYER + REORG HANDLING             │
│  • Deduplication (timestamp + source + coin + chain)     │
│  • Outlier clipping (price: 0.80-1.20)                  │
│  • Reorg-aware event versioning                          │
│  • Backpressure & retry logic                            │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│         TIME BUCKET ALIGNMENT + COMPLETENESS CHECK       │
│  • Floor to nearest 1m/5m window                         │
│  • Track expected vs present sources                     │
│  • Calculate staleness penalty                           │
│  • Forward-fill for sparse streams                       │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│           TEMPORAL CONFIDENCE SCORE (TCS) ENGINE         │
│  • Finality weight calculation                           │
│  • Cross-chain confidence (min of chains)                │
│  • Completeness factor                                   │
│  • Staleness penalty                                     │
│  • Reorg history prior (Bayesian)                        │
│  ──────────────────────────────────────                  │
│  Output: TCS ∈ [0.0, 1.0]                                │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│        CROSS-CHAIN AGGREGATION + WINDOW STATE MACHINE    │
│  • Per-coin aggregation across chains                    │
│  • Window states: OPEN → PROVISIONAL → FINAL             │
│  • Confidence-gated state transitions                    │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│         UNIFIED EVENT STREAM (Pathway) + METADATA        │
│  Schema:                                                  │
│    timestamp, coin, chain,                                │
│    price, volume, liquidity_depth,                        │
│    net_supply_change, market_volatility, sentiment_score,│
│    finality_tier, temporal_confidence,                    │
│    window_state, confidence_breakdown                     │
└──────────────────────────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│          CONFIDENCE-GATED PERSISTENCE LAYER              │
│  • Provisional Cache (TCS < 0.6)                         │
│  • Alert Log (TCS ≥ 0.6)                                 │
│  • Immutable Attestation (TCS ≥ 0.8 + FINAL state)      │
│  • JSONL rolling file (all events)                       │
│  • Console output (debug)                                 │
└──────────────────────────────────────────────────────────┘
Unified Multi-Chain Schema with TCS
All data sources normalize to:
# Core Fields (Required)
timestamp: datetime (UTC)          # Ingestion timestamp, enforced
coin: str                          # USDT | USDC | DAI | BUSD
chain: str                         # ethereum | arbitrum | solana
source: str                        # coingecko | defillama | web3 | sentiment

# Data Fields (Optional)
price: Optional[float]             # Nullable
volume: Optional[float]            # Nullable
liquidity_depth: Optional[float]   # Nullable
net_supply_change: Optional[float] # Nullable
market_volatility: Optional[float] # Nullable
sentiment_score: Optional[float]   # Range [-1.0, 1.0]

# Finality Tracking Fields
block_number: Optional[int]        # On-chain block number (if applicable)
tx_hash: Optional[str]             # Transaction hash (if applicable)
confirmation_count: int            # Number of confirmations (default: 0)
finality_tier: str                 # tier1 | tier2 | tier3
is_finalized: bool                 # True if tier3, else False

# Temporal Confidence Fields
temporal_confidence: float         # TCS ∈ [0.0, 1.0]
confidence_breakdown: dict         # {finality: ..., cross_chain: ..., completeness: ..., staleness: ...}

# Window & Aggregation Fields
window_id: str                     # Time bucket identifier (e.g., "2024-01-15T12:05:00")
window_state: str                  # OPEN | PROVISIONAL | FINAL
aggregation_level: str             # single_chain | cross_chain

# Reorg & Versioning Fields
event_id: str                      # Unique event identifier
event_version: int                 # Increments on corrections (default: 1)
invalidated: bool                  # True if reorg invalidated this event
replacement_event_id: Optional[str]# Points to corrected event (if invalidated)
Validation Rules:
    • timestamp must be valid UTC datetime
    • coin must be in STABLECOINS list
    • chain must be in SUPPORTED_CHAINS list
    • price if present: 0.80 ≤ price ≤ 1.20 (outlier clipping)
    • sentiment_score if present: -1.0 ≤ score ≤ 1.0
    • temporal_confidence must be in [0.0, 1.0]
    • finality_tier must be in {"tier1", "tier2", "tier3"}
    • window_state must be in {"OPEN", "PROVISIONAL", "FINAL"}

Directory Structure (4-Layer Architecture)
/home/tba/projects/web3/data/
├── ingestion/                      # Core pipeline code
│   ├── __init__.py
│   ├── schema.py                   # Multi-chain unified schema with TCS
│   ├── pipeline.py                 # 4-layer orchestrator (progressive)
│   │
│   ├── historical/                 # Historical replay (Layer 1 foundation)
│   │   ├── __init__.py
│   │   ├── csv_reader.py           # Multi-file CSV loader
│   │   ├── replay_engine.py        # Time-based replay controller
│   │   ├── time_scaler.py          # Speed multiplier logic
│   │   └── replay_controller.py    # Pause/resume/jump controls
│   │
│   ├── live/                       # Live streaming connectors (Layer 1)
│   │   ├── __init__.py
│   │   ├── base_connector.py       # Abstract async connector
│   │   ├── coingecko.py            # Price/volume (60s)
│   │   ├── defillama.py            # Liquidity (2-5min)
│   │   ├── web3_events.py          # Mint/burn events (multi-chain)
│   │   ├── volatility.py           # BTC volatility calc
│   │   ├── sentiment.py            # Sentiment analyzer (Twitter/Reddit)
│   │   ├── scheduler.py            # Async task orchestration
│   │   └── backpressure.py         # Rate limit & retry logic
│   │
│   ├── multi_chain/                # Multi-chain support (Layer 3)
│   │   ├── __init__.py
│   │   ├── ethereum.py             # Ethereum-specific finality rules
│   │   ├── arbitrum.py             # Arbitrum L2 finality (L1 batch tracking)
│   │   ├── solana.py               # Solana commitment levels
│   │   ├── finality_tracker.py     # Track confirmations per chain
│   │   ├── reorg_detector.py       # Monitor block hash changes
│   │   ├── chain_config.py         # Per-chain confirmation thresholds
│   │   └── rpc_manager.py          # Multi-chain RPC connection pool
│   │
│   ├── normalization/              # Raw event normalization layer
│   │   ├── __init__.py
│   │   ├── timestamp_normalizer.py # UTC conversion, type handling
│   │   ├── schema_enforcer.py      # Strict schema validation
│   │   ├── type_coercer.py         # String→float, ms→seconds
│   │   └── chain_tagger.py         # Extract chain metadata from events
│   │
│   ├── quality/                    # Data quality layer
│   │   ├── __init__.py
│   │   ├── deduplicator.py         # Dedup by (timestamp, source, coin, chain)
│   │   ├── outlier_clipper.py      # Price range enforcement
│   │   ├── missing_detector.py     # Missing value alerts
│   │   ├── validator.py            # Final validation before output
│   │   └── reorg_handler.py        # Emit correction events on reorg
│   │
│   ├── tcs/                        # Temporal Confidence Score engine
│   │   ├── __init__.py
│   │   ├── tcs_calculator.py       # Main TCS computation logic
│   │   ├── finality_weights.py     # Per-tier confidence mapping
│   │   ├── completeness_tracker.py # Expected vs present sources
│   │   ├── staleness_calculator.py # Age-based confidence penalty
│   │   └── reorg_history.py        # Bayesian prior from reorg rate
│   │
│   ├── aggregation/                # Cross-chain aggregation (Layer 3)
│   │   ├── __init__.py
│   │   ├── cross_chain_aggregator.py # Per-coin aggregation across chains
│   │   ├── window_state_machine.py   # OPEN → PROVISIONAL → FINAL
│   │   └── confidence_gater.py       # TCS-based state transitions
│   │
│   ├── sharding/                   # Logical sharding (Layer 4)
│   │   ├── __init__.py
│   │   ├── feature_shards.py       # Price/Liquidity/Supply shards
│   │   ├── coin_shards.py          # Per-coin partitioning
│   │   ├── shard_coordinator.py    # Shard output aggregation
│   │   └── shard_router.py         # Route events to correct shard
│   │
│   └── pathway/                    # Pathway streaming logic
│       ├── __init__.py
│       ├── stream_builder.py       # Build multi-chain streaming tables
│       ├── joiners.py              # Time-windowed joins with TCS
│       ├── transformers.py         # Apply normalization + TCS
│       ├── time_aligner.py         # Time bucket alignment
│       └── output_handlers.py      # Confidence-gated persistence
│
├── historical/                     # Historical CSV data (multi-chain)
│   ├── ethereum/                   # Ethereum historical data
│   │   ├── price.csv
│   │   ├── liquidity.csv
│   │   ├── supply.csv
│   │   └── sentiment.csv
│   ├── arbitrum/                   # Arbitrum historical data
│   │   ├── price.csv
│   │   ├── liquidity.csv
│   │   └── supply.csv
│   ├── solana/                     # Solana historical data (optional)
│   │   ├── price.csv
│   │   └── supply.csv
│   └── volatility.csv              # BTC volatility (chain-agnostic)
│
├── output/                         # Layered output
│   ├── provisional/                # TCS < 0.6 (fast but uncertain)
│   │   └── provisional_stream.jsonl
│   ├── alerts/                     # TCS ≥ 0.6 (high confidence)
│   │   └── alert_stream.jsonl
│   ├── finalized/                  # TCS ≥ 0.8 + FINAL state
│   │   └── canonical_stream.jsonl
│   └── unified_stream.jsonl        # All events (debug)
│
├── scripts/                        # Utilities
│   ├── generate_sample_data.py     # Generate multi-chain CSV dataset
│   ├── test_connectors.py          # Test API connectivity per chain
│   ├── test_finality_tracking.py   # Test confirmation monitoring
│   ├── test_tcs_calculator.py      # Test TCS computation
│   └── run_pipeline.py             # Main entry point (layer-aware)
│
├── config.py                       # Multi-chain configuration management
├── requirements.txt                # Python dependencies (multi-chain)
└── .env.example                    # Environment template (per-chain RPCs)

Critical Files Implementation
1. /home/tba/projects/web3/data/config.py
Purpose: Environment-driven configuration for entire pipeline.
Key Settings:
MODE = "historical" or "live"           # Operating mode
REPLAY_SPEED = 10.0                     # Historical speed multiplier
STABLECOINS = ["USDT", "USDC", "DAI", "BUSD"]
COINGECKO_INTERVAL = 60                 # seconds
DEFILLAMA_INTERVAL = 180
PATHWAY_WINDOW_DURATION = 300           # 5-minute windows
HISTORICAL_DATA_DIR = "data/historical"
OUTPUT_FILE = "data/output/unified_stream.jsonl"
Reads from .env file with fallback defaults.

2. /home/tba/projects/web3/data/ingestion/schema.py
Purpose: Define the contract between all pipeline components.
Core Class:
@dataclass
class StablecoinDataPoint:
    timestamp: datetime
    coin: str
    price: Optional[float] = None
    volume: Optional[float] = None
    liquidity_depth: Optional[float] = None
    net_supply_change: Optional[float] = None
    market_volatility: Optional[float] = None

    def to_pathway_schema(self) -> dict:
        # Convert to Pathway table schema

    def validate(self) -> bool:
        # Ensure timestamp exists, coin is valid
Critical: All data sources must output this schema.

3. /home/tba/projects/web3/data/ingestion/historical/replay_engine.py
Purpose: Replay historical CSV files with time-scaled delays.
Key Features:
    • Merge multiple CSVs (price, liquidity, supply, volatility, sentiment) by timestamp
    • Emit data points in chronological order
    • Sleep scaled by REPLAY_SPEED (10x = 10 times faster than real-time)
    • Generator-based async streaming
Pattern:
class ReplayEngine:
    def __init__(self, data_dir: Path, speed: float, controller: ReplayController)

    async def stream_events(self) -> AsyncIterator[StablecoinDataPoint]:
        # 1. Load all CSVs
        # 2. Merge by timestamp (use heapq)
        # 3. For each row:
        #    - Check if paused (controller.is_paused)
        #    - Sleep until next event (scaled)
        #    - Yield StablecoinDataPoint
Time Scaling:
# If next event is 60 seconds later in data
# and REPLAY_SPEED = 10
# then sleep for 60/10 = 6 seconds real-time

3b. /home/tba/projects/web3/data/ingestion/historical/replay_controller.py
Purpose: Enhanced replay control for demos and testing.
Features:
class ReplayController:
    def __init__(self):
        self.is_paused = False
        self.current_time = None
        self.speed = 1.0

    def pause(self):
        """Pause replay without losing state"""

    def resume(self):
        """Resume from paused state"""

    def jump_to_date(self, target: datetime):
        """Skip to specific timestamp in data"""

    def set_speed(self, multiplier: float):
        """Change replay speed dynamically"""
Use Case: During demo, pause at crisis point, explain, then resume.

4. /home/tba/projects/web3/data/ingestion/live/coingecko.py
Purpose: Fetch price and volume from CoinGecko API every 60 seconds.
Implementation:
class CoinGeckoConnector(BaseConnector):
    ENDPOINT = "https://api.coingecko.com/api/v3/simple/price"

    async def fetch(self) -> List[StablecoinDataPoint]:
        # GET price?ids=tether,usd-coin,dai,binance-usd
        #     &vs_currencies=usd
        #     &include_24hr_vol=true

        # Transform response to StablecoinDataPoint[]
        # Each coin gets its own data point with timestamp=now()
Rate Limiting: Free tier = 10-50 calls/min. Single batch call for all 4 coins.

5. /home/tba/projects/web3/data/ingestion/live/web3_events.py
Purpose: Listen for mint/burn Transfer events from stablecoin contracts.
Pattern:
class Web3EventConnector(BaseConnector):
    def __init__(self, contracts: Dict[str, str], rpc_url: str):
        # contracts = {"USDT": "0xdac17f...", ...}
        # Use Web3.py to subscribe to logs

    async def fetch(self) -> List[StablecoinDataPoint]:
        # Filter Transfer events:
        #   - Mint: from = 0x0
        #   - Burn: to = 0x0
        # Calculate net_supply_change = mints - burns
        # Return data point with net_supply_change field
Polling Strategy: Check new blocks every 15 seconds.

5b. /home/tba/projects/web3/data/ingestion/live/sentiment.py
Purpose: Analyze social sentiment from Twitter/Reddit about stablecoins.
Implementation Options:
Option 1: Twitter API v2 (requires API access):
class SentimentAnalyzer(BaseConnector):
    async def fetch(self) -> List[StablecoinDataPoint]:
        # Search tweets mentioning "USDT depeg" OR "Tether concerns"
        # Use TextBlob/VADER for sentiment scoring
        # Aggregate to single score per coin per interval
Option 2: Reddit API (via PRAW):
# Monitor r/CryptoCurrency, r/DeFi
# Search posts/comments mentioning coin names
# Sentiment analysis with VADER
Option 3: Alternative Sentiment APIs:
    • LunarCrush API (crypto-specific sentiment)
    • Santiment API
    • TheTIE.io
Scoring:
    • Range: -1.0 (very negative) to +1.0 (very positive)
    • Update interval: 5-10 minutes (sentiment changes slower than price)
    • Aggregate multiple sources if available
Simplified Approach for MVP:
class SimpleSentimentAnalyzer(BaseConnector):
    """Use free alternative or mock sentiment for testing"""

    async def fetch(self) -> List[StablecoinDataPoint]:
        # For MVP: Generate synthetic sentiment
        # Later: Integrate real sentiment API
        sentiment_score = self._calculate_sentiment(coin)
        return [StablecoinDataPoint(
            timestamp=datetime.now(UTC),
            coin=coin,
            sentiment_score=sentiment_score,
            source="sentiment"
        )]
Critical: Sentiment is sparse - only emit when significant change detected (threshold: ±0.1 change).

6. /home/tba/projects/web3/data/ingestion/normalization/schema_enforcer.py
Purpose: Strict schema validation before data enters pipeline.
Problem: APIs change formats silently, breaking downstream.
Solution:
class SchemaEnforcer:
    REQUIRED_FIELDS = ["timestamp", "coin", "source"]
    OPTIONAL_FIELDS = ["price", "volume", "liquidity_depth",
                       "net_supply_change", "market_volatility",
                       "sentiment_score"]
    VALID_COINS = ["USDT", "USDC", "DAI", "BUSD"]

    def enforce(self, raw_data: Dict) -> StablecoinDataPoint:
        # 1. Check required fields exist
        if not all(field in raw_data for field in self.REQUIRED_FIELDS):
            raise SchemaViolation("Missing required fields")

        # 2. Validate coin
        if raw_data["coin"] not in self.VALID_COINS:
            raise SchemaViolation(f"Invalid coin: {raw_data['coin']}")

        # 3. Type coercion (see type_coercer.py)
        # 4. Return validated StablecoinDataPoint
Benefit: Pipeline fails fast on invalid data instead of corrupting downstream.

7. /home/tba/projects/web3/data/ingestion/normalization/timestamp_normalizer.py
Purpose: Normalize all timestamp formats to UTC datetime.
Problem: Different sources return:
    • ISO strings: "2024-01-15T12:00:00Z"
    • Unix seconds: 1705320000
    • Unix milliseconds: 1705320000000
    • Local timezone timestamps
Solution:
class TimestampNormalizer:
    def normalize(self, raw_timestamp: Any) -> datetime:
        # Try ISO string
        if isinstance(raw_timestamp, str):
            return datetime.fromisoformat(raw_timestamp.replace('Z', '+00:00'))

        # Try Unix timestamp (detect ms vs seconds)
        if isinstance(raw_timestamp, (int, float)):
            if raw_timestamp > 10**10:  # Likely milliseconds
                return datetime.fromtimestamp(raw_timestamp / 1000, tz=UTC)
            else:  # Likely seconds
                return datetime.fromtimestamp(raw_timestamp, tz=UTC)

        raise ValueError(f"Cannot normalize timestamp: {raw_timestamp}")
Enforcement: All timestamps converted to aware UTC datetime before entering Pathway.

8. /home/tba/projects/web3/data/ingestion/quality/deduplicator.py
Purpose: Remove duplicate events from retries, reorgs, and API quirks.
Deduplication Key: (timestamp, source, coin)
Implementation:
class Deduplicator:
    def __init__(self, window_size: timedelta = timedelta(minutes=10)):
        # Keep seen events for last 10 minutes (sliding window)
        self.seen = {}  # (timestamp, source, coin) -> event

    def deduplicate(self, event: StablecoinDataPoint) -> Optional[StablecoinDataPoint]:
        key = (event.timestamp, event.source, event.coin)

        # Clean old entries (older than window)
        self._cleanup_old_entries()

        # Check if seen
        if key in self.seen:
            logger.debug(f"Duplicate detected: {key}")
            return None  # Drop duplicate

        # Store and return
        self.seen[key] = event
        return event
Why This Matters:
    • Web3 events can re-emit during chain reorgs
    • API retries can cause duplicates
    • Without dedupe: supply change events counted twice → false alerts

9. /home/tba/projects/web3/data/ingestion/quality/outlier_clipper.py
Purpose: Clip obviously invalid values to prevent garbage data.
Rules:
class OutlierClipper:
    PRICE_MIN = 0.80
    PRICE_MAX = 1.20
    SENTIMENT_MIN = -1.0
    SENTIMENT_MAX = 1.0

    def clip(self, event: StablecoinDataPoint) -> StablecoinDataPoint:
        # Price clipping
        if event.price is not None:
            if event.price < self.PRICE_MIN or event.price > self.PRICE_MAX:
                logger.warning(f"Outlier price {event.price} clipped")
                event.price = None  # Drop outlier

        # Sentiment clipping
        if event.sentiment_score is not None:
            event.sentiment_score = max(
                self.SENTIMENT_MIN,
                min(self.SENTIMENT_MAX, event.sentiment_score)
            )

        # Volume sanity check (must be > 0)
        if event.volume is not None and event.volume < 0:
            event.volume = None

        return event
Rationale: API glitches can return price = $0.00 or $999. Clipping prevents false alarms.

10. /home/tba/projects/web3/data/ingestion/live/backpressure.py
Purpose: Handle API failures, rate limits, and retries gracefully.
Pattern:
class BackpressureHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def fetch_with_retry(self, fetch_fn: Callable) -> Any:
        for attempt in range(self.max_retries):
            try:
                return await fetch_fn()
            except RateLimitError as e:
                wait = self.base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Rate limited, retry in {wait}s")
                await asyncio.sleep(wait)
            except APIDownError as e:
                logger.error(f"API down: {e}")
                return None  # Return None, don't crash pipeline

        # All retries failed
        logger.error("Max retries exceeded")
        return None
Integration: Wrap all connector fetch() methods.
Benefit: Pipeline continues running even if one API is down.

11. /home/tba/projects/web3/data/ingestion/pathway/time_aligner.py
Purpose: Align events to time bucket boundaries for consistent joins.
Problem: Events arrive at:
    • 12:03:47
    • 12:04:12
    • 12:05:33
These won't join properly in 5-minute windows.
Solution: Floor timestamps to bucket boundaries.
class TimeAligner:
    def __init__(self, bucket_size: timedelta = timedelta(minutes=5)):
        self.bucket_size = bucket_size

    def align(self, timestamp: datetime) -> datetime:
        # Floor to nearest bucket
        # Example: 12:03:47 → 12:00:00 (5-minute bucket)
        epoch = datetime(1970, 1, 1, tzinfo=UTC)
        delta = (timestamp - epoch).total_seconds()
        bucket_seconds = self.bucket_size.total_seconds()
        aligned_delta = int(delta // bucket_seconds) * bucket_seconds
        return epoch + timedelta(seconds=aligned_delta)
Pathway Integration: Apply before joins.

12. /home/tba/projects/web3/data/ingestion/pathway/stream_builder.py
Purpose: Build Pathway streaming tables with full data quality pipeline.
Core Logic:
def build_unified_stream(mode: str):
    if mode == "historical":
        # Create Pathway input from replay engine
        raw_source = pw.io.python.read(
            ReplayEngine(...).stream_events(),
            schema=StablecoinDataPoint
        )

    elif mode == "live":
        # Create separate streams for each connector
        price_stream = pw.io.python.read(CoinGeckoConnector(...))
        liquidity_stream = pw.io.python.read(DeFiLlamaConnector(...))
        supply_stream = pw.io.python.read(Web3EventConnector(...))
        vol_stream = pw.io.python.read(VolatilityConnector(...))
        sentiment_stream = pw.io.python.read(SentimentAnalyzer(...))

        # Merge all sources
        raw_source = pw.Table.concat(
            price_stream,
            liquidity_stream,
            supply_stream,
            vol_stream,
            sentiment_stream
        )

    # === DATA QUALITY PIPELINE ===

    # 1. Normalization layer
    normalized = raw_source.select(
        timestamp=pw.apply(normalize_timestamp, pw.this.timestamp),
        coin=pw.apply(enforce_schema, pw.this)
        # ... all fields
    )

    # 2. Deduplication
    deduplicated = normalized.deduplicate(
        key=(pw.this.timestamp, pw.this.source, pw.this.coin)
    )

    # 3. Outlier clipping
    cleaned = deduplicated.select(
        **pw.apply(clip_outliers, pw.this)
    )

    # 4. Time bucket alignment
    aligned = cleaned.with_columns(
        timestamp=pw.apply(align_to_bucket, pw.this.timestamp)
    )

    # 5. Time-windowed joins (group sparse streams)
    unified = join_and_forward_fill(
        aligned,
        window_duration=300
    )

    # === OUTPUT ===
    pw.io.jsonlines.write(unified, OUTPUT_FILE)

    return unified

7. /home/tba/projects/web3/data/ingestion/pathway/joiners.py
Purpose: Time-windowed joins with forward-fill for sparse data.
Challenge:
    • Price updates every 60s
    • Liquidity updates every 2-5min
    • Supply changes are event-driven (irregular)
Solution: Join on 5-minute tumbling windows, forward-fill missing values.
def join_streams(price, liquidity, supply, volatility, window_duration):
    window = pw.temporal.tumbling(duration=window_duration)

    # Join price + liquidity
    joined = price.windowby(
        pw.this.timestamp, window
    ).join(
        liquidity.windowby(pw.this.timestamp, window),
        pw.left.coin == pw.right.coin,
        how="left"
    )

    # Forward-fill missing liquidity
    joined = joined.with_columns(
        liquidity_depth=pw.coalesce(
            pw.this.liquidity_depth,
            pw.this.prev.liquidity_depth
        )
    )

    # Repeat for supply and volatility
    # Return fully joined stream

8. /home/tba/projects/web3/data/scripts/generate_sample_data.py
Purpose: Generate realistic 30-day historical dataset for testing.
Output CSVs:
price.csv:
timestamp,coin,price,volume
2024-01-15T00:00:00Z,USDT,1.0001,52000000000
2024-01-15T01:00:00Z,USDT,0.9999,51800000000
...
liquidity.csv:
timestamp,coin,liquidity_depth
2024-01-15T00:00:00Z,USDT,8500000000
2024-01-15T00:05:00Z,USDT,8520000000
...
supply.csv (sparse, event-driven):
timestamp,coin,net_supply_change
2024-01-15T03:45:00Z,USDT,100000000
2024-01-15T09:22:00Z,USDT,-50000000
...
volatility.csv:
timestamp,market_volatility
2024-01-15T00:00:00Z,0.0234
2024-01-15T01:00:00Z,0.0241
...
sentiment.csv:
timestamp,coin,sentiment_score
2024-01-15T00:00:00Z,USDT,0.15
2024-01-15T00:10:00Z,USDT,0.12
2024-01-15T00:15:00Z,USDC,0.45
...
Generation Strategy:
    • Price: Random walk around $1.00 (±0.5%)
    • Volume: 40B-60B with daily patterns
    • Liquidity: 8B-10B with slow drift
    • Supply: Random mint/burn events (5-15 per day)
    • Volatility: Rolling stddev of synthetic BTC price
    • Sentiment: Sparse updates (every 5-10 minutes), range [-1.0, 1.0], with occasional negative spikes during crisis periods

9. /home/tba/projects/web3/data/scripts/run_pipeline.py
Purpose: Main entry point to start the pipeline.
#!/usr/bin/env python3
import asyncio
from ingestion.pipeline import DataPipeline
from config import MODE

async def main():
    pipeline = DataPipeline(mode=MODE)

    print(f"Starting pipeline in {MODE} mode...")

    if MODE == "historical":
        print(f"Replay speed: {REPLAY_SPEED}x")

    await pipeline.start()

if __name__ == "__main__":
    asyncio.run(main())
Usage:
# Historical mode (10x speed)
MODE=historical REPLAY_SPEED=10 python data/scripts/run_pipeline.py

# Live mode
MODE=live python data/scripts/run_pipeline.py

10. /home/tba/projects/web3/data/ingestion/pipeline.py
Purpose: Main orchestrator that switches between historical/live modes.
class DataPipeline:
    def __init__(self, mode: str):
        self.mode = mode
        self.pathway_graph = None

    async def start(self):
        if self.mode == "historical":
            await self._start_historical()
        elif self.mode == "live":
            await self._start_live()

    async def _start_historical(self):
        # Initialize ReplayEngine
        # Build Pathway graph from replay stream
        # Run computation
        pw.run()

    async def _start_live(self):
        # Initialize all connectors (CoinGecko, DeFiLlama, Web3, Volatility)
        # Build Pathway graph from live streams
        # Run computation
        pw.run()

Python Dependencies
/home/tba/projects/web3/data/requirements.txt:
# Streaming framework
pathway>=0.13.0

# Data processing
pandas>=2.2.0
numpy>=1.26.0
scipy>=1.11.0  # For statistical functions (TCS, volatility)

# Web3 and blockchain (multi-chain)
web3>=7.0.0
eth-abi>=5.0.0
solana>=0.30.0  # Solana Python SDK
solders>=0.18.0  # Solana types

# HTTP clients
httpx>=0.27.0
aiohttp>=3.10.0
websockets>=12.0  # For WebSocket RPC connections

# Sentiment analysis
vaderSentiment>=3.3.2
# Optional: textblob>=0.17.0
# Optional: praw>=7.7.0  # Reddit API

# Configuration
pydantic>=2.9.0
pydantic-settings>=2.6.0
python-dotenv>=1.0.0

# Utilities
python-dateutil>=2.9.0
pytz>=2024.1
cachetools>=5.3.0  # For RPC response caching
tenacity>=8.2.0  # For advanced retry logic

# Logging & Monitoring
structlog>=24.1.0
prometheus-client>=0.19.0  # Metrics export

# Multi-chain RPC providers (optional, for production)
# alchemy-sdk>=0.1.0
# infura-sdk>=0.1.0

# Testing
pytest>=8.3.0
pytest-asyncio>=0.24.0
pytest-cov>=6.0.0
pytest-mock>=3.12.0
freezegun>=1.4.0  # For time-based testing

# Development
black>=24.0.0
ruff>=0.6.0
mypy>=1.8.0

Configuration
/home/tba/projects/web3/data/.env.example:
# ========================================
# LAYER CONFIGURATION
# ========================================
ACTIVE_LAYERS=1,2,3,4  # Comma-separated: 1=single-coin, 2=multi-coin, 3=multi-chain, 4=sharded
PIPELINE_MODE=historical  # historical | live

# Historical replay settings
REPLAY_SPEED=10.0
HISTORICAL_DATA_DIR=data/historical

# ========================================
# MULTI-COIN CONFIGURATION (Layer 2)
# ========================================
STABLECOINS=USDC,USDT,DAI,BUSD

# ========================================
# MULTI-CHAIN CONFIGURATION (Layer 3)
# ========================================
CHAINS=ethereum,arbitrum  # ethereum, arbitrum, solana

# Ethereum RPC endpoints
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_WS_URL=wss://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_BACKUP_RPC=https://rpc.ankr.com/eth

# Arbitrum RPC endpoints
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ARBITRUM_WS_URL=wss://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Solana RPC endpoints (optional)
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_WS_URL=wss://api.mainnet-beta.solana.com

# ========================================
# FINALITY CONFIGURATION (Layer 3)
# ========================================
# Ethereum finality thresholds
ETHEREUM_TIER1_CONFIRMATIONS=1
ETHEREUM_TIER2_CONFIRMATIONS=12
ETHEREUM_TIER3_CONFIRMATIONS=64

# Arbitrum finality thresholds
ARBITRUM_TIER1_CONFIRMATIONS=1
ARBITRUM_TIER2_CONFIRMATIONS=10
ARBITRUM_L1_FINALITY_REQUIRED=true

# Solana commitment levels
SOLANA_TIER1_COMMITMENT=confirmed
SOLANA_TIER2_COMMITMENT=confirmed
SOLANA_TIER3_COMMITMENT=finalized

# ========================================
# TCS CONFIGURATION
# ========================================
TCS_ENABLED=true
TCS_MIN_CONFIDENCE_FOR_ALERT=0.6
TCS_MIN_CONFIDENCE_FOR_ATTESTATION=0.8
TCS_STALENESS_THRESHOLD_SECONDS=300
TCS_REORG_HISTORY_WINDOW_HOURS=24

# ========================================
# CONTRACT ADDRESSES
# ========================================
# Ethereum mainnet
ETHEREUM_USDT_CONTRACT=0xdac17f958d2ee523a2206206994597c13d831ec7
ETHEREUM_USDC_CONTRACT=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48
ETHEREUM_DAI_CONTRACT=0x6b175474e89094c44da98b954eedeac495271d0f
ETHEREUM_BUSD_CONTRACT=0x4fabb145d64652a948d72533023f6e7a623c7c53

# Arbitrum One
ARBITRUM_USDC_CONTRACT=0xaf88d065e77c8cC2239327C5EDb3A432268e5831
ARBITRUM_USDT_CONTRACT=0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9

# Solana (optional)
SOLANA_USDC_MINT=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

# ========================================
# API KEYS
# ========================================
COINGECKO_API_KEY=
DEFILLAMA_API_KEY=
INFURA_PROJECT_ID=
ALCHEMY_API_KEY=

# ========================================
# UPDATE INTERVALS (seconds)
# ========================================
COINGECKO_INTERVAL=60
DEFILLAMA_INTERVAL=180
WEB3_POLL_INTERVAL=15
VOLATILITY_INTERVAL=300
SENTIMENT_INTERVAL=300

# ========================================
# PATHWAY CONFIGURATION
# ========================================
PATHWAY_WINDOW_DURATION=300  # 5 minutes
PATHWAY_GRACE_PERIOD=30      # Grace period for late arrivals

# ========================================
# SHARDING CONFIGURATION (Layer 4)
# ========================================
SHARDING_ENABLED=false
SHARD_COUNT=5  # price, liquidity, supply, volatility, sentiment

# ========================================
# OUTPUT CONFIGURATION
# ========================================
OUTPUT_DIR=data/output
PROVISIONAL_OUTPUT=data/output/provisional/provisional_stream.jsonl
ALERT_OUTPUT=data/output/alerts/alert_stream.jsonl
FINALIZED_OUTPUT=data/output/finalized/canonical_stream.jsonl
UNIFIED_OUTPUT=data/output/unified_stream.jsonl

# ========================================
# LOGGING & MONITORING
# ========================================
LOG_LEVEL=INFO
LOG_FORMAT=json
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=9090

Progressive Layer Implementation Strategy
Critical Rule: Perfect Before Expand
Each layer must work flawlessly before moving to the next. No exceptions.

Layer-by-Layer Implementation
🟢 Layer 1: Perfected Single-Coin Core (Weeks 1-2)
Scope: USDC on Ethereum ONLY
Components:
    1. Single-coin schema with basic TCS
    2. Historical replay mode (CSV with USDC Ethereum data)
    3. Live mode: CoinGecko (price), DeFiLlama (liquidity)
    4. Web3 events for USDC Ethereum contract
    5. Full normalization + quality layers
    6. Finality tracking for Ethereum (tier1/tier2/tier3)
    7. Basic TCS calculation (finality + completeness + staleness)
    8. Reorg detection and correction events
Success Criteria:
    • ✅ 30-day historical replay works perfectly
    • ✅ Live mode tracks USDC Ethereum with finality tiers
    • ✅ TCS accurately reflects event confidence
    • ✅ Reorgs detected and corrected automatically
    • ✅ Output format stable and validated
Deliverable: Bulletproof foundation for one coin on one chain.

🟡 Layer 2: Multi-Coin Parallel Monitoring (Week 3)
Scope: Expand to USDC, USDT, DAI, BUSD on Ethereum
New Components:
    1. Multi-coin configuration (coin loop)
    2. Isolated coin contexts (no shared state)
    3. Per-coin TCS tracking
    4. Coin-level partitioning in Pathway
Changes:
    • Schema: Add per-coin TCS breakdown
    • Config: COINS = [USDC, USDT, DAI, BUSD]
    • Pipeline: Instantiate separate ingestion context per coin
    • Output: Partitioned by coin
Success Criteria:
    • ✅ All 4 coins ingest simultaneously
    • ✅ No cross-contamination between coin contexts
    • ✅ TCS computed independently per coin
    • ✅ Aggregated dashboard shows all 4 coins
Deliverable: Ecosystem-level monitoring on single chain.

🟠 Layer 3: Cross-Chain Synchronization (Weeks 4-5)
Scope: Add Arbitrum (+ optionally Solana)
New Components:
    1. Chain-specific finality trackers:
        ◦ ethereum.py: 12/64 confirmation thresholds
        ◦ arbitrum.py: L1 batch posting tracking
        ◦ solana.py: Commitment level monitoring (optional)
    2. Cross-chain aggregation logic
    3. Chain-specific grace periods
    4. Enhanced TCS with cross-chain confidence (min of chains)
    5. Window state machine (OPEN → PROVISIONAL → FINAL)
Schema Changes:
    • Add chain field
    • Add cross_chain_confidence to TCS breakdown
    • Add window_state field
Critical Implementation:
    • Heterogeneous finality handling: Each chain has different confirmation semantics
    • Temporal alignment: Events from different chains must align to same time buckets
    • Reorg divergence: Ethereum reorgs while Arbitrum doesn't → confidence impacts
Success Criteria:
    • ✅ USDC tracked on both Ethereum AND Arbitrum
    • ✅ Cross-chain total supply = sum(Ethereum supply, Arbitrum supply)
    • ✅ TCS reflects weakest chain's finality (min)
    • ✅ Window state transitions correctly (PROVISIONAL → FINAL when all chains finalized)
    • ✅ Arbitrum L1 batch posting correctly tracked
Deliverable: Multi-chain synchronized monitoring with heterogeneous finality.

🔴 Layer 4: Sharded Scaling Simulation (Week 6)
Scope: Logical feature-based sharding
New Components:
    1. Feature shards:
        ◦ Price shard (handles all price events)
        ◦ Liquidity shard (handles all liquidity events)
        ◦ Supply shard (handles all supply events)
        ◦ Volatility shard (handles volatility calc)
        ◦ Sentiment shard (handles sentiment)
    2. Shard coordinator: Aggregates shard outputs
    3. Shard router: Routes events to correct shard
Architecture:
Event → Router → [Price Shard | Liq Shard | Supply Shard | ...] → Coordinator → Unified Stream
Key Point: This runs locally but is structured like a distributed system. Each shard is a separate Pathway computation graph that could theoretically run on different nodes.
Success Criteria:
    • ✅ Events correctly routed to shards by feature type
    • ✅ Shards process independently
    • ✅ Coordinator correctly aggregates shard outputs
    • ✅ Output identical to non-sharded mode (correctness test)
    • ✅ Code structure allows easy migration to actual distributed deployment
Deliverable: Horizontally scalable architecture demonstrated locally.

Implementation Sequence (Progressive Phases)
Phase 1: Foundation - Layer 1 Core (Weeks 1-2)
Sub-Phase 1.1: Setup & Schema
    1. Create full directory structure (all 4 layers, initially empty)
    2. Implement config.py with chain-aware configuration
    3. Implement schema.py with full TCS-enabled schema
    4. Set up requirements.txt with multi-chain dependencies
    5. Implement .env.example with per-chain RPC endpoints
Sub-Phase 1.2: Historical Replay (Single Coin, Single Chain)
    1. Implement historical/csv_reader.py (load Ethereum USDC CSVs)
    2. Implement historical/time_scaler.py (virtual clock)
    3. Implement historical/replay_controller.py (pause/resume/jump)
    4. Implement historical/replay_engine.py (async generator)
    5. Generate sample data: 30-day USDC Ethereum dataset
    6. Test: Replay works with correct chronological order
Sub-Phase 1.3: Data Quality + Normalization
    1. Implement normalization/timestamp_normalizer.py
    2. Implement normalization/schema_enforcer.py
    3. Implement normalization/type_coercer.py
    4. Implement normalization/chain_tagger.py (extract Ethereum metadata)
    5. Implement quality/deduplicator.py (add chain to dedup key)
    6. Implement quality/outlier_clipper.py
    7. Implement quality/missing_detector.py
    8. Test: Quality layers filter bad data
Sub-Phase 1.4: Finality Tracking (Ethereum Only)
    1. Implement multi_chain/ethereum.py (finality rules)
    2. Implement multi_chain/finality_tracker.py (confirmation counter)
    3. Implement multi_chain/reorg_detector.py (block hash monitoring)
    4. Implement quality/reorg_handler.py (emit correction events)
    5. Test: Simulated reorg triggers correction event
Sub-Phase 1.5: Basic TCS (Single Chain)
    1. Implement tcs/finality_weights.py (tier1/tier2/tier3 mapping)
    2. Implement tcs/completeness_tracker.py (expected sources)
    3. Implement tcs/staleness_calculator.py (age penalty)
    4. Implement tcs/tcs_calculator.py (basic formula, no cross-chain yet)
    5. Test: TCS correctly reflects finality tier and completeness
Sub-Phase 1.6: Live Connectors (USDC Ethereum)
    1. Implement live/base_connector.py
    2. Implement live/backpressure.py
    3. Implement live/coingecko.py (USDC only)
    4. Implement live/defillama.py (USDC Ethereum only)
    5. Implement live/web3_events.py (USDC Ethereum contract)
    6. Implement live/volatility.py (BTC)
    7. Implement multi_chain/rpc_manager.py (Ethereum RPC pool)
    8. Test: Each connector fetches USDC Ethereum data
Sub-Phase 1.7: Pathway Integration (Single Coin, Single Chain)
    1. Implement pathway/time_aligner.py
    2. Implement pathway/transformers.py (apply normalization + TCS)
    3. Implement pathway/joiners.py (time windows)
    4. Implement pathway/stream_builder.py (single-chain mode)
    5. Implement pathway/output_handlers.py (confidence-gated)
    6. Test: End-to-end USDC Ethereum pipeline
Sub-Phase 1.8: Layer 1 Validation
    1. Implement pipeline.py (Layer 1 mode only)
    2. Implement scripts/run_pipeline.py
    3. Test historical replay: 30 days, 10x speed
    4. Test live mode: USDC Ethereum real-time
    5. Verify TCS accuracy
    6. Verify reorg handling
Milestone: ✅ Layer 1 Complete - Bulletproof Single-Coin Foundation

Phase 2: Multi-Coin Expansion - Layer 2 (Week 3)
Sub-Phase 2.1: Multi-Coin Configuration
    1. Update config.py: Add COINS = [USDC, USDT, DAI, BUSD]
    2. Update schema.py: Add per-coin TCS breakdown
    3. Update pipeline.py: Coin-level parallelization
Sub-Phase 2.2: Multi-Coin Data Generation
    1. Update scripts/generate_sample_data.py (all 4 coins)
    2. Generate 30-day CSV datasets for USDT, DAI, BUSD
    3. Implement coin-specific contract addresses in live/web3_events.py
Sub-Phase 2.3: Isolated Coin Contexts
    1. Update live/coingecko.py (batch fetch all 4 coins)
    2. Update live/defillama.py (all 4 coins)
    3. Update live/web3_events.py (listen to all 4 contracts)
    4. Implement coin partitioning in pathway/stream_builder.py
Sub-Phase 2.4: Layer 2 Validation
    1. Test historical: All 4 coins replay correctly
    2. Test live: All 4 coins stream simultaneously
    3. Verify no cross-contamination
    4. Verify per-coin TCS
Milestone: ✅ Layer 2 Complete - Multi-Coin Ecosystem Monitoring

Phase 3: Cross-Chain Sync - Layer 3 (Weeks 4-5)
Sub-Phase 3.1: Arbitrum Integration
    1. Implement multi_chain/arbitrum.py (L1 batch tracking)
    2. Update multi_chain/finality_tracker.py (Arbitrum logic)
    3. Update multi_chain/rpc_manager.py (Arbitrum RPC)
    4. Update config.py: Add CHAINS = [ethereum, arbitrum]
Sub-Phase 3.2: Cross-Chain Data
    1. Generate Arbitrum historical CSVs (USDC, USDT)
    2. Update live/web3_events.py (Arbitrum contracts)
    3. Update live/defillama.py (Arbitrum liquidity)
Sub-Phase 3.3: Cross-Chain Aggregation
    1. Implement aggregation/cross_chain_aggregator.py
    2. Implement aggregation/window_state_machine.py
    3. Implement aggregation/confidence_gater.py
    4. Update tcs/tcs_calculator.py (add cross-chain confidence)
Sub-Phase 3.4: Layer 3 Validation
    1. Test USDC on Ethereum + Arbitrum
    2. Verify cross-chain total supply = sum(ETH, ARB)
    3. Verify TCS reflects weakest chain (min)
    4. Verify window state transitions
    5. Test heterogeneous finality handling
Milestone: ✅ Layer 3 Complete - Multi-Chain Synchronized

Phase 4: Sharded Scaling - Layer 4 (Week 6)
Sub-Phase 4.1: Shard Infrastructure
    1. Implement sharding/feature_shards.py
    2. Implement sharding/shard_router.py
    3. Implement sharding/shard_coordinator.py
Sub-Phase 4.2: Shard Logic
    1. Create price shard graph
    2. Create liquidity shard graph
    3. Create supply shard graph
    4. Update pipeline.py (Layer 4 mode)
Sub-Phase 4.3: Layer 4 Validation
    1. Test event routing to correct shards
    2. Verify shard independence
    3. Verify coordinator aggregation
    4. Compare sharded vs non-sharded output (must match)
Milestone: ✅ Layer 4 Complete - Horizontally Scalable Architecture

Phase 5: TCS Enhancements (Week 7)
Sub-Phase 5.1: Advanced TCS Features
    1. Implement tcs/reorg_history.py (Bayesian priors)
    2. Implement confidence decay functions
    3. Implement alert upgrade logic (provisional → probable → confirmed)
Sub-Phase 5.2: Meta-Confidence Dashboard
    1. Update output format with full confidence breakdown
    2. Implement confidence-gated attestation rules
    3. Test alert progression over time
Milestone: ✅ Full TCS Implementation Complete

Phase 6: Integration & Polish (Week 8)
    1. Full end-to-end testing (all 4 layers)
    2. Performance optimization
    3. Documentation
    4. Demo preparation
    5. Presentation materials

Verification & Testing
End-to-End Test: Historical Mode
# 1. Generate sample data
python data/scripts/generate_sample_data.py

# 2. Run historical replay at 10x speed
cd /home/tba/projects/web3
MODE=historical REPLAY_SPEED=10 python data/scripts/run_pipeline.py

# 3. Verify output
cat data/output/unified_stream.jsonl | head -20

# Expected output format:
# {"timestamp": "2024-01-15T00:00:00Z", "coin": "USDT", "price": 1.0001, ...}
# {"timestamp": "2024-01-15T00:01:00Z", "coin": "USDT", "price": 0.9999, ...}
Success Criteria:
    • Output contains all 4 coins
    • Timestamps are monotonically increasing
    • All fields populated (with forward-fill for sparse data)
    • 30 days of data replays in ~7 hours at 10x speed

End-to-End Test: Live Mode
# 1. Set up environment with API keys
cp data/.env.example data/.env
# Edit .env with INFURA_PROJECT_ID

# 2. Test connectors individually
python data/scripts/test_connectors.py

# 3. Run live pipeline
MODE=live python data/scripts/run_pipeline.py

# 4. Watch live output
tail -f data/output/unified_stream.jsonl
Success Criteria:
    • New data points appear every 60 seconds (CoinGecko interval)
    • Console shows "Healthy" status for all connectors
    • No API rate limit errors
    • Data quality: price near $1.00, volume > 0

Validation Checks
Data Quality:
# In pathway/transformers.py
def validate_data_point(row):
    assert 0.90 <= row.price <= 1.10, "Price out of range"
    assert row.volume >= 0, "Volume cannot be negative"
    assert row.coin in STABLECOINS, "Unknown coin"
    return row
Performance:
    • Historical: 10x replay should complete 1 day in ~2.4 hours
    • Live: Latency from API fetch to output < 5 seconds
    • Memory: Stable over 24+ hour run

Key Design Decisions
    1. Self-Contained in /data: No backend API framework. Pure streaming pipeline.
    2. Pathway for Streaming: Handles time-windowed joins, late arrivals, and backpressure automatically.
    3. Dual-Mode Architecture: Same output schema whether replaying history or streaming live.
    4. CSV-Based Historical: Simple, portable, easy to generate test datasets.
    5. Async Connectors: Non-blocking I/O for concurrent API polling.
    6. Forward-Fill Strategy: Sparse data (liquidity, supply) gets propagated forward in time windows.
    7. Environment-Driven Config: No hardcoded values. Production-ready from day one.

Future Extensions
Once core pipeline is working:
    1. Add more data sources: Chainlink oracles, on-chain reserves, social sentiment
    2. Risk scoring layer: Consume unified stream, output risk scores
    3. Smart contract logging: Write critical events to blockchain
    4. API wrapper: Simple FastAPI layer to serve data to frontend
    5. ML features: Real-time feature engineering in Pathway transformers
But these are NOT part of this initial implementation.

Critical Files Summary (All 4 Layers)
Layer 1: Core Foundation
File	Purpose	Layer	Complexity
config.py	Multi-chain configuration management	1	⭐⭐
ingestion/schema.py	Multi-chain schema with TCS fields	1	⭐⭐⭐
ingestion/pipeline.py	4-layer orchestrator	1-4	⭐⭐⭐⭐
ingestion/historical/replay_engine.py	CSV replay with time scaling	1	⭐⭐⭐
ingestion/historical/replay_controller.py	Pause/resume/jump controls	1	⭐⭐
ingestion/live/base_connector.py	Abstract async connector	1	⭐⭐
ingestion/live/backpressure.py	Retry logic with exponential backoff	1	⭐⭐
ingestion/live/coingecko.py	Price/volume connector (multi-coin)	1-2	⭐⭐
ingestion/live/web3_events.py	Multi-chain mint/burn events	1-3	⭐⭐⭐⭐
ingestion/normalization/chain_tagger.py	Extract chain metadata	1	⭐⭐
ingestion/quality/deduplicator.py	Dedup with chain awareness	1	⭐⭐
ingestion/quality/reorg_handler.py	Emit correction events	1	⭐⭐⭐

Layer 2: Multi-Coin
File	Purpose	Layer	Complexity
No new files	Coin parallelization uses existing modules	2	⭐

Layer 3: Multi-Chain & TCS
File	Purpose	Layer	Complexity
ingestion/multi_chain/ethereum.py	Ethereum finality rules (12/64 confirmations)	3	⭐⭐
ingestion/multi_chain/arbitrum.py	Arbitrum L1 batch tracking	3	⭐⭐⭐⭐
ingestion/multi_chain/solana.py	Solana commitment levels	3	⭐⭐⭐
ingestion/multi_chain/finality_tracker.py	Track confirmations per chain	3	⭐⭐⭐⭐
ingestion/multi_chain/reorg_detector.py	Monitor block hash changes	3	⭐⭐⭐⭐
ingestion/multi_chain/rpc_manager.py	Multi-chain RPC connection pool	3	⭐⭐⭐
ingestion/tcs/tcs_calculator.py	Main TCS computation logic	3	⭐⭐⭐⭐⭐
ingestion/tcs/finality_weights.py	Per-tier confidence mapping	3	⭐⭐
ingestion/tcs/completeness_tracker.py	Expected vs present sources	3	⭐⭐
ingestion/tcs/staleness_calculator.py	Age-based confidence penalty	3	⭐⭐
ingestion/tcs/reorg_history.py	Bayesian prior from reorg rate	3	⭐⭐⭐⭐
ingestion/aggregation/cross_chain_aggregator.py	Per-coin cross-chain aggregation	3	⭐⭐⭐⭐⭐
ingestion/aggregation/window_state_machine.py	OPEN → PROVISIONAL → FINAL	3	⭐⭐⭐⭐
ingestion/aggregation/confidence_gater.py	TCS-based state transitions	3	⭐⭐⭐

Layer 4: Sharding
File	Purpose	Layer	Complexity
ingestion/sharding/feature_shards.py	Price/Liquidity/Supply shards	4	⭐⭐⭐⭐
ingestion/sharding/shard_router.py	Route events to correct shard	4	⭐⭐⭐
ingestion/sharding/shard_coordinator.py	Aggregate shard outputs	4	⭐⭐⭐⭐

Pathway & Output
File	Purpose	Layer	Complexity
ingestion/pathway/stream_builder.py	Multi-chain Pathway graphs	1-4	⭐⭐⭐⭐⭐
ingestion/pathway/joiners.py	Time-windowed joins with TCS	1-3	⭐⭐⭐⭐
ingestion/pathway/transformers.py	Apply normalization + TCS	1-3	⭐⭐⭐
ingestion/pathway/output_handlers.py	Confidence-gated persistence	3	⭐⭐⭐⭐

Scripts
File	Purpose	Layer	Complexity
scripts/generate_sample_data.py	Multi-chain CSV generator	1-3	⭐⭐⭐
scripts/run_pipeline.py	Layer-aware entry point	1-4	⭐⭐
scripts/test_finality_tracking.py	Test confirmation monitoring	3	⭐⭐⭐
scripts/test_tcs_calculator.py	Test TCS computation	3	⭐⭐⭐

Legend: ⭐ = Low complexity, ⭐⭐⭐⭐⭐ = Highest complexity (critical architectural component)

Non-Functional Requirements Met
✅ Async-compatible: All I/O is async (aiohttp, asyncio) ✅ Environment-driven: All config from .env ✅ No hardcoded secrets: API keys from environment ✅ Clean separation: Historical vs Live vs Normalization vs Quality vs Pathway layers ✅ Easy to extend: Add new connector = implement BaseConnector ✅ Production-oriented: Logging, error handling, validation ✅ Modular structure: Clear directory organization ✅ Schema enforcement: Strict validation prevents bad data from entering pipeline ✅ Time normalization: All timestamps converted to UTC datetime ✅ Deduplication: Duplicate events removed by (timestamp, source, coin) key ✅ Outlier protection: Price and sentiment clipping prevent garbage data ✅ Backpressure handling: Exponential backoff on API failures ✅ Replay control: Pause/resume/jump-to-date for demos and testing ✅ Sentiment analysis: MVP synthetic sentiment, extensible to real APIs

🚨 Architectural Risks & Mitigations
Risk #1: Cross-Chain Temporal Ordering with Heterogeneous Finality ⚠️⚠️⚠️⚠️⚠️
THE BIG ONE - This is the single biggest technical risk in the architecture.
Problem:
    • Ethereum: 12-15 min finality
    • Arbitrum: ~13 sec soft finality, depends on L1 batch posting
    • Solana: 400ms probabilistic finality
    • You're trying to join events in 5-minute windows across these chains
Failure Scenario:
12:00:00  Solana: USDC mint +100M (instant, tier1)
12:00:05  Arbitrum: USDC transfer -50M (soft, tier1)
12:00:10  Ethereum: USDC burn -30M (tier1, unconfirmed)
12:05:00  [Window closes] → Output: total_supply_change = +20M, TCS = 0.3

12:10:00  Ethereum REORGS (canonical chain switched)
          → Burn event invalidated
          → Actual supply change: +50M
          → Your previous output was WRONG
          → If you logged it to blockchain: permanent incorrect attestation
Mitigation:
    1. ✅ Three-tier finality system (tier1/tier2/tier3 with different confidence levels)
    2. ✅ Window state machine (OPEN → PROVISIONAL → FINAL)
    3. ✅ Confidence-gated attestation (only log tier2+ to blockchain)
    4. ✅ Reorg-aware event versioning (emit correction events)
    5. ✅ TCS meta-confidence (quantify uncertainty explicitly)
    6. ✅ Chain-specific grace periods (Ethereum: 15min, Arbitrum: 2min, Solana: 30s)
Result: System is fast for monitoring but safe for immutable commitments.

Risk #2: Arbitrum L1 Batch Posting Complexity ⚠️⚠️⚠️⚠️
Problem: Arbitrum finality depends on:
    1. L2 sequencer soft confirmation (instant)
    2. L2 block finalization (seconds)
    3. L1 batch submission (minutes)
    4. L1 batch finalization (15+ minutes)
Mitigation:
    • Track L1 batch posting via Arbitrum Sequencer Inbox contract
    • tier2 = batch posted to L1 (regardless of L1 finality)
    • tier3 = L1 batch finalized (64+ confirmations on Ethereum)
Implementation: multi_chain/arbitrum.py monitors both L2 and L1 state.

Risk #3: Pathway Temporal Window Assumptions ⚠️⚠️⚠️
Problem: Pathway assumes events are append-only after window closes. Reorgs violate this.
Mitigation:
    • Don't close windows immediately
    • Use grace periods (ETHEREUM_GRACE = 15 min)
    • Keep windows in PROVISIONAL state until all events tier2+
    • Use Pathway's dynamic table updates for corrections
Implementation: aggregation/window_state_machine.py manages window lifecycle.

Risk #4: RPC Rate Limiting & Reliability ⚠️⚠️⚠️
Problem: Free RPCs throttle, paid RPCs go down, confirmations require frequent polling.
Mitigation:
    • Connection pooling with fallback RPCs
    • Exponential backoff on failures
    • Response caching (immutable block data)
    • WebSocket connections for event subscriptions (reduces polling)
Implementation: multi_chain/rpc_manager.py with tenacity retry decorator.

Risk #5: Scope Creep / Implementation Paralysis ⚠️⚠️⚠️⚠️⚠️
Problem: This is a MASSIVE scope. All 4 layers + full TCS is 6-8 weeks of work.
Mitigation:
    • STRICT layer-by-layer progression
    • Layer 1 MUST work before Layer 2
    • No shortcuts, no "we'll fix it later"
    • If stuck, drop back to simpler layer
Critical: Better to have Layer 1 perfect than Layer 4 broken.

Risk #6: Solana Commitment Semantics ⚠️⚠️⚠️
Problem: Solana's "finalized" is probabilistic, reorgs are possible even after finalization.
Mitigation:
    • Add SOLANA_SKIP_SLOT_THRESHOLD (if too many skipped slots, lower confidence)
    • Monitor cluster health metrics
    • Optionally: Skip Solana for Layer 3 MVP, add later
Decision Point: Ethereum + Arbitrum is already enough to demonstrate multi-chain. Solana is optional.

Risk #7: TCS Calculation Complexity ⚠️⚠️⭐
Problem: TCS formula is complex, many edge cases, easy to get wrong.
Mitigation:
    • Extensive unit tests (scripts/test_tcs_calculator.py)
    • Known test cases with expected TCS values
    • Gradual rollout: start with simple finality-only TCS, add components incrementally
Implementation: Start with TCS = finality_weight, then add completeness, then staleness, etc.

Risk #8: Sharding Coordination Overhead ⚠️⚠️
Problem: Sharding adds complexity without immediate benefit (running locally anyway).
Mitigation:
    • Layer 4 is optional for MVP
    • Implement only if Layers 1-3 are done early
    • Focus on architectural clarity (code could run distributed) not actual distribution
Strategic: Layer 4 is for "wow factor" in pitch, not functional necessity.

🎯 Strategic Presentation Approach
When presenting to judges/investors:
The Hook (30 seconds)
"Stablecoins are $150B of systemic risk running on blind trust. When Terra/UST collapsed, there was no real-time risk monitoring. We built an institutional-grade, multi-chain risk intelligence platform that not only detects threats but quantifies its own confidence in those assessments."
The Architecture Flex (1 minute)
"Our ingestion layer is architected as a four-layer progressive platform:
Layer 1: Bulletproof single-coin foundation with full data quality pipeline Layer 2: Multi-coin ecosystem monitoring (USDC, USDT, DAI, BUSD) Layer 3: Cross-chain synchronization with heterogeneous finality handling Layer 4: Horizontally scalable sharding architecture
Most critically, we solve the hardest problem in multi-chain monitoring: temporal consistency across heterogeneous consensus systems."
The Innovation (1 minute)
"We introduce the Temporal Confidence Score (TCS) - a meta-awareness layer that quantifies the system's confidence in its own risk assessments. TCS accounts for:
    • Chain-specific finality tiers (Ethereum takes 12 minutes, Arbitrum seconds)
    • Data source completeness
    • Temporal staleness
    • Historical reorg rates
This transforms risk alerts from binary warnings to confidence intervals, preventing false alarms during chain instability."
The Production Readiness (30 seconds)
"This isn't a hackathon demo. It's production-grade distributed systems engineering:
    • Reorg-aware event versioning
    • Confidence-gated immutable attestations
    • Window state machines (provisional → finalized)
    • Three-tier finality tracking
    • Exponential backoff with fallback RPCs
We built it to scale."
The Demo (2 minutes)
    1. Show Layer 1: USDC Ethereum real-time monitoring with TCS
    2. Show Layer 3: Cross-chain aggregation (Ethereum + Arbitrum)
    3. Simulate reorg: Show correction event + TCS drop
    4. Show window state transition: PROVISIONAL → FINAL
The Vision (30 seconds)
"This is the data backbone for institutional stablecoin risk management. Banks, regulators, and DeFi protocols need real-time multi-chain intelligence with quantified confidence. We built the infrastructure to deliver it."

✅ Success Criteria
Layer 1 Success:
    • ✅ 30-day USDC Ethereum replay at 10x speed completes
    • ✅ Live mode tracks real USDC with correct finality tiers
    • ✅ Simulated reorg triggers correction event within 5 seconds
    • ✅ TCS accurately reflects confidence (tier1=0.3, tier2=0.8, tier3=1.0)
Layer 2 Success:
    • ✅ All 4 coins stream simultaneously without cross-contamination
    • ✅ Per-coin TCS tracked independently
Layer 3 Success:
    • ✅ USDC on Ethereum + Arbitrum aggregates correctly
    • ✅ Cross-chain total supply = sum(ETH, ARB)
    • ✅ Window transitions PROVISIONAL → FINAL when both chains finalized
    • ✅ TCS reflects cross-chain confidence (min of chains)
Layer 4 Success:
    • ✅ Events route to correct feature shard
    • ✅ Sharded output == non-sharded output (correctness test)
    • ✅ Architecture allows distributed deployment
Full System Success:
    • ✅ Judges understand temporal confidence innovation
    • ✅ Demo shows reorg handling and confidence evolution
    • ✅ Code review reveals institutional-grade engineering
    • ✅ Presentation conveys production readiness

📊 Estimated Implementation Timeline
Aggressive (6 weeks):
    • Week 1-2: Layer 1 (foundation)
    • Week 3: Layer 2 (multi-coin)
    • Week 4-5: Layer 3 (multi-chain + full TCS)
    • Week 6: Layer 4 (sharding) + polish
Realistic (8 weeks):
    • Week 1-2: Layer 1
    • Week 3: Layer 2
    • Week 4-6: Layer 3 (multi-chain finality is complex)
    • Week 7: TCS enhancements
    • Week 8: Layer 4 + demo prep
Safe (10 weeks):
    • Add 2 weeks buffer for inevitable complexity
Fallback Plan:
    • If time constrained: Ship Layers 1-3 only
    • Layer 3 alone demonstrates institutional thinking
    • Layer 4 is "future work" slide

🏁 Final Architectural Principle
"Perfect Before Expand"
Do NOT move to the next layer until the current layer works flawlessly. A bulletproof Layer 1 is infinitely more valuable than a broken Layer 4.

End of plan.
