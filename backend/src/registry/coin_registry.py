"""
Coin Registry for managing multiple stablecoins.

Provides centralized configuration and metadata for all monitored coins.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

from src.common.config import config, CoinConfig

logger = logging.getLogger(__name__)


@dataclass
class CoinStatus:
    """Runtime status for a monitored coin."""
    coin: str
    is_active: bool = True
    last_update: Optional[datetime] = None
    health_score: float = 1.0  # 0.0 (critical) to 1.0 (healthy)

    # Risk flags
    is_depegged: bool = False
    depeg_severity: float = 0.0
    has_liquidity_crisis: bool = False
    has_supply_anomaly: bool = False

    # Data availability
    sources_available: Set[str] = field(default_factory=set)
    chains_available: Set[str] = field(default_factory=set)

    # Metrics
    current_price: Optional[float] = None
    total_liquidity: Optional[float] = None
    daily_volume: Optional[float] = None
    market_volatility: Optional[float] = None
    sentiment_score: Optional[float] = None
    temporal_confidence: float = 0.0


class CoinRegistry:
    """
    Registry for managing multiple stablecoins.

    Provides:
    - Coin configuration and metadata
    - Runtime status tracking
    - Risk thresholds
    - Cross-coin operations
    """

    def __init__(self):
        # Load coin configurations from config
        self.coins: Dict[str, CoinConfig] = config.COINS.copy()

        # Runtime status for each coin
        self.coin_status: Dict[str, CoinStatus] = {}

        # Initialize status for all configured coins
        for coin_symbol in self.coins.keys():
            self.coin_status[coin_symbol] = CoinStatus(coin=coin_symbol)

        logger.info(f"Initialized coin registry with {len(self.coins)} stablecoins")

    def get_coin_config(self, coin: str) -> Optional[CoinConfig]:
        """Get configuration for a coin."""
        return self.coins.get(coin)

    def get_coin_status(self, coin: str) -> Optional[CoinStatus]:
        """Get runtime status for a coin."""
        return self.coin_status.get(coin)

    def update_coin_status(self, coin: str, **kwargs):
        """Update runtime status for a coin."""
        if coin not in self.coin_status:
            logger.warning(f"Unknown coin: {coin}")
            return

        status = self.coin_status[coin]

        # Update provided fields
        for key, value in kwargs.items():
            if hasattr(status, key):
                setattr(status, key, value)

        # Update last_update timestamp
        status.last_update = datetime.utcnow()

        # Recalculate health score
        status.health_score = self._calculate_health_score(status)

    def _calculate_health_score(self, status: CoinStatus) -> float:
        """
        Calculate overall health score for a coin.

        Factors:
        - Price stability (not depegged)
        - Liquidity availability
        - Data freshness
        - TCS confidence
        """
        score = 1.0

        # Price stability (most critical)
        if status.is_depegged:
            if status.depeg_severity > 0.05:  # >5% depeg
                score *= 0.0  # Critical
            elif status.depeg_severity > 0.02:  # >2% depeg
                score *= 0.3  # Severe
            else:
                score *= 0.7  # Moderate

        # Liquidity health
        if status.has_liquidity_crisis:
            score *= 0.5

        # Supply anomalies
        if status.has_supply_anomaly:
            score *= 0.8

        # Data availability (TCS)
        score *= status.temporal_confidence

        # Sentiment (mild factor)
        if status.sentiment_score is not None:
            if status.sentiment_score < -0.5:  # Very negative
                score *= 0.9

        return max(0.0, min(1.0, score))

    def get_all_coins(self) -> List[str]:
        """Get list of all monitored coins."""
        return list(self.coins.keys())

    def get_active_coins(self) -> List[str]:
        """Get list of actively monitored coins."""
        return [
            coin for coin, status in self.coin_status.items()
            if status.is_active
        ]

    def get_depegged_coins(self) -> List[str]:
        """Get list of currently depegged coins."""
        return [
            coin for coin, status in self.coin_status.items()
            if status.is_depegged
        ]

    def get_healthy_coins(self, threshold: float = 0.8) -> List[str]:
        """Get list of healthy coins (health_score >= threshold)."""
        return [
            coin for coin, status in self.coin_status.items()
            if status.health_score >= threshold
        ]

    def get_at_risk_coins(self, threshold: float = 0.5) -> List[str]:
        """Get list of at-risk coins (health_score < threshold)."""
        return [
            coin for coin, status in self.coin_status.items()
            if status.health_score < threshold
        ]

    def get_coins_by_chain(self, chain: str) -> List[str]:
        """Get list of coins available on a specific chain."""
        return [
            coin for coin, config in self.coins.items()
            if chain in config.chains
        ]

    def get_chains_for_coin(self, coin: str) -> List[str]:
        """Get list of chains where a coin is deployed."""
        coin_config = self.get_coin_config(coin)
        return coin_config.chains if coin_config else []

    def is_coin_supported(self, coin: str, chain: str) -> bool:
        """Check if a coin is supported on a specific chain."""
        coin_config = self.get_coin_config(coin)
        return coin_config and chain in coin_config.chains

    def get_contract_address(self, coin: str, chain: str) -> Optional[str]:
        """Get contract address for a coin on a specific chain."""
        coin_config = self.get_coin_config(coin)
        if not coin_config:
            return None
        return coin_config.contract_addresses.get(chain)

    def register_coin(
        self,
        symbol: str,
        name: str,
        chains: List[str],
        contract_addresses: Dict[str, str],
        decimals: int = 6,
        **kwargs
    ):
        """
        Register a new coin in the registry.

        Useful for dynamically adding coins not in config.
        """
        coin_config = CoinConfig(
            symbol=symbol,
            name=name,
            chains=chains,
            contract_addresses=contract_addresses,
            decimals=decimals,
            **kwargs
        )

        self.coins[symbol] = coin_config
        self.coin_status[symbol] = CoinStatus(coin=symbol)

        logger.info(f"Registered new coin: {symbol} ({name}) on {len(chains)} chains")

    def deactivate_coin(self, coin: str):
        """Deactivate monitoring for a coin."""
        if coin in self.coin_status:
            self.coin_status[coin].is_active = False
            logger.info(f"Deactivated coin: {coin}")

    def activate_coin(self, coin: str):
        """Activate monitoring for a coin."""
        if coin in self.coin_status:
            self.coin_status[coin].is_active = True
            logger.info(f"Activated coin: {coin}")

    def get_registry_summary(self) -> Dict:
        """Get summary statistics for the registry."""
        active_coins = self.get_active_coins()
        depegged_coins = self.get_depegged_coins()
        at_risk_coins = self.get_at_risk_coins()

        # Average health score
        health_scores = [s.health_score for s in self.coin_status.values()]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.0

        # Average TCS
        tcs_scores = [s.temporal_confidence for s in self.coin_status.values()]
        avg_tcs = sum(tcs_scores) / len(tcs_scores) if tcs_scores else 0.0

        return {
            "total_coins": len(self.coins),
            "active_coins": len(active_coins),
            "depegged_coins": len(depegged_coins),
            "at_risk_coins": len(at_risk_coins),
            "average_health_score": avg_health,
            "average_tcs": avg_tcs,
            "chains_supported": list(set(
                chain for coin in self.coins.values()
                for chain in coin.chains
            ))
        }


# Singleton registry
coin_registry = CoinRegistry()
