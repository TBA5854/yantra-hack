"""
Chain-aware configuration for multi-chain stablecoin risk platform.
Supports Ethereum, Arbitrum, and Solana with heterogeneous finality settings.
"""

from dataclasses import dataclass
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ChainConfig:
    """Configuration for a specific blockchain."""
    name: str
    rpc_url: str
    fallback_rpcs: List[str]
    block_time_ms: int

    # Finality tier thresholds (in confirmations)
    tier1_confirmations: int  # 0.3 confidence - "probable"
    tier2_confirmations: int  # 0.8 confidence - "highly likely"
    tier3_confirmations: int  # 1.0 confidence - "final"

    # Finality time estimates (seconds)
    tier1_time_sec: int
    tier2_time_sec: int
    tier3_time_sec: int

    # Reorg characteristics
    max_reorg_depth: int
    reorg_probability: float


@dataclass
class CoinConfig:
    """Configuration for a stablecoin."""
    symbol: str
    name: str
    chains: List[str]  # Which chains this coin is deployed on
    contract_addresses: Dict[str, str]  # chain -> contract address
    decimals: int

    # Risk thresholds
    depeg_threshold: float = 0.02  # 2% depeg triggers alert
    liquidity_min: float = 1_000_000  # Min $1M liquidity
    volatility_max: float = 0.05  # Max 5% daily volatility


class Config:
    """Global configuration singleton."""

    # ============================================
    # CHAIN CONFIGURATIONS
    # ============================================

    CHAINS: Dict[str, ChainConfig] = {
        "ethereum": ChainConfig(
            name="ethereum",
            rpc_url=os.getenv("ETHEREUM_RPC_URL", "https://eth.llamarpc.com"),
            fallback_rpcs=[
                "https://rpc.ankr.com/eth",
                "https://eth.rpc.blxrbdn.com"
            ],
            block_time_ms=12_000,
            tier1_confirmations=1,   # ~12 seconds
            tier2_confirmations=32,  # ~6.4 minutes (safety margin before finality)
            tier3_confirmations=64,  # ~12.8 minutes (finalized)
            tier1_time_sec=12,
            tier2_time_sec=384,
            tier3_time_sec=768,
            max_reorg_depth=64,
            reorg_probability=0.001
        ),
        "arbitrum": ChainConfig(
            name="arbitrum",
            rpc_url=os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"),
            fallback_rpcs=[
                "https://rpc.ankr.com/arbitrum",
                "https://arbitrum.llamarpc.com"
            ],
            block_time_ms=250,
            tier1_confirmations=1,    # ~250ms (L2 confirmation)
            tier2_confirmations=50,   # ~12.5 sec (batch posted to L1)
            tier3_confirmations=256,  # ~64 sec + L1 finality (~15 min total)
            tier1_time_sec=1,
            tier2_time_sec=13,
            tier3_time_sec=900,  # 15 minutes to L1 finality
            max_reorg_depth=256,
            reorg_probability=0.002  # Higher than Ethereum due to L2 batching
        ),
        "solana": ChainConfig(
            name="solana",
            rpc_url=os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
            fallback_rpcs=[
                "https://solana-api.projectserum.com",
                "https://rpc.ankr.com/solana"
            ],
            block_time_ms=400,
            tier1_confirmations=1,    # ~400ms (1 slot)
            tier2_confirmations=32,   # ~13 seconds (optimistic confirmation)
            tier3_confirmations=300,  # ~2 minutes (rooted - 2/3 stake voted)
            tier1_time_sec=1,
            tier2_time_sec=13,
            tier3_time_sec=120,
            max_reorg_depth=300,
            reorg_probability=0.005  # Higher due to probabilistic finality
        )
    }

    # ============================================
    # COIN CONFIGURATIONS
    # ============================================

    COINS: Dict[str, CoinConfig] = {
        "USDC": CoinConfig(
            symbol="USDC",
            name="USD Coin",
            chains=["ethereum", "arbitrum", "solana"],
            contract_addresses={
                "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
                "solana": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            },
            decimals=6
        ),
        "USDT": CoinConfig(
            symbol="USDT",
            name="Tether USD",
            chains=["ethereum", "arbitrum", "solana"],
            contract_addresses={
                "ethereum": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "arbitrum": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
                "solana": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
            },
            decimals=6
        ),
        "DAI": CoinConfig(
            symbol="DAI",
            name="Dai Stablecoin",
            chains=["ethereum", "arbitrum"],
            contract_addresses={
                "ethereum": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                "arbitrum": "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1"
            },
            decimals=18
        )
    }

    # ============================================
    # DATA SOURCE CONFIGURATIONS
    # ============================================

    # Price sources
    PRICE_SOURCES = {
        "coingecko": {
            "base_url": "https://api.coingecko.com/api/v3",
            "api_key": os.getenv("COINGECKO_API_KEY"),
            "rate_limit": 50,  # requests per minute
            "timeout": 10
        },
        "chainlink": {
            "enabled": True,
            "feeds": {
                "USDC/USD": "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6",
                "USDT/USD": "0x3E7d1eAB13ad0104d2750B8863b489D65364e32D",
                "DAI/USD": "0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9"
            }
        }
    }

    # Liquidity sources (DEX data)
    LIQUIDITY_SOURCES = {
        "uniswap_v3": {
            "subgraph_url": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
            "chains": ["ethereum", "arbitrum"]
        },
        "curve": {
            "api_url": "https://api.curve.fi/api",
            "chains": ["ethereum", "arbitrum"]
        },
        "orca": {
            "api_url": "https://api.orca.so",
            "chains": ["solana"]
        }
    }

    # Supply monitoring (on-chain events)
    SUPPLY_SOURCES = {
        "ethereum": {
            "transfer_event_sig": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "mint_event_sig": "0x0f6798a560793a54c3bcfe86a93cde1e73087d944c0ea20544137d4121396885",
            "burn_event_sig": "0xcc16f5dbb4873280815c1ee09dbd06736cffcc184412cf7a71a0fdb75d397ca5"
        }
    }

    # Poll intervals (seconds)
    SOURCE_CONFIG = {
        "price_interval_sec": 60,
        "liquidity_interval_sec": 300,
        "volatility_interval_sec": 3600,
        "sentiment_interval_sec": 3600
    }

    # Sentiment sources
    SENTIMENT_SOURCES = {
        "twitter": {
            "api_key": os.getenv("TWITTER_API_KEY"),
            "keywords": ["USDC", "USDT", "DAI", "depeg", "stablecoin"]
        },
        "reddit": {
            "client_id": os.getenv("REDDIT_CLIENT_ID"),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
            "subreddits": ["CryptoCurrency", "defi", "ethereum"]
        }
    }

    # ============================================
    # TEMPORAL CONFIDENCE SCORE (TCS) CONFIG
    # ============================================

    TCS_CONFIG = {
        # Expected data sources per aggregation
        "expected_sources": ["price", "liquidity", "supply", "volatility", "sentiment"],

        # Staleness penalties
        "staleness_thresholds": {
            "fresh": 300,      # < 5 min: penalty = 1.0
            "acceptable": 600,  # < 10 min: penalty = 0.9
            "stale": float('inf')  # >= 10 min: penalty = 0.7
        },

        # Source importance weights
        "source_importance": {
            "price": 1.0,
            "liquidity": 0.8,
            "supply": 0.9,
            "volatility": 0.7,
            "sentiment": 0.5
        },

        # Minimum TCS thresholds for attestation
        "attestation_threshold": 0.8,  # Only log tier2+ events (TCS >= 0.8)

        # Grace period for cross-chain aggregation (slowest chain finality)
        "cross_chain_grace_period": 900  # 15 minutes (Ethereum finality)
    }

    # ============================================
    # WINDOW STATE MACHINE CONFIG
    # ============================================

    WINDOW_CONFIG = {
        "window_size_sec": 300,  # 5-minute windows

        # State transition timing
        "provisional_delay_sec": 60,   # OPEN -> PROVISIONAL after 1 min
        "finalization_delay_sec": 900,  # PROVISIONAL -> FINAL after 15 min (slowest chain)

        # Reorg grace period
        "reorg_grace_period_sec": 300,  # 5 min after window close to detect reorgs

        # Max events per window (backpressure threshold)
        "max_events_per_window": 10000
    }

    # ============================================
    # DATA QUALITY CONFIG
    # ============================================

    QUALITY_CONFIG = {
        # Outlier detection (z-score method)
        "outlier_z_threshold": 3.0,

        # Normalization bounds
        "price_bounds": (0.95, 1.05),  # Stablecoins should be $0.95-$1.05

        # Deduplication window
        "dedup_window_sec": 60,  # Dedupe identical events within 1 minute

        # Backpressure handling
        "max_retry_attempts": 3,
        "retry_backoff_base": 2,  # Exponential backoff: 2^n seconds
        "circuit_breaker_threshold": 10  # Open circuit after 10 consecutive failures
    }

    # ============================================
    # PATHWAY STREAMING CONFIG
    # ============================================

    PATHWAY_CONFIG = {
        "mode": "streaming",
        "persistence_backend": "filesystem",
        "persistence_path": "./data/pathway_state",

        # Time-windowed join settings
        "join_mode": "left",  # Forward-fill for sparse data
        "join_max_delay_sec": 60,

        # Output settings
        "output_format": "jsonlines",
        "output_path": "./data/output"
    }

    # ============================================
    # ATTESTATION CONFIG
    # ============================================

    ATTESTATION_CONFIG = {
        "enabled": os.getenv("ATTESTATION_ENABLED", "false").lower() == "true",
        "contract_address": os.getenv("ATTESTATION_CONTRACT_ADDRESS"),
        "private_key": os.getenv("ATTESTATION_PRIVATE_KEY"),

        # Only attest high-confidence events
        "min_tcs": 0.8,
        "min_finality_tier": "tier2",

        # Gas settings
        "gas_limit": 100000,
        "max_gas_price_gwei": 50
    }

    # ============================================
    # LOGGING & MONITORING
    # ============================================

    LOGGING_CONFIG = {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "output": "both",  # "console", "file", or "both"
        "file_path": "./logs/platform.log"
    }

    # Monitoring endpoints
    MONITORING = {
        "prometheus_port": int(os.getenv("PROMETHEUS_PORT", "9090")),
        "healthcheck_port": int(os.getenv("HEALTHCHECK_PORT", "8080"))
    }


# Singleton instance
config = Config()
